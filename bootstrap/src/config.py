import configparser
import os

config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
config.read(config_path)

MINIO_URL = config['minio']['url']
ACCESS_KEY = config['minio']['access_key']
SECRET_KEY = config['minio']['secret_key']
BUCKET_NAMES = config['minio']['bucket_names'].split(',')
FHIR_BUCKET_PATHS = config['minio']['fhir_bucket_paths'].split(',')