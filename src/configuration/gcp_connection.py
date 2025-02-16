from google.cloud import storage
import os
from google.auth import exceptions
from src.constants import GCS_BUCKET_NAME_ENV_KEY

class GCSClient:
    gcs_client = None
    gcs_resource = None

    def __init__(self):
        """ 
        This class connects to Google Cloud Storage and raises an exception 
        if the environment variable for authentication is not set.
        """
        
        # Check if the Google Cloud credentials environment variable is set
        if GCSClient.gcs_resource is None or GCSClient.gcs_client is None:
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            
            if credentials_path is None:
                raise Exception("Environment variable GOOGLE_APPLICATION_CREDENTIALS is not set.")
            
            try:
                # Initialize the GCS client using the service account JSON file
                GCSClient.gcs_client = storage.Client.from_service_account_json(credentials_path)
                GCSClient.gcs_resource = GCSClient.gcs_client
            except exceptions.DefaultCredentialsError as e:
                raise Exception(f"Error connecting to GCS: {e}")
        
        self.gcs_client = GCSClient.gcs_client
        self.gcs_resource = GCSClient.gcs_resource

    def list_buckets(self):
        """ List all buckets in the GCS project """
        try:
            buckets = self.gcs_client.list_buckets()
            for bucket in buckets:
                print(bucket.name)
        except Exception as e:
            raise Exception(f"Failed to list GCS buckets: {e}")

    def get_bucket(self, bucket_name: str):
        """ Get a GCS bucket by name """
        try:
            return self.gcs_client.get_bucket(bucket_name)
        except Exception as e:
            raise Exception(f"Failed to get GCS bucket: {e}")

    def upload_file(self, local_filename: str, bucket_name: str, blob_name: str):
        """ Upload a file to GCS """
        try:
            bucket = self.get_bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(local_filename)
            print(f"File {local_filename} uploaded to {bucket_name}/{blob_name}.")
        except Exception as e:
            raise Exception(f"Failed to upload file to GCS: {e}")

    def download_file(self, bucket_name: str, blob_name: str, local_filename: str):
        """ Download a file from GCS """
        try:
            bucket = self.get_bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.download_to_filename(local_filename)
            print(f"File {blob_name} downloaded to {local_filename}.")
        except Exception as e:
            raise Exception(f"Failed to download file from GCS: {e}")
