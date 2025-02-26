import json
import logging
from minio import Minio
from minio.error import S3Error
from config import MINIO_URL, ACCESS_KEY, SECRET_KEY, FHIR_BUCKET_NAME, ARCHIVE_BUCKET_NAME, TODO_BUCKET_PATH, ERROR_BUCKET_PATH
from flask import Flask, request, jsonify
from claim import process_fhir_bundle
from storage import ObjectStorageClient
from database import SQLiteDatabase

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

minio_client = ObjectStorageClient(
    url=MINIO_URL,
    access_key=ACCESS_KEY,
    secret_key=SECRET_KEY
)


@app.route('/api/process', methods=['POST'])
def process():
    data = request.get_json()
    object_key = data.get('object_key')
    
    if not object_key:
        logger.error('object_key is required')
        return jsonify({'error': 'object_key is required'}), 400
    
    try:
        try:
            response = minio_client.get_object(FHIR_BUCKET_NAME, object_key)
            data = response.read()
            json_data = data.decode('utf-8')
        except S3Error as e:
            logger.error('S3Error: %s', str(e))
            minio_client.dlq_error('minio',object_key, json_data, FHIR_BUCKET_NAME, ERROR_BUCKET_PATH)
            return jsonify({'error': str(e)}), 500
        except Exception as e:
            minio_client.dlq_error('processor',object_key, json_data, FHIR_BUCKET_NAME, ERROR_BUCKET_PATH)
            return jsonify({'error': 'Failed to process fhir bundle'}), 500
        
        claims = process_fhir_bundle(json_data)
        sqlite_client = SQLiteDatabase()
        sqlite_client.connect()
        for claim in claims:    
            try:
                sqlite_client.add_claim(claim)
            except Exception as e:
                logger.error('Failed to add claim to database: %s', str(e))
                minio_client.dlq_error('database',claim.claim_id, claim.toJSON(), FHIR_BUCKET_NAME, ERROR_BUCKET_PATH)
        minio_client.archive_fhir_bundle(data, object_key)
        logger.info('Processing complete for object_key: %s', object_key)
        return jsonify({'message': 'Processing complete'}), 200
    except S3Error as e:
        logger.error('S3Error: %s', str(e))
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        logger.error('Unexpected error: %s', str(e))
        return jsonify({'error': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)