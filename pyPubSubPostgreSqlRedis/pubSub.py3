#!/usr/bin/python3
# -*- coding: utf-8 -*-
from os.path import exists
import psycopg2, psycopg2.extras
import redis
import requests
import json
from settings import *
#import pprint

data_packet_elements_processed = 0

def postgres_connection():
	try:
		conn = psycopg2.connect(
			database=PG_DB_NAME,
			user=PG_USER,
			password=PG_PASS,
			host=PG_HOST,
			port=PG_PORT
			)
		curs = conn.cursor()
	except (Exception,psycopg2.DatabaseError) as e:
		logger.error("Postgres connection is not ready yet. Error: " + str(e))
	return [conn, curs]

def redis_connection():
	try:
		pool = redis.ConnectionPool(
			host=R_HOST,
			port=R_PORT,
			db=R_DB
			)
		r = redis.Redis(connection_pool=pool)
	except Exception as e:
		logger.error("Redis connection is not ready yet. Error: " + str(e))
	return r

def api_query():

	data_packet = []

	try:
		# I will use https://developer.edamam.com/ to get data related with 
		# food and brands,as a part of extract some kind of data for this 
		# example. If you want to use this API, you'll need request your
		# private app_key
		response = requests.get(
			"https://api.edamam.com/api/food-database/parser?ingr=red%20apple&app_id="+APP_ID+"&app_key="+APP_KEY,timeout=10
			)
		if(response.ok):
			#print ("Well done!:\n",response.content)
			str_response = response.content.decode('utf-8')
			json_response = json.loads(str_response)
			#pp = pprint.PrettyPrinter(indent=4)

			# In this case, i'll store only brands and categories that are in
			# the "hints" level of the JSON
			for i,elem in enumerate(json_response['hints']):
				#pp.pprint(elem['food'])
				try:
					# Only store foods with brand
					if(elem['food']['brand']):
						# Working with big XML or JSON structure, you could also think
						# about store this temporal data_packet in a mongodb document
						data_packet.append(elem['food'])
				except Exception as e:
					logger.info("The FoodId: "+ elem['food']['foodId'] + " doesn't have a brand related, so it won't be stored")

			logger.info("Data Packet received successfully")
		else:
			logger.error("Fail in response. Status code: "+str(response.status_code)+"\n")
	
	except Exception as e:
		logger.error("Fail in api_query. Error: "+ str(e))

	return data_packet

def listen(pgcon, pgcur, channel):

	global data_packet_elements_processed
	try:
		pgcon.poll()
		notify = pgcon.notifies.pop()
		notify_args = {}
		notify_args['pid'] = notify.pid
		notify_args['channel'] = notify.channel
		notify_args['payload'] = json.loads(notify.payload)
		logger.info("NOTIFY received:" +json.dumps(notify_args))
		return notify.payload
	except Exception as e:
		logger.error("NOTIFY by the channel: " +channel+" not received. Error: " + str(e))
		data_packet_elements_processed+=1
		return None

def check_brands_categories_relationship(r,pgcon,pgcur,brand_id,category_id):

	global data_packet_elements_processed
	try:

		# If exists in redis, do not insert in postgres
		if (r.hget(
			"tbl_brands_categories_"+str(brand_id)+"_"+str(category_id),"brands_categories_id")):
			logger.info("tbl_brands_categories_"+str(brand_id)+"_"+str(category_id)+" already exists") 

			data_packet_elements_processed+=1

		# If not exists in redis...
		else:
			logger.info("tbl_brands_categories_"+str(brand_id)+"_"+str(category_id)+" doesn't exists")

			# Load in postgres
			pgcur.execute("BEGIN")
			pgcur.execute("LISTEN notify_channel_tbl_brands_categories")
			args = [brand_id,category_id]
			pgcur.callproc("core_schema.udf_brands_categories_insert",args)
			pgcur.execute("COMMIT")
			logger.info("Executed successfully udf_brands_categories_insert")
			payload = listen(pgcon,pgcur,'notify_channel_tbl_brands_categories')

			if (payload is not None):

				json_response = json.loads(payload)

				key = json_response['redisHash']
				valuesDict = {}
				valuesDict['brands_categories_id'] = str(json_response['brands_categories_id'])
				valuesDict['brand_id'] = str(json_response['brand_id'])
				valuesDict['categories_id'] = str(json_response['categories_id'])

				# Send values to Redis
				r.hmset(key,valuesDict)
				logger.info("Values sent to redis successfully: "+json.dumps(key)+","+json.dumps(valuesDict))

				data_packet_elements_processed+=1

	except Exception as e:
		logger.error("Fail in listenerBrandsCategoriesRelationship. Error: "+ str(e))

def check_categories(r,pgcon,pgcur,data_packet_elem,brand_id):

	global data_packet_elements_processed
	try:

		# If exists in redis, do not insert in postgres
		if (r.hget("tbl_categories_"+data_packet_elem['category'],"name")):
			logger.info("tbl_categories_"+data_packet_elem['category']+" already exists")
			category_id = r.hget("tbl_categories_"+data_packet_elem['category'],"category_id")

			check_brands_categories_relationship(r,pgcon,pgcur,brand_id,category_id.decode())

		# If not exists in redis...
		else:
			logger.info("Category: "+data_packet_elem['category']+" doesn't exists")

			# Load in postgres
			pgcur.execute("BEGIN")
			pgcur.execute("LISTEN notify_channel_tbl_categories")
			args = [data_packet_elem['category']]
			pgcur.callproc("core_schema.udf_categories_insert",args)
			pgcur.execute("COMMIT")
			logger.info("Executed successfully udf_categories_insert")
			payload = listen(pgcon,pgcur,'notify_channel_tbl_categories')

			if (payload is not None):

				json_response = json.loads(payload)

				# In this case, key is buld by the category name, because
				# the API doesn't supplie an ID, so to compare 
				# the category name is used, but the ideal thing is to use
				# the tablename followed by the id
				key = json_response['redisHash']
				valuesDict = {}
				valuesDict['category_id'] = str(json_response['category_id'])
				valuesDict['name'] = json_response['redisHash']

				# Send values to Redis
				r.hmset(key,valuesDict)
				logger.info("Values sent to redis successfully: "+json.dumps(key)+","+json.dumps(valuesDict))

				check_brands_categories_relationship(r,pgcon,pgcur,brand_id,valuesDict['category_id'])

	except Exception as e:
		logger.error("Fail in listenerCategories. Error: "+ str(e))

def check_brands(r,pgcon,pgcur,data_packet_elem):

	global data_packet_elements_processed

	# If the current food belongs to a brand
	try:

		# If exists in redis, do not insert in postgres
		if (r.hget("tbl_brands_"+data_packet_elem['brand'],"name")):
			logger.info("tbl_brands_"+data_packet_elem['brand']+" already exists")
			brand_id = r.hget("tbl_brands_"+data_packet_elem['brand'],"brand_id")

			# Check if the category already exists in redis 
			check_categories(r,pgcon,pgcur,data_packet_elem,brand_id.decode())

		# If not exists in redis, load in postgres
		else:
			logger.info("Brand: "+data_packet_elem['brand']+" doesn't exists")

			# Load in postgres
			pgcur.execute("BEGIN")
			pgcur.execute("LISTEN notify_channel_tbl_brands")
			args = [data_packet_elem['brand']]
			pgcur.callproc("core_schema.udf_brands_insert",args)
			pgcur.execute("COMMIT")
			logger.info("Executed successfully udf_brands_insert")
			payload = listen(pgcon,pgcur,'notify_channel_tbl_brands')

			if (payload is not None):

				json_response = json.loads(payload)

				# In this case, key is buld by the brand name, because
				# the API doesn't supplie an ID, so to compare 
				# the brand name is used, but the ideal thing is to use
				# the tablename followed by the id
				key = json_response['redisHash']
				valuesDict = {}
				valuesDict['brand_id'] = str(json_response['brand_id'])
				valuesDict['name'] = json_response['redisHash']

				# Send values to Redis
				r.hmset(key,valuesDict)
				logger.info("Values sent to redis successfully: "+key+","+json.dumps(valuesDict))

				# Check if the category already exists in redis 
				check_categories(r,pgcon,pgcur,data_packet_elem,valuesDict['brand_id'])

	# If the current food doesn't belongs to a brand
	except Exception as e:
		logger.error("Fail in listenerBrands. Error: "+ str(e))

def main():

	r = redis_connection()
	pgcon, pgcur = postgres_connection()

	data_packet_list = []
	global data_packet_elements_processed
	'''
	with open('foodChunk.json') as foodFile:
		data_packet_list = json.load(foodFile)
	'''
	data_packet_list = api_query()
	if (data_packet_list is not None):
		for i, data_packet_elem in enumerate(data_packet_list):
			check_brands(r,pgcon,pgcur,data_packet_elem)

		if (data_packet_elements_processed == len(data_packet_list)):
			print ("All the elements of the data packet were processed successfully")
		else:
			print ("Not all the elements of the data packet were processed successfully. Please check the logs")

	pgcon.close()
	pgcur.close()

if __name__ == '__main__':
    main()
