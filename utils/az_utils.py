import os
from io import StringIO

from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = os.getenv("CONTAINER_NAME")
BLOB_NAME = os.getenv("BLOB_NAME")


def blob_client_helper():
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=BLOB_NAME)
    return blob_client

def download_blob_helper(blob_client):
    blob_data = blob_client.download_blob().readall()
    existing_data = StringIO(blob_data.decode("utf-8"))
    return existing_data

def upload_blob_helper(prod_riverflow_dataset, blob_client):
    output = StringIO()
    prod_riverflow_dataset.to_csv(output)
    output.seek(0)
    blob_client.upload_blob(output.getvalue(), overwrite=True)
