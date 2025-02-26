import configparser
import os

config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
config.read(config_path)

MINIO_URL = config['minio']['url']
ACCESS_KEY = config['minio']['access_key']
SECRET_KEY = config['minio']['secret_key']
FHIR_BUCKET_NAME = config['minio']['fhir_bucket_name']
ARCHIVE_BUCKET_NAME = config['minio']['archive_bucket_name']
TODO_BUCKET_PATH = config['minio']['todo_bucket_path']
ERROR_BUCKET_PATH = config['minio']['error_bucket_path']

SQLITE_DATABASE_PATH = config['database']['uri']
