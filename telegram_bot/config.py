import os
import configparser

BOT_TOKEN = os.environ.get('BOT_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
DATABASE_USER = os.environ.get('DATABASE_USER')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')

config = configparser.ConfigParser()
config.read('config.ini')

# Get the value of a configuration setting
app_settings = dict(config.items('app'))
app_name = app_settings['name']
app_version = float(app_settings['version'])
app_debug = bool(app_settings['debug'])
app_user_max_chats = int(app_settings['user_max_chats'])

database_settings = dict(config.items('database'))
database_name = database_settings['database']
database_host = database_settings['host']
database_port = int(database_settings['port'])