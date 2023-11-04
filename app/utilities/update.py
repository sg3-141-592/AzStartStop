import os
from azure.storage.blob import BlobServiceClient
import requests

DEPLOYMENT_URL = "https://startstopvmresources.compactcloud.co.uk/releases/az-start-stop-latest.squashfs"

def copy_url_to_blob() -> None:
    # Download the file from the URL
    response = requests.get(DEPLOYMENT_URL)
    data = response.content

    # Create a BlobServiceClient object using the connection string
    blob_service_client = BlobServiceClient.from_connection_string(
        conn_str=os.environ["AzureWebJobsStorage"]
    )

    container_client = blob_service_client.get_container_client("deployment")
    if not container_client.exists():
        container_client.create_container()

    # Get a BlobClient object for the container and blob
    blob_client = container_client.get_blob_client("az-start-stop-latest.squashfs")

    # Upload the file to the blob
    blob_client.upload_blob(data, overwrite=True)
