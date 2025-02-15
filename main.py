from src.pipeline.training_pipeline import TrainPipeline
from src.logger import logging

def main():
    try:
        # Stage 1: Data Ingestion
        STAGE_NAME = "Data Ingestion stage"
        try:
            logging.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
            train_pipeline = TrainPipeline()
            data_ingestion_artifact = train_pipeline.start_data_ingestion()
            logging.info(f"Data Ingestion Completed: {data_ingestion_artifact}")
            logging.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
        except Exception as e:
            logging.exception(f"Error during {STAGE_NAME}")
            raise e

        # Stage 2: Data Validation
        STAGE_NAME = "Data Validation stage"
        try:
            logging.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
            data_validation_artifact = train_pipeline.start_data_validation(data_ingestion_artifact)
            logging.info(f"Data Validation Completed: {data_validation_artifact}")
            logging.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
        except Exception as e:
            logging.exception(f"Error during {STAGE_NAME}")
            raise e

    except Exception as e:
        logging.error(f"Error in training pipeline: {e}")

if __name__ == "__main__":
    main()
