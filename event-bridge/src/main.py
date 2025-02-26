import time
import requests
from minio import Minio
from minio.error import S3Error
from config import MINIO_URL, ACCESS_KEY, SECRET_KEY, BUCKET_NAME, TODO_PATH, EXECUTOR_ENDPOINT, POLL_INTERVAL

def poll_minio(client):
    try:
        objects = client.list_objects(BUCKET_NAME, prefix=TODO_PATH, recursive=True)
        objects = list(objects)
        for obj in objects:
            print(obj.object_name)
            if obj.object_name.endswith('.json'):
                send_to_executor(obj.object_name)
    except S3Error as err:
        print(f"Error polling MinIO: {err}")

def send_to_executor(object_key):
    try:
        response = requests.post(EXECUTOR_ENDPOINT, json={"object_key": object_key})
        if response.status_code == 200:
            print(f"Successfully sent {object_key} to executor.")
        else:
            print(f"Failed to send {object_key} to executor. Status code: {response.status_code}")
    except requests.RequestException as err:
        print(f"Error sending to executor: {err}")

def main():
    client = Minio(MINIO_URL, access_key=ACCESS_KEY, secret_key=SECRET_KEY, secure=False)
    while True:
        poll_minio(client)
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()