from google.cloud import storage
from io import StringIO
from typing import Union, List
import os
import sys
import logging
import pickle
import pandas as pd
from src.exception import MyException

class GoogleCloudStorage:
    """
    A class for interacting with Google Cloud Storage, providing methods for file management, 
    data uploads, and data retrieval in GCS buckets.
    """

    def __init__(self):
        """
        Initializes the GoogleCloudStorage instance with a GCS client.
        """
        self.client = storage.Client()

    def bucket_exists(self, bucket_name: str) -> bool:
        """
        Checks if a specified GCS bucket exists.

        Args:
            bucket_name (str): Name of the GCS bucket.

        Returns:
            bool: True if the bucket exists, False otherwise.
        """
        try:
            self.client.get_bucket(bucket_name)
            return True
        except Exception:
            return False

    def get_bucket(self, bucket_name: str):
        """
        Retrieves the GCS bucket object.
        """
        return self.client.bucket(bucket_name)

    def file_exists(self, bucket_name: str, blob_name: str) -> bool:
        """
        Checks if a file exists in the specified GCS bucket.

        Args:
            bucket_name (str): Name of the GCS bucket.
            blob_name (str): Name of the file in GCS.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        return blob.exists()

    def upload_file(self, local_filename: str, bucket_name: str, blob_name: str, remove: bool = True):
        """
        Uploads a local file to GCS with an optional file deletion.

        Args:
            local_filename (str): Path to the local file.
            bucket_name (str): Name of the GCS bucket.
            blob_name (str): Destination path in GCS.
            remove (bool, optional): Whether to remove the local file after upload. Defaults to True.
        """
        bucket = self.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(local_filename)
        logging.info(f"Uploaded {local_filename} to {bucket_name}/{blob_name}")

        if remove:
            os.remove(local_filename)
            logging.info(f"Removed local file {local_filename}")

    def download_file(self, bucket_name: str, blob_name: str, local_filename: str):
        """
        Downloads a file from GCS to a local path.

        Args:
            bucket_name (str): Name of the GCS bucket.
            blob_name (str): File path in GCS.
            local_filename (str): Local file path to save the downloaded file.
        """
        bucket = self.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.download_to_filename(local_filename)
        logging.info(f"Downloaded {bucket_name}/{blob_name} to {local_filename}")

    def upload_dataframe_as_csv(self, df: pd.DataFrame, bucket_name: str, blob_name: str):
        """
        Uploads a pandas DataFrame as a CSV file to GCS.

        Args:
            df (pd.DataFrame): DataFrame to upload.
            bucket_name (str): Name of the GCS bucket.
            blob_name (str): Destination path in GCS.
        """
        bucket = self.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        blob.upload_from_string(csv_buffer.getvalue(), content_type='text/csv')
        logging.info(f"Uploaded DataFrame to {bucket_name}/{blob_name}")

    def read_csv_from_gcs(self, bucket_name: str, blob_name: str) -> pd.DataFrame:
        """
        Reads a CSV file from GCS and converts it to a DataFrame.

        Args:
            bucket_name (str): Name of the GCS bucket.
            blob_name (str): File path in GCS.

        Returns:
            pd.DataFrame: DataFrame containing the CSV data.
        """
        bucket = self.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        data = blob.download_as_text()
        return pd.read_csv(StringIO(data))

    def load_model(self, model_path: str, bucket_name: str) -> object:
        """Load the model from GCS"""
        try:
            # Assuming self.gcs refers to the current instance, so we use self.load_model
            local_model_path = self.download_file(model_path, bucket_name)  # Corrected method call
            with open(local_model_path, "rb") as model_file:
                return pickle.load(model_file)
        except Exception as e:
            raise MyException(e, sys)

    def save_model(self, model: object, bucket_name: str, model_path: str):
        """
        Saves a serialized model to GCS.

        Args:
            model (object): The model to save.
            bucket_name (str): Name of the GCS bucket.
            model_path (str): Destination path in GCS.
        """
        bucket = self.get_bucket(bucket_name)
        blob = bucket.blob(model_path)
        model_bytes = pickle.dumps(model)
        blob.upload_from_string(model_bytes)
        logging.info(f"Model saved to {bucket_name}/{model_path}")
