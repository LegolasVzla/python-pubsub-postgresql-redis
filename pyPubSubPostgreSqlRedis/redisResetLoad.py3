# -*- coding: utf-8 -*-
import psycopg2, psycopg2.extras
import select
import redis
import json
from settings import *

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
		logger.error("Postgres connection is not ready yet. Error: " + str(e))
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
		logger.error("Redis connection is not ready yet. Error: " + str(e))
	return r

def listen(pgcon, pgcur, channel):
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
		return None

def loadRedisBrands(r,pgcon,pgcur):
	try:

		pgcur.execute("BEGIN")
		pgcur.execute("LISTEN notify_channel_tbl_brands")
		pgcur.callproc("core_schema.udf_load_redis_brand")
		nrows = pgcur.fetchone()
		pgcur.execute("COMMIT")
		logger.info("Executed successfully udf_load_redis_brand")

		if (nrows[0] != None):
			current_row = 0
			while(current_row != nrows[0]):

				payload = listen(pgcon,pgcur,'notify_channel_tbl_brands')

				if (payload is not None):

					json_response = json.loads(payload)

					key = json_response['redisHash']
					valuesDict = {}
					valuesDict['brand_id'] = str(json_response['brand_id'])
					valuesDict['name'] = json_response['redisHash']

					# Send values to Redis
					r.hmset(key,valuesDict)
					logger.info("Values sent to redis successfully: "+key+","+json.dumps(valuesDict))
					current_row+=1
			return True
		else:
			return False

	except Exception as e:
		logger.error("Fail in loadRedisBrands. Error: "+ str(e))
		return False

def loadRedisCategories(r,pgcon,pgcur):
	try:

		pgcur.execute("BEGIN")
		pgcur.execute("LISTEN notify_channel_tbl_categories")
		pgcur.callproc("core_schema.udf_load_redis_categories")
		nrows = pgcur.fetchone()
		pgcur.execute("COMMIT")
		logger.info("Executed successfully udf_load_redis_categories")

		if (nrows[0] != None):
			current_row = 0
			while(current_row != nrows[0]):

				payload = listen(pgcon,pgcur,'notify_channel_tbl_categories')

				if (payload is not None):

					json_response = json.loads(payload)

					key = json_response['redisHash']
					valuesDict = {}
					valuesDict['category_id'] = str(json_response['category_id'])
					valuesDict['name'] = json_response['redisHash']

					# Send values to Redis
					r.hmset(key,valuesDict)
					logger.info("Values sent to redis successfully: "+key+","+json.dumps(valuesDict))
					current_row+=1
			return True
		else:
			return False

	except Exception as e:
		logger.error("Fail in loadRedisCategories. Error: "+ str(e))
		return False

def loadRedisBrandsCategories(r,pgcon,pgcur):
	try:
		pgcur.execute("BEGIN")
		pgcur.execute("LISTEN notify_channel_tbl_brands_categories")
		pgcur.callproc("core_schema.udf_load_redis_brands_categories")
		nrows = pgcur.fetchone()
		pgcur.execute("COMMIT")
		logger.info("Executed successfully udf_load_redis_brands_categories")

		if (nrows[0] != None):
			current_row = 0
			while(current_row != nrows[0]):

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
					logger.info("Values sent to redis successfully: "+key+","+json.dumps(valuesDict))
					current_row+=1
			return True
		else:
			return False

	except Exception as e:
		logger.error("Fail in loadRedisBrandsCategories. Error: "+ str(e))
		return False

def redisResetLoad(r,pgcon,pgcur):
	try:
		r.flushdb()

		if (loadRedisBrands(r,pgcon,pgcur) == True
			and loadRedisCategories(r,pgcon,pgcur) == True
			and loadRedisBrandsCategories(r,pgcon,pgcur) == True):
			print("Redis has been populated successfully")
		else:
			print("Error: Redis hasn't been populated")

	except Exception as e:
		logger.error("Fail in redisResetLoad. Error: "+ str(e))

def main():

	r = redisConnection()
	pgcon, pgcur = postgresConnection()	

	redisResetLoad(r,pgcon,pgcur)

	pgcon.close()
	pgcur.close()

if __name__ == '__main__':
    main()
