# -*- coding: utf-8 -*-
import os
import logging
import logging.config
from configparser import RawConfigParser

BASE_DIR = os.getcwd()
config = RawConfigParser()
config.read(BASE_DIR + '/settings.ini')

PG_DB_NAME = config.get('pgConf', 'DB_NAME')
PG_USER = config.get('pgConf', 'DB_USER')
PG_PASS = config.get('pgConf', 'DB_PASS')
PG_HOST = config.get('pgConf', 'DB_HOST')
PG_PORT = config.get('pgConf', 'DB_PORT')

R_DB = config.get('redisConf', 'R_DB')
R_HOST = config.get('redisConf', 'R_HOST')
R_PORT = config.get('redisConf', 'R_PORT')

APP_KEY = config.get('appConf', 'KEY')
APP_ID = config.get('appConf', 'ID')

# Logs properties for console output
logging.config.fileConfig(fname=config, disable_existing_loggers=True)

# Logs properties for .logs files

# Create a custom logger
logger = logging.getLogger(__name__)

# Create handlers
handler_info = logging.FileHandler('log_info.log')
handler_error = logging.FileHandler('log_error.log')
handler_info.setLevel(logging.INFO)
handler_error.setLevel(logging.ERROR)

# Create formatters and add it to handlers
format_info = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s : %(message)s')
format_error = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s')
handler_info.setFormatter(format_info)
handler_error.setFormatter(format_error)

# Add handlers to the logger
logger.addHandler(handler_info)
logger.addHandler(handler_error)
