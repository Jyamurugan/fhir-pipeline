import gzip
import io
import json
import logging
from minio import Minio
from minio.commonconfig import CopySource
from minio.error import S3Error
from config import MINIO_URL, ACCESS_KEY, SECRET_KEY, FHIR_BUCKET_NAME, ARCHIVE_BUCKET_NAME, TODO_BUCKET_PATH, ERROR_BUCKET_PATH
from flask import Flask, request, jsonify
from claim import process_fhir_bundle
import os
from datetime import datetime

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ObjectStorageClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ObjectStorageClient, cls).__new__(cls)
        return cls._instance

    def __init__(self, url, access_key, secret_key, secure=False):
        if not hasattr(self, 'initialized'):
            self.client = Minio(url, access_key=access_key, secret_key=secret_key, secure=secure)
            self.initialized = True

    def archive_fhir_bundle(self, data: bytes, fhir_bundle_object_key: str) -> None:
        try:
            gzipped_data = gzip.compress(data)
            date_str = datetime.now().strftime("%Y-%m-%d")
            filename = os.path.basename(fhir_bundle_object_key)
            gzipped_object_key = f"{date_str}/{filename}.gz"
            self.client.put_object(ARCHIVE_BUCKET_NAME, gzipped_object_key, io.BytesIO(gzipped_data), len(gzipped_data), content_type='application/gzip')
            self.client.remove_object(FHIR_BUCKET_NAME, fhir_bundle_object_key)
        except S3Error as e:
            logger.warning('S3Error: %s', str(e))
        
    def dlq_error(self, type: str, claim_id: str, json: str, fhir_bucket: str, error_path: str) -> None:
        try:
            error_object_key = f"{error_path}/{type}/{claim_id}.json"
            encoded_json = json.encode('utf-8')
            self.client.put_object(fhir_bucket, error_object_key, io.BytesIO(encoded_json), len(encoded_json), content_type='application/json')
        except S3Error as e:
            logger.warning('S3Error: %s', str(e))

    def get_object(self, bucket_name: str, object_key: str):
        try:
            return self.client.get_object(bucket_name, object_key)
        except S3Error as e:
            logger.error('S3Error: %s', str(e))
            raise
