Redis as cache of Postgres and PubSub with LISTEN/NOTIFY
------------------------

This is an example of the logic to use in case where redis is used, as cache of postgres. In architectures oriented to microservices, it's very useful to keep the power of postgres as DBMS, and allow the fast communication needed by the microservices to Redis. We can use PubSub design pattern in this context, using LISTEN/NOTIFY of postgres, of course, exists another kind of solutions for this type of architecture, but postgres offers to you all you need :)

For this example, i'll use **Edamam** API, to get a chunk of information. First of all, you'll need to register and get your own "app_id" and "app_key", you can find all the documentation here: https://developer.edamam.com/food-database-api-docs

Create your virtualenv and install the requirements:

	virtualenv virtual_name --python=python3
	source virtual_name/bin/activate

	pip install -r requirements.txt

Start redis server in your console:

	redis-server

Give permission to "execute_all.sh":

	chmod +x pubsub_db/execute_all.sh
	sudo -i -u postgres

Move to the folder of the project and execute it as postgres user:

	./execute_all.sh

Now you have create your database and all the functions needed.

Define your own connection settings for postgres and redis in the settings.ini file (according to configparser) as follow:

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

Also, for logging, I set this configuration in my settings.ini file:

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

And that's it. In this example you could find the basic logic for this kind of architecture.  

Also in case of redis failure (e.g. Lost data in redis), you can execute "redisResetLoad.py3" to get all the information from postgres, and then, store again in redis.

Contributions
-----------------------

All work to improve performance is good



Enjoy it!