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

APP_KEY = config.get('appConf', 'APP_KEY')
APP_ID = config.get('appConf', 'APP_ID')

# Logs properties for console output
logging.config.fileConfig(fname=config, disable_existing_loggers=True)

# Logs properties for .logs files
def custom_filter(record):
	if record.levelname == 'INFO':
		return True

# Create a custom logger
handler_info = logging.FileHandler(BASE_DIR + '/logs/log_info.log','w')
handler_info.addFilter(custom_filter)
handler_info.setLevel(logging.INFO)

# Create handlers
handler_error = logging.FileHandler(BASE_DIR + '/logs/log_error.log','w')
handler_error.setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

# Create formatters and add it to handlers
format_info = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s : %(message)s')
format_error = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s')
handler_info.setFormatter(format_info)
handler_error.setFormatter(format_error)

# Add handlers to the logger
logger.addHandler(handler_info)
logger.addHandler(handler_error)
