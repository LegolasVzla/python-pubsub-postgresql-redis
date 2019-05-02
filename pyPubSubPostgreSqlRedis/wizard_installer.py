#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
from os.path import exists
import string
import requests
import subprocess
import time
import psycopg2, psycopg2.extras
import redis

BASE_PATH = os.getcwd()

INPUT_MESSAGES = ["Enter the app key: \n APP_KEY: ",
	"Enter the app id: \n APP_ID: ",
	"Enter a postgres user. \n POSTGRESQL USER: ",
	"Enter a postgresql password. \n POSTGRESQL PASSWORD: ",
	"Enter a postgresql database name. \n POSTGRESQL DATABASE NAME: ",
	"Enter a redis database number. \n REDIS DATABASE NUMBER: "
	]
OUTPUT_MESSAGES = ["Configuration finish unsuccessfully by the user.",
	"[ ERROR ] You must provide the app key.",
	"[ ERROR ] You must provide the app id.",
	"[ ERROR ] You must provide an user for the postgres configuration.",
	"[ ERROR ] You must provide a password for the postgres configuration.",
	"[ ERROR ] You must provide a database name for the postgres configuration.",
	"[ ERROR ] You must provide a database number for the redis configuration.",
	"[ ERROR ] Please provide a different username.",
	"[ ERROR ] Please provide a different password."
	]

def udf_postgres_test_connection(postgres_db_name, postgres_db_user, 
	postgres_db_pass, postgres_db_host, postgres_db_port):
	validator = False
	try:
		conn = psycopg2.connect(
			database=postgres_db_name,
			user=postgres_db_user,
			password=postgres_db_pass,
			host=postgres_db_host,
			port=postgres_db_port,
			connect_timeout=10
			)
		curs = conn.cursor()
		print ("[ OK ] Successful Test Connection with Postgres.")
		validator = True
	except (Exception,psycopg2.DatabaseError) as e:
		print("Postgres connection is not ready yet. Error: " + str(e))
	return validator

def udf_redis_test_connection(redis_db_index,redis_db_host,redis_db_port):
	validator = False
	try:
		subprocess.call("nohup redis-server &",shell=True)
		pool = redis.ConnectionPool(
			host=redis_db_host,
			port=redis_db_port,
			db=redis_db_index
			)
		r = redis.Redis(connection_pool=pool)
		time.sleep(1)
		if(r.ping()):
			validator = True
			print ("[ OK ] Successful Test Connection with Redis.")
	except Exception as e:
		print("Redis connection is not ready yet. Error: " + str(e))
	return validator

# Function to set host and port in redis.conf
def udf_redis_configuration_update(redis_db_host, redis_db_port):
	pass

def udf_replace_parameters(text, dic):
	for i, j in dic.items():
		text = text.replace(i, str(j))
	return text

def udf_postgres_configuration_create(postgres_db_user,postgres_db_pass):

	global BASE_PATH

	with open(BASE_PATH + "/pubsub_db/execute_all.sh") as text_file:
		temporal_file_content = text_file.read()

	dictionary = {"postgres_db_user": postgres_db_user,
				"postgres_db_pass": postgres_db_pass}

	# Replace default parameters name to parameters named by the user
	new_file_content = udf_replace_parameters(temporal_file_content, dictionary)

	with open(BASE_PATH + "/pubsub_db/execute_all.sh", "+w") as text_file:
		text_file.write(new_file_content)

def udf_parameters_validation(input_message,error_message):
	global OUTPUT_MESSAGES, INPUT_MESSAGES
	parameter = ""
	validator = False
	while not parameter and validator is False:
		parameter = input(input_message)
		if parameter.strip():
			if parameter == 'exit':
				print (OUTPUT_MESSAGES[0])
				os._exit(0)
			# Consider reserved words for postgres configuration
			elif input_message == INPUT_MESSAGES[2] and parameter == 'user':
				parameter = ""
				print (OUTPUT_MESSAGES[7])
			elif input_message == INPUT_MESSAGES[3] and parameter == 'password':
				parameter = ""
				print (OUTPUT_MESSAGES[8])
			# Consider when password start with numbers
			elif input_message == INPUT_MESSAGES[3] and parameter[0].isdigit():
				parameter = '"' + parameter + '"'
				validator = True
			# Consider when password start with punctuation signs and numbers
			elif input_message == INPUT_MESSAGES[3] and parameter[0] in string.punctuation and parameter[1].isdigit():
				parameter = '"' + parameter + '"'
				validator = True
			else:
				validator = True
		# Empty input
		else:
			parameter = ""
			print (error_message)
	return parameter

def udf_environment_validation_parameters():
	global INPUT_MESSAGES, OUTPUT_MESSAGES
	app_key = None
	app_id = None
	api_validator = False
	api_validator_count = 0
	postgres_db_name = 'pubsub_db'
	postgres_db_user = None
	postgres_db_pass = None
	postgres_db_host = 'localhost'
	postgres_db_port = 5432
	postgres_validator = False
	redis_db_index = None
	redis_db_host = 'localhost'
	redis_db_port = 6379
	redis_validator = False
	
	print ("-----Wizard Installer-----\n(Write 'exit' if you want to exit)")
	print ("\n**** Credentials API Configuration ****")
	while (api_validator is False):
		app_key = udf_parameters_validation(INPUT_MESSAGES[0],OUTPUT_MESSAGES[1])
		app_id = udf_parameters_validation(INPUT_MESSAGES[1],OUTPUT_MESSAGES[2])
		try:
			for x in range(0,3):
				print ("Testing api connection...")
				response = requests.get(
					"https://api.edamam.com/api/food-database/parser?ingr=red%20apple&app_id="+app_id+"&app_key="+app_key, timeout=10
					)
				if(response.ok):
					print ("[ OK ] Successful Test Connection with the API")
					api_validator = True
					break
				else:
					print("Fail in response. Status code: "+str(response.status_code)+"\n")
					print("Trying again...")
					api_validator_count+=1
					time.sleep(2)
					if(x == 2):
						print ("[ ERROR ] Failed test connection with the API. Perhaps your APP_KEY or APP_ID credentials are wrong.\n")
		except requests.exceptions.ConnectionError as e:
			api_validator = False
			print("Fail in api_query. Error: "+ str(e))

	print ("\n**** Postgresql Database Configuration ****")
	while (postgres_validator is False):
		postgres_db_user = udf_parameters_validation(INPUT_MESSAGES[2],OUTPUT_MESSAGES[3])
		postgres_db_pass = udf_parameters_validation(INPUT_MESSAGES[3],OUTPUT_MESSAGES[4])
		try:
			# Create the postgres configuration
			udf_postgres_configuration_create(postgres_db_user, postgres_db_pass)
			# Execute all the functions needed
			os.chdir(BASE_PATH + "/pubsub_db/")
			os.chmod("execute_all.sh", 775)
			subprocess.call("./execute_all.sh", shell=False)
			os.chdir(BASE_PATH)

		except Exception as e:
			print ("Fail creating the postgresql configuration. Error: " + str(e))

		'''
		Consider the case where password started with puntuaction signs
		or numbers in udf_parameters_validation(), remove ""
		'''  
		if(postgres_db_pass[0] == '"'):
			postgres_db_pass = postgres_db_pass.replace('"','')

		if(udf_postgres_test_connection(postgres_db_name,postgres_db_user,
			postgres_db_pass,postgres_db_host, postgres_db_port)):
			postgres_validator = True
		else:
			print("Please enter your postgres configuration again.\n")

	print ("\n**** Redis Configuration ****")
	while (redis_validator is False):
	    redis_db_index = udf_parameters_validation(INPUT_MESSAGES[5],OUTPUT_MESSAGES[6])
	    if(udf_redis_test_connection(redis_db_index,redis_db_host,redis_db_port)):
	    	redis_validator = True
	    else:
	    	print("Please enter your redis configuration again.\n")

	return (postgres_db_name, postgres_db_user, postgres_db_pass, 
	postgres_db_host, postgres_db_port, redis_db_index, redis_db_host, 
	redis_db_port, app_key, app_id)

def udf_environment_configuration_create(postgres_db_name, postgres_db_user,
		postgres_db_pass, postgres_db_host, postgres_db_port, redis_db_index,
		redis_db_host, redis_db_port, app_key, app_id):
	'''
	Parameters for a settings.ini file with postgres, redis and api credentials,
	also, this part setting the logging with 2 levels:
	- ERROR level: to print errors by the console and in a .log file
	- INFO level: to print successfull messages in a .log file
	'''
	text = """[pgConf]
DB_NAME=pubsub_db
DB_USER=postgres_db_user
DB_PASS=postgres_db_pass
DB_HOST=postgres_db_host
DB_PORT=postgres_db_port

[redisConf]
R_DB=redis_db_index
R_HOST=redis_db_host
R_PORT=redis_db_port

[appConf]
APP_KEY=app_key
APP_ID=app_id

[loggers]
keys=root

[handlers]
keys=consoleHandler

[formatters]
keys=sampleFormatter

[logger_root]
level=INFO
handlers=consoleHandler

[handler_consoleHandler]
class=StreamHandler
level=ERROR
formatter=sampleFormatter
args=(sys.stdout,)

[formatter_sampleFormatter]
format=%(asctime)s - %(levelname)s - %(message)s
    """

	dictionary = {"postgres_db_name": postgres_db_name, 
				"postgres_db_user": postgres_db_user,
				"postgres_db_pass": postgres_db_pass,
				"postgres_db_host": postgres_db_host,
				"postgres_db_port": postgres_db_port,
				"redis_db_index": redis_db_index,
				"redis_db_host": redis_db_host,
				"redis_db_port": redis_db_port,
				"app_key": app_key,
				"app_id": app_id}

	settings_variables = udf_replace_parameters(text, dictionary)

	with open("settings.ini", "+w") as text_file:
		text_file.write(settings_variables)

def main():

	global BASE_PATH

	# Get all the values for the configuration parameters
	(postgres_db_name, postgres_db_user, postgres_db_pass, 
	postgres_db_host, postgres_db_port, redis_db_index, 
	redis_db_host, redis_db_port, app_key, app_id) = udf_environment_validation_parameters()

	udf_redis_configuration_update(redis_db_host, redis_db_port)

	# Create the settings.ini file
	udf_environment_configuration_create(postgres_db_name, postgres_db_user,
		postgres_db_pass, postgres_db_host, postgres_db_port, redis_db_index,
		redis_db_host, redis_db_port, app_key, app_id)

	if exists('settings.ini'):
		print ("\nWizard intaller finished susccessfully.")
	else:
		print ("\n[ ERROR ] Wizard installer finished unsuccessfully. Check the permissions of this wizard installer file.")		

if __name__ == '__main__':
    main()
