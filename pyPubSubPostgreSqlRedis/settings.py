# -*- coding: utf-8 -*-
import os
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
