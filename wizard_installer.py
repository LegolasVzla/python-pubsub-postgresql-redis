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
	"Enter a redis database index. \n REDIS DATABASE INDEX: ",
	"Enter a redis database port. \n REDIS DATABASE PORT: "	
	]
OUTPUT_MESSAGES = ["Configuration finish unsuccessfully by the user.",
	"[ ERROR ] You must provide the app key.",
	"[ ERROR ] You must provide the app id.",
	"[ ERROR ] You must provide an user for the postgres configuration.",
	"[ ERROR ] You must provide a password for the postgres configuration.",
	"[ ERROR ] You must provide a database name for the postgres configuration.",
	"[ ERROR ] You must provide a database index for the redis configuration.",
	"[ ERROR ] You must provide a database port for the redis configuration.",
	"[ ERROR ] Please provide a different username.",
	"[ ERROR ] Please provide a different password."
	]

class bcolors:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def udf_postgres_test_connection(postgres_db_name, postgres_db_user, 
	postgres_db_pass, postgres_db_host, postgres_db_port):
	print (bcolors.OKBLUE + "Testing postgres connection..." + bcolors.ENDC)
	time.sleep(1)
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
		print (bcolors.OKGREEN + "[ OK ] Successful Test Connection with Postgres." + bcolors.ENDC)
		return True
	except (Exception,psycopg2.DatabaseError) as e:
		print (bcolors.FAIL + "Postgres connection is not ready yet. Error: " + str(e) + bcolors.ENDC)

def udf_redis_test_connection(redis_db_index,redis_db_host,redis_db_port):
	print (bcolors.OKBLUE + "Testing redis connection..." + bcolors.ENDC)
	try:
		subprocess.call("nohup redis-server --port "+str(redis_db_port)+" &",shell=True)
		pool = redis.ConnectionPool(
			host=redis_db_host,
			port=redis_db_port,
			db=redis_db_index
			)
		r = redis.Redis(connection_pool=pool)
		time.sleep(1)
		if(r.ping()):
			print (bcolors.OKGREEN + "[ OK ] Successful Test Connection with Redis." + bcolors.ENDC)
			return True
	except Exception as e:
		print (bcolors.FAIL + "Redis connection is not ready yet. Error: " + str(e) + bcolors.ENDC)

def udf_replace_parameters(text, dic):
	for i, j in dic.items():
		text = text.replace(i, str(j))
	return text

def udf_postgres_configuration_create(postgres_db_user,postgres_db_pass):

	global BASE_PATH

	text="""#!/bin/bash
sudo -u postgres psql -c "DROP DATABASE IF EXISTS pubsub_db;"
sudo -u postgres psql -c "DROP USER IF EXISTS postgres_db_user;"
sudo -u postgres psql -c "CREATE USER postgres_db_user WITH PASSWORD 'postgres_db_pass';"
sudo -u postgres psql -c "ALTER ROLE postgres_db_user WITH SUPERUSER;"
sudo -u postgres psql -c "CREATE DATABASE pubsub_db WITH OWNER postgres_db_user;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE pubsub_db TO postgres_db_user;"
sudo -u postgres psql -d pubsub_db -a -c "CREATE SCHEMA core_schema;"
"""

	dictionary = {"postgres_db_user": postgres_db_user,
				"postgres_db_pass": postgres_db_pass}

	# Replace default parameters name to parameters named by the user
	new_file_content = udf_replace_parameters(text, dictionary)

	# Create the main postgres database configuration file
	with open(BASE_PATH + "/pubsub_db/main_postgres_db_config.sh", "+w") as text_file:
		text_file.write(new_file_content)

def udf_postgres_execute_database_object(postgres_db_name,db_elem_folder,schema_path):

	global BASE_PATH
	os.chdir(db_elem_folder)
	CURRENT_PATH = os.getcwd()

	# Get the current database objects (tables and functions list)
	DB_ELEMENTS_OBJECTS = os.listdir(os.getcwd())

	# Execute all the database objects (tables and functions list)
	for j,db_elem_object in enumerate(DB_ELEMENTS_OBJECTS):

		os.chdir(BASE_PATH)

		subprocess.call("sudo -u postgres psql -d "+postgres_db_name+" -a -f "+CURRENT_PATH+"/"+db_elem_object,shell=True)

		os.chdir(CURRENT_PATH)

	# Return to the core_schema folder
	os.chdir(schema_path)

def udf_postgres_create_database_elements(postgres_db_name,postgres_db_pass,postgres_db_user,postgres_db_host,postgres_db_port):

	os.chdir("core_schema")
	SCHEMA_PATH = os.getcwd()

	db_elem_folder = "tables"
	udf_postgres_execute_database_object(postgres_db_name,db_elem_folder,SCHEMA_PATH)

	db_elem_folder = "relations"
	udf_postgres_execute_database_object(postgres_db_name,db_elem_folder,SCHEMA_PATH)

	db_elem_folder = "functions"
	udf_postgres_execute_database_object(postgres_db_name,db_elem_folder,SCHEMA_PATH)

	# Return to the pubsub_db folder
	os.chdir(BASE_PATH)

def udf_parameters_validation(input_message,error_message):
	global OUTPUT_MESSAGES, INPUT_MESSAGES
	parameter = ""
	validator = False
	while not parameter and validator is False:
		parameter = input(input_message)
		if parameter.strip():
			if parameter == 'exit':
				print (bcolors.FAIL + OUTPUT_MESSAGES[0] + bcolors.ENDC)
				os._exit(0)
			# Consider reserved words for postgres configuration
			elif input_message == INPUT_MESSAGES[2] and parameter == 'user':
				parameter = ""
				print (bcolors.FAIL + OUTPUT_MESSAGES[8] + bcolors.ENDC)
			elif input_message == INPUT_MESSAGES[3] and parameter == 'password':
				parameter = ""
				print (bcolors.FAIL + OUTPUT_MESSAGES[9] + bcolors.ENDC)
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
			print (bcolors.FAIL + error_message + bcolors.ENDC)
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
	redis_db_port = None
	redis_validator = False
	
	print (bcolors.BOLD + "-------Wizard Installer-------\n" + bcolors.ENDC)
	print ("Write 'exit' if you want to exit")
	print (bcolors.BOLD + "\n**** Credentials API Configuration ****" + bcolors.ENDC)
	while (api_validator is False):
		app_key = udf_parameters_validation(INPUT_MESSAGES[0],OUTPUT_MESSAGES[1])
		app_id = udf_parameters_validation(INPUT_MESSAGES[1],OUTPUT_MESSAGES[2])
		try:
			for x in range(0,3):
				print (bcolors.OKBLUE + "Testing api connection..." + bcolors.ENDC)
				response = requests.get(
					"https://api.edamam.com/api/food-database/parser?ingr=red%20apple&app_id="+app_id+"&app_key="+app_key, timeout=10
					)
				if(response.ok):
					print (bcolors.OKGREEN + "[ OK ] Successful Test Connection with the API" + bcolors.ENDC)
					api_validator = True
					break
				else:
					print (bcolors.WARNING + "Fail in response. Status code: "+str(response.status_code)+"\n" + bcolors.ENDC)
					print("Trying again...")
					api_validator_count+=1
					time.sleep(2)
					if(x == 2):
						print (bcolors.FAIL + "[ ERROR ] Failed test connection with the API. Perhaps your APP_KEY or APP_ID credentials are wrong.\n" + bcolors.ENDC)
		except requests.exceptions.ConnectionError as e:
			api_validator = False
			print (bcolors.FAIL + "Fail in api_query. Error: "+ str(e) + bcolors.ENDC)

	print (bcolors.BOLD + "\n**** Postgresql Database Configuration ****" + bcolors.ENDC)
	while (postgres_validator is False):
		postgres_db_user = udf_parameters_validation(INPUT_MESSAGES[2],OUTPUT_MESSAGES[3])
		postgres_db_pass = udf_parameters_validation(INPUT_MESSAGES[3],OUTPUT_MESSAGES[4])
		try:
			# Create the postgres configuration
			udf_postgres_configuration_create(postgres_db_user, postgres_db_pass)

			# Generate the main postgres database
			os.chdir(BASE_PATH + "/pubsub_db/")
			os.chmod("main_postgres_db_config.sh", 775)
			subprocess.call("./main_postgres_db_config.sh", shell=False)

		except Exception as e:
			print (bcolors.FAIL + "Fail creating the postgresql configuration. Error: " + str(e) + bcolors.ENDC)

		'''
		Consider the case where password started with puntuaction signs
		or numbers in udf_parameters_validation(), remove ""
		'''  
		if(postgres_db_pass[0] == '"'):
			postgres_db_pass = postgres_db_pass.replace('"','')

		if(udf_postgres_test_connection(postgres_db_name,postgres_db_user,
			postgres_db_pass,postgres_db_host, postgres_db_port)):

			# Create the tables and the functions needed
			udf_postgres_create_database_elements(postgres_db_name,postgres_db_pass,postgres_db_user,postgres_db_host,postgres_db_port)
			os.chdir(BASE_PATH)

			postgres_validator = True

		else:
			print("Please enter your postgres configuration again.\n")

	print (bcolors.BOLD + "\n**** Redis Configuration ****" + bcolors.ENDC)
	while (redis_validator is False):
	    redis_db_index = udf_parameters_validation(INPUT_MESSAGES[5],OUTPUT_MESSAGES[6])
	    redis_db_port = udf_parameters_validation(INPUT_MESSAGES[6],OUTPUT_MESSAGES[7])
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

	# Create the settings.ini file
	udf_environment_configuration_create(postgres_db_name, postgres_db_user,
		postgres_db_pass, postgres_db_host, postgres_db_port, redis_db_index,
		redis_db_host, redis_db_port, app_key, app_id)

	if exists('settings.ini'):
		print (bcolors.OKGREEN + "\nWizard intaller finished susccessfully." + bcolors.ENDC)
	else:
		print (bcolors.FAIL + "\n[ ERROR ] Wizard installer finished unsuccessfully. Check the permissions of this wizard installer file." + bcolors.ENDC)		

if __name__ == '__main__':
    main()
