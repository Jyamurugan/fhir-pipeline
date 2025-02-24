from minio import Minio
from minio.error import S3Error
import configparser
from datetime import datetime
import os
from io import BytesIO

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__)), 'config.ini')

MINIO_URL = config['minio']['url']
ACCESS_KEY = config['minio']['access_key']
SECRET_KEY = config['minio']['secret_key']
BUCKET_NAME = config['minio']['bucket_name']
FHIR_BUCKET_PATHS = config['minio']['fhir_bucket_paths'].split(',')

print(MINIO_URL, ACCESS_KEY, SECRET_KEY, BUCKET_NAME, FHIR_BUCKET_PATHS)

def create_text_file(client, bucket_name, path, content):
    try:
        
        client.put_object(bucket_name, f"{path}/readme.txt", BytesIO(content.encode('utf-8')), len(content))
        print(f"Text file 'readme.txt' created successfully in path '{path}' of bucket '{bucket_name}'.")
    except S3Error as err:
        print(f"Error creating text file in path '{path}' of bucket '{bucket_name}': {err}")

def create_bucket(client, bucket_name):
    try:
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            print(f"Bucket '{bucket_name}' created successfully.")
        else:
            print(f"Bucket '{bucket_name}' already exists.")
    except S3Error as err:
        print(f"Error creating bucket '{bucket_name}': {err}")

def main():
    client = Minio(MINIO_URL, access_key=ACCESS_KEY, secret_key=SECRET_KEY, secure=False)
    create_bucket(client, BUCKET_NAME)
    for path in FHIR_BUCKET_PATHS:
        create_text_file(client, BUCKET_NAME, path, f"This is auto-generated text file\n{datetime.now()}")

if __name__ == "__main__":
    main()