import configparser
import os

config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
config.read(config_path)

MINIO_URL = config['minio']['url']
ACCESS_KEY = config['minio']['access_key']
SECRET_KEY = config['minio']['secret_key']
BUCKET_NAME = config['minio']['bucket_name']
TODO_PATH = config['minio']['bucket_path']

EXECUTOR_ENDPOINT = config['EXECUTOR']['endpoint']

POLL_INTERVAL = int(config['SETTINGS']['poll_interval'])