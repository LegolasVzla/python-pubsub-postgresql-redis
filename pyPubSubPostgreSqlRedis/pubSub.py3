# -*- coding: utf-8 -*-
import psycopg2, psycopg2.extras
import select
import redis
import requests
import json
from settings import *
#import pprint

def postgresConnection():
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
		print ("Postgres connection is not ready yet. Error: " + str(e))
	return [conn, curs]

def redisConnection():
	try:
		pool = redis.ConnectionPool(
			host=R_HOST,
			port=R_PORT,
			db=R_DB
			)
		r = redis.Redis(connection_pool=pool)
	except Exception as e:
		print ("Redis connection is not ready yet. Error: " + str(e))
	return r

def apiQuery():

	data_packet = []

	try:
		# I will use https://developer.edamam.com/ to get data related with 
		# food and brands,as a part of extract some kind of data for this 
		# example. If you want to use this API, you'll need request your
		# private app_key
		response = requests.get(
			"https://api.edamam.com/api/food-database/parser?ingr=red%20apple&app_id="+APP_ID+"&app_key="+APP_KEY
			)
		if(response.ok):
			#print ("Well done!:\n",response.content)
			str_response = response.content.decode('utf-8')
			json_response = json.loads(str_response)
			#pp = pprint.PrettyPrinter(indent=4)
			#pp.pprint(d['hints'][10]['food'])

			# In this case, i'll store only brands and categories that are in
			# the "hints" level of the JSON
			for i,elem in enumerate(json_response['hints']):
				#pp.pprint(elem['food'])

				# Working with big XML or JSON structure, you could also think
				# about store this temporal data_packet in a mongodb document
				data_packet.append(elem['food'])
		else:
			print ("Fail in response\n")

	except Exception as e:
		print ("Fail in apiQuery. Error: "+ str(e))

	return data_packet

def listen(pgcon, pgcur, channel):
	try:
		pgcon.poll()
		notify = pgcon.notifies.pop()
		#print ("NOTIFY received:", notify.pid, notify.channel, notify.payload)
		return notify.payload
	except Exception as e:
		print ("NOTIFY by the channel: " +channel+" not received. Error: " + str(e))
		return None

def checkBrandsCategoriesRelationship(r,pgcon,pgcur,brand_id,category_id):

	try:

		# If exists in redis, do not insert in postgres
		if (r.hget(
			"tbl_brands_categories_"+str(brand_id)+"_"+str(category_id),"brands_categories_id")):
			print ("tbl_brands_categories_"+str(brand_id)+"_"+str(category_id)+" already exists")

		# If not exists in redis...
		else:
			print ("tbl_brands_categories_"+str(brand_id)+"_"+str(category_id)+" doesn't exists")

			# Load in postgres
			pgcur.execute("BEGIN")
			pgcur.execute("LISTEN notify_channel_tbl_brands_categories")
			args = [brand_id,category_id]
			pgcur.callproc("core_schema.udf_brands_categories_insert",args)
			pgcur.execute("COMMIT")
			#print ("Executed sucessfully udf_brands_categories_insert")
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

	except Exception as e:
		print ("Fail in listenerBrandsCategoriesRelationship. Error: "+ str(e))

def checkCategories(r,pgcon,pgcur,data_packet_elem,brand_id):

	try:

		# If exists in redis, do not insert in postgres
		if (r.hget("tbl_categories_"+data_packet_elem['category'],"name")):
			print ("tbl_categories_"+data_packet_elem['category']+" already exists")
			category_id = r.hget("tbl_categories_"+data_packet_elem['category'],"category_id")

			checkBrandsCategoriesRelationship(r,pgcon,pgcur,brand_id,category_id.decode())

		# If not exists in redis...
		else:
			print ("Category: "+data_packet_elem['category']+" doesn't exists")

			# Load in postgres
			pgcur.execute("BEGIN")
			pgcur.execute("LISTEN notify_channel_tbl_categories")
			args = [data_packet_elem['category']]
			pgcur.callproc("core_schema.udf_categories_insert",args)
			pgcur.execute("COMMIT")
			# print ("Executed sucessfully udf_categories_insert")
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

				checkBrandsCategoriesRelationship(r,pgcon,pgcur,brand_id,valuesDict['category_id'])

	except Exception as e:
		print ("Fail in listenerCategories. Error: "+ str(e))

def checkBrands(r,pgcon,pgcur,data_packet_elem):

	# If the current food belongs to a brand
	try:

		# If exists in redis, do not insert in postgres
		if (r.hget("tbl_brands_"+data_packet_elem['brand'],"name")):
			print ("tbl_brands_"+data_packet_elem['brand']+" already exists")
			brand_id = r.hget("tbl_brands_"+data_packet_elem['brand'],"brand_id")

			# Check if the category already exists in redis 
			checkCategories(r,pgcon,pgcur,data_packet_elem,brand_id.decode())

		# If not exists in redis, load in postgres
		else:
			print ("Brand: "+data_packet_elem['brand']+" doesn't exists")

			# Load in postgres
			pgcur.execute("BEGIN")
			pgcur.execute("LISTEN notify_channel_tbl_brands")
			args = [data_packet_elem['brand']]
			pgcur.callproc("core_schema.udf_brands_insert",args)
			pgcur.execute("COMMIT")
			# print ("Executed sucessfully udf_brands_insert")
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

				# Check if the category already exists in redis 
				checkCategories(r,pgcon,pgcur,data_packet_elem,valuesDict['brand_id'])

	# If the current food doesn't belongs to a brand
	except Exception as e:
		print ("Fail in listenerBrands. Maybe the current food is not related with a brand, so it won't be stored. Error: "+ str(e))

def main():

	r = redisConnection()
	pgcon, pgcur = postgresConnection()

	data_packet_list = []
	'''
	with open('foodChunk.json') as foodFile:
		data_packet_list = json.load(foodFile)
	'''
	data_packet_list = apiQuery()
	if (data_packet_list is not None):
		for i, data_packet_elem in enumerate(data_packet_list):
			checkBrands(r,pgcon,pgcur,data_packet_elem)
		print ("Food datapacket processed sucessfully")

	pgcon.close()
	pgcur.close()

if __name__ == '__main__':
    main()
