# Pub-Sub (Publisher-Subscriber) Design Pattern
Redis as cache of PostgreSQL and PubSub with LISTEN/NOTIFY
------------------------

This is an example of the logic to use in case where Redis is used, as cache of PostgreSQL. In architectures oriented to microservices, it's very useful to keep the power of PostgreSQL as DBMS, and allow the fast communication needed by the microservices to Redis. We can use PubSub design pattern in this context, using LISTEN/NOTIFY of PostgreSQL, of course, exists another kind of solutions for this type of architecture (even Redis has it's own [PubSub commands](https://redis.io/topics/pubsub) to implement this paradigm), but PostgreSQL offers to you all you need, using [**pg_notify** function](https://www.postgresql.org/docs/9.3/sql-notify.html) to send a notification as below:

```
	PERFORM pg_notify (<channel_name>, <payload>)
```
And receive the "message" with:

```
	LISTEN <channel_name>
```
For this example, i'll use **Edamam** API, to get a chunk of information. 

1. First of all, you'll need to register and get your own "app_id" and "app_key", you can find all the documentation here: https://developer.edamam.com/food-database-api-docs

2. Create your virtualenv and install the requirements:
```
	virtualenv virtual_name --python=python3
	source virtual_name/bin/activate
	pip install -r requirements.txt
```
3. Execute the wizard installer (this is a help to generate settings.ini file easy):
```
	sudo ./env/bin/python wizard_installer.py 
```
Assuming that "env" is the name of your virtualenv and it's located inside of the **pyPubSubPostgreSqlRedis** folder. The wizard will generate a **settings.ini** file, with the enviroment variables, related with the credentials of the API, PostgreSQL and Redis configuration. It also will create the PostgreSQL database, with all the statement in a **main_postgres_db_config.sh** file and execute, all the database elements contained in the folder **pubsub_db** folder. By last, the wizard also will start redis-server service. The structure of the **settings.ini** file, is described below:

	[pgConf]
	DB_NAME=dbname
	DB_USER=user
	DB_PASS=pass
	DB_HOST=host
	DB_PORT=port

	[redisConf]
	R_DB=dbNumber
	R_HOST=host
	R_PORT=port

	[appConf]
	APP_KEY=key
	APP_ID=id

Also, configuration for logging with 2 levels: ERROR (by output console and .log file) and INFO (by .log file):

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

4. And that's it. Now you can execute the pubSub.py file:
```
	python pubSub.py
```
If you have [Redis Desktop Manager](https://redisdesktop.com/), you can see how data is stored. In this case, I store Brands and Food Categories, but not all the Categories are related with a Brands, and also Brands hasn't a specific ID, so for this reason, either Categories and Brands data are store with this structure:

	<table_name>_<Food or Brand name>

And for the relationship between Categories and Brands:

	<table_name>_<brand_id PK>_<categories_id PK>
	
This last is the best option to store this data.

Also in case of Redis failure (e.g. Lost data in Redis), you can execute:

	python redisResetLoad.py3
	
To get all the information from PostgreSQL, and then, store again in Redis.

In this example you could find the basic logic for this kind of architecture, **Publish–subscribe pattern**.  

Contributions
-----------------------

All work to improve performance is good



Enjoy it!
