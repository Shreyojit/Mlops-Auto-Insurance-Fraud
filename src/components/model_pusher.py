import sys
import os
from src.entity.artifact_entity import ModelEvaluationArtifact, ModelPusherArtifact
from src.entity.config_entity import ModelPusherConfig
from src.exception import MyException
from src.cloud_storage.gcp_storage import GoogleCloudStorage
from src.logger import logging


class ModelPusher:
    def __init__(self, model_pusher_config: ModelPusherConfig,
                 model_evaluation_artifact: ModelEvaluationArtifact):
        self.model_pusher_config = model_pusher_config
        self.model_evaluation_artifact = model_evaluation_artifact
        self.gcs = GoogleCloudStorage()

        logging.info(f"{'>>' * 10} Model Pusher Initialized {'<<' * 10}")

    def push_model_to_gcs(self) -> str:
        try:
            logging.info("Starting model upload to GCS")

            trained_model_path = self.model_evaluation_artifact.trained_model_path
            gcs_model_path = self.model_pusher_config.gcs_model_path

            logging.debug(f"Local model path: {trained_model_path}")
            logging.debug(f"Target GCS path: gs://{self.model_pusher_config.bucket_name}/{gcs_model_path}")

            # CORRECTED PARAMETER NAME HERE (local_filename instead of local_file_path)
            self.gcs.upload_file(
                local_filename=trained_model_path,  # Changed parameter name
                bucket_name=self.model_pusher_config.bucket_name,
                blob_name=gcs_model_path
            )

            logging.info("Model successfully uploaded to GCS")
            return gcs_model_path

        except Exception as e:
            error_detail = MyException(e, sys)
            logging.error(f"Error uploading model to GCS: {error_detail}")
            raise error_detail

    def initiate_model_pusher(self) -> ModelPusherArtifact:
        try:
            if self.model_evaluation_artifact.is_model_accepted:
                logging.info("Model accepted in evaluation. Proceeding to push.")
                gcs_model_path = self.push_model_to_gcs()
            else:
                logging.info("Model rejected in evaluation. Skipping push.")
                gcs_model_path = None

            logging.info("Preparing ModelPusherArtifact")
            pusher_artifact = ModelPusherArtifact(
                pushed_to_gcs=self.model_evaluation_artifact.is_model_accepted,
                gcs_model_path=gcs_model_path
            )

            logging.info(f"Model Pusher Artifact: {pusher_artifact}")
            return pusher_artifact

        except Exception as e:
            error_detail = MyException(e, sys)
            logging.error(f"Error in model pusher: {error_detail}")
            raise error_detail
