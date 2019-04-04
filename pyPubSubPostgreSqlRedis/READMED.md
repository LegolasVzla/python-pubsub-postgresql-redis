Redis as cache of Postgres and PubSub with LISTEN/NOTIFY
------------------------

This is an example of the logic to use in case where redis is used, as cache of postgres. In architectures oriented to microservices, it's very useful to keep the power of postgres as DBMS, and allow the fast communication needed by the microservices to Redis. We can use PubSub design pattern in this context, using LISTEN/NOTIFY of postgres, of course, exists another kind of solutions for this type of architecture, but postgres offers to you all you need :)

For this example, i'll use **Edamam** API, to get a chunk of information. First of all, you'll need to register and get your own "app_id" and "app_key", you can find all the documentation here: https://developer.edamam.com/food-database-api-docs

Install the requirements:

	pip install -r requirements.txt

Define your own connection settings for postgres and redis in the settings.ini file, and that's it. In this example you could find the basic logic for this kind of architecture.  


Contributions
-----------------------

All work to improve performance is good



Enjoy it!