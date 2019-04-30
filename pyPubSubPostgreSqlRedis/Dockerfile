#cargar la imagen de ubuntu32
#FROM 32bit/ubuntu:16.04
FROM python:3

# Set the working directory to pyPubSubPostgreSqlRedis
#WORKDIR /usr/src/app
WORKDIR /pyPubSubPostgreSqlRedis

COPY requirements.txt ./

# Copy the current directory contents into the container at /app
#ADD . /pyPubSubPostgreSqlRedis

# Make port 80 available to the world outside this container
# EXPOSE 80

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Give permission to create the database elements
CMD ["chmod +x","execute_all.sh"]

RUN ./execute_all.sh

# CMD [ "python", "./your-daemon-or-script.py" ]
