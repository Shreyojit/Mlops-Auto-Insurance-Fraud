from src.pipeline.training_pipeline import TrainPipeline
from src.logger import logging

def main():
    try:
        train_pipeline = TrainPipeline()
        
        # Stage 1: Data Ingestion
        STAGE_NAME = "Data Ingestion Stage"
        try:
            logging.info(f">>>>>> {STAGE_NAME} started <<<<<<")
            data_ingestion_artifact = train_pipeline.start_data_ingestion()
            logging.info(f"{STAGE_NAME} Completed: {data_ingestion_artifact}")
            logging.info(f">>>>>> {STAGE_NAME} completed <<<<<<\n\nx==========x")
        except Exception as e:
            logging.exception(f"Error during {STAGE_NAME}")
            raise e

        # Stage 2: Data Validation
        STAGE_NAME = "Data Validation Stage"
        try:
            logging.info(f">>>>>> {STAGE_NAME} started <<<<<<")
            data_validation_artifact = train_pipeline.start_data_validation(data_ingestion_artifact)
            logging.info(f"{STAGE_NAME} Completed: {data_validation_artifact}")
            logging.info(f">>>>>> {STAGE_NAME} completed <<<<<<\n\nx==========x")
        except Exception as e:
            logging.exception(f"Error during {STAGE_NAME}")
            raise e

        # Stage 3: Data Transformation
        STAGE_NAME = "Data Transformation Stage"
        try:
            logging.info(f">>>>>> {STAGE_NAME} started <<<<<<")
            data_transformation_artifact = train_pipeline.start_data_transformation(
                data_ingestion_artifact=data_ingestion_artifact,
                data_validation_artifact=data_validation_artifact
            )
            logging.info(f"{STAGE_NAME} Completed: {data_transformation_artifact}")
            logging.info(f">>>>>> {STAGE_NAME} completed <<<<<<\n\nx==========x")
        except Exception as e:
            logging.exception(f"Error during {STAGE_NAME}")
            raise e
        
        # Stage 4: Model Training
        STAGE_NAME = "Model Training Stage"
        try:
            logging.info(f">>>>>> {STAGE_NAME} started <<<<<<")
            model_trainer_artifact = train_pipeline.start_model_trainer(data_transformation_artifact)
            logging.info(f"{STAGE_NAME} Completed: {model_trainer_artifact}")
            logging.info(f">>>>>> {STAGE_NAME} completed <<<<<<\n\nx==========x")
        except Exception as e:
            logging.exception(f"Error during {STAGE_NAME}")
            raise e

    except Exception as e:
        logging.error(f"Training pipeline failed: {e}")

if __name__ == "__main__":
    main()
