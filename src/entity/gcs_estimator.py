from src.cloud_storage.gcp_storage import GoogleCloudStorage
from src.exception import MyException
from src.entity.estimator import MyModel
import sys
from pandas import DataFrame
import pickle


class Proj1Estimator:
    """
    Handles saving, retrieving, and predicting with the model from GCS.
    """

    def __init__(self, bucket_name, model_path):
        self.bucket_name = bucket_name
        self.gcs = GoogleCloudStorage()
        self.model_path = model_path
        self.loaded_model: MyModel = None

    def is_model_present(self, model_path):
        try:
            # Correct 'file_path' to 'blob_name'
            return self.gcs.file_exists(bucket_name=self.bucket_name, blob_name=model_path)
        except MyException as e:
            print(e)
            return False

    def load_model(self) -> MyModel:
        """Load the model from GCS"""
        try:
            local_model_path = f"/tmp/{self.model_path.split('/')[-1]}"  # Example path
            self.gcs.download_file(
                bucket_name=self.bucket_name,
                blob_name=self.model_path,
                local_filename=local_model_path
            )
            with open(local_model_path, "rb") as model_file:
                return pickle.load(model_file)
        except Exception as e:
            raise MyException(e, sys)

        

    def save_model(self, from_file, remove: bool = False) -> None:
        """Save the model to GCS"""
        try:
            # Match parameter name to GCS client expectations
            self.gcs.upload_file(
                local_filename=from_file,  # Changed parameter name
                bucket_name=self.bucket_name,
                blob_name=self.model_path
            )
        except Exception as e:
            raise MyException(e, sys)

    def predict(self, dataframe: DataFrame):
        """Make predictions using the model"""
        try:
            if self.loaded_model is None:
                self.loaded_model = self.load_model()
            return self.loaded_model.predict(dataframe)
        except Exception as e:
            raise MyException(e, sys)
