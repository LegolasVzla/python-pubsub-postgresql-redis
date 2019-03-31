# -*- coding: utf-8 -*-
import psycopg2, psycopg2.extras
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

def listenerBrandsCategoriesRelationship(brand_id,category_id):

	try:

		r = redisConnection()
		pgcon, pgpcur = postgresConnection()

		# If exists in redis, do not insert in postgres
		if (r.hget(
			"tbl_brands_categories_"+str(brand_id)+"_"+str(category_id),"category_id")):
			print ("tbl_brands_categories_"+str(brand_id)+"_"+str(category_id)+" already exists")

		# If not exists in redis...
		else:
			print ("tbl_brands_categories"+str(brand_id)+"_"+str(category_id)+" doesn't exists")

			# Load in postgres
			pgpcur.execute("BEGIN")
			#pgpcur.execute("LISTEN notify_channel_tbl_brands_categories")
			args = [brand_id,category_id]
			pgpcur.callproc("core_schema.udf_brands_categories_insert",args)
			brands_categories_result = pgpcur.fetchone()
			pgpcur.execute("COMMIT")
			print ("Executed sucessfully udf_brands_categories_insert")

			if (brands_categories_result[0] == '1'):

				key = "tbl_brands_categories_"+str(brand_id)+"_"+str(category_id)
				valuesDict = {}
				valuesDict['brand_id'] = str(brand_id)
				valuesDict['category_id'] = str(category_id)

				# Send values to Redis
				r.hmset(key,valuesDict)

	except Exception as e:
		print ("Fail in listenerBrandsCategoriesRelationship. Error: "+ str(e))

	finally:
		pgcon.close()
		pgpcur.close()

def listenerCategories(data_packet_elem,brand_id):

	try:

		r = redisConnection()
		pgcon, pgpcur = postgresConnection()

		# If exists in redis, do not insert in postgres
		if (r.hget("tbl_categories_"+data_packet_elem['category'],"name")):
			print ("tbl_categories_"+data_packet_elem['category']+" already exists")
			category_id = r.hget("tbl_categories_"+data_packet_elem['category'],"category_id")

			listenerBrandsCategoriesRelationship(brand_id,category_id[0])

		# If not exists in redis...
		else:
			print ("Category: "+data_packet_elem['category']+" doesn't exists")

			# Load in postgres
			pgpcur.execute("BEGIN")
			#pgpcur.execute("LISTEN notify_channel_tbl_categories")
			args = [data_packet_elem['category']]
			pgpcur.callproc("core_schema.udf_categories_insert",args)
			category_id = pgpcur.fetchone()
			pgpcur.execute("COMMIT")
			# print ("Executed sucessfully udf_categories_insert")

			if (category_id is not None):

				key = "tbl_categories_"+data_packet_elem['category']
				valuesDict = {}
				valuesDict['name'] = data_packet_elem['category']
				valuesDict['category_id'] = str(category_id[0])

				# Send values to Redis
				r.hmset(key,valuesDict)

				listenerBrandsCategoriesRelationship(brand_id,category_id[0])

	except Exception as e:
		print ("Fail in listenerCategories. Error: "+ str(e))

	finally:
		pgcon.close()
		pgpcur.close()

def listenerBrands(data_packet_elem):

	# If the current food belongs to a brand
	try:

		r = redisConnection()
		pgcon, pgpcur = postgresConnection()

		# If exists in redis, do not insert in postgres
		if (r.hget("tbl_brands_"+data_packet_elem['brand'],"name")):
			print ("tbl_brands_"+data_packet_elem['brand']+" already exists")
			brand_id = r.hget("tbl_brands_"+data_packet_elem['brand'],"brand_id")

			# Check if the category already exists in redis 
			listenerCategories(data_packet_elem,brand_id[0])

		# If not exists in redis, load in postgres
		else:
			print ("Brand: "+data_packet_elem['brand']+" doesn't exists")

			# Load in postgres
			pgpcur.execute("BEGIN")
			#pgpcur.execute("LISTEN notify_channel_tbl_brands")
			args = [data_packet_elem['brand']]
			pgpcur.callproc("core_schema.udf_brands_insert",args)
			brand_id = pgpcur.fetchone()
			pgpcur.execute("COMMIT")
			# print ("Executed sucessfully udf_brands_insert")

			if (brand_id is not None):

				key = "tbl_brands_"+data_packet_elem['brand']
				valuesDict = {}
				valuesDict['name'] = data_packet_elem['brand']
				valuesDict['brand_id'] = str(brand_id[0])

				# Send values to Redis
				r.hmset(key,valuesDict)

				# Check if the category already exists in redis 
				listenerCategories(data_packet_elem,brand_id[0])

	# If the current food doesn't belongs to a brand
	except Exception as e:
		print ("Fail in listenerBrands. Maybe the current food is not related with a brand, so it won't be stored. Error: "+ str(e))

	finally:
		pgcon.close()
		pgpcur.close()

def main():

	data_packet_list = []
	'''
	with open('foodChunk.json') as foodFile:
		data_packet_list = json.load(foodFile)
	'''
	data_packet_list = apiQuery()
	if (data_packet_list is not None):
		for i, data_packet_elem in enumerate(data_packet_list):
			listenerBrands(data_packet_elem)
		print ("Food datapacket processed sucessfully")

if __name__ == '__main__':
    main()
