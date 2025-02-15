import os
import sys
import pymongo
import certifi
from dotenv import load_dotenv

from src.exception import MyException
from src.logger import logging
from src.constants import DATABASE_NAME, MONGODB_URL_KEY

# Load environment variables from .env file
load_dotenv()

# Load the certificate authority file to avoid timeout errors when connecting to MongoDB
ca = certifi.where()


class MongoDBClient:
    """
    MongoDBClient handles the connection to the MongoDB database.

    Attributes:
    ----------
    client : MongoClient
        A shared MongoClient instance.
    database : Database
        The specific database instance that MongoDBClient connects to.

    Methods:
    -------
    __init__(database_name: str) -> None
        Initializes the MongoDB connection using the given database name.
    get_mongo_url() -> str
        Retrieves the MongoDB URL from environment variables.
    """

    client = None  # Shared MongoClient instance

    @staticmethod
    def get_mongo_url() -> str:
        """
        Retrieves MongoDB connection URL from environment variables.

        Returns:
        -------
        str
            The MongoDB URL.

        Raises:
        ------
        Exception
            If the environment variable for the MongoDB URL is not set.
        """
        mongo_db_url = os.getenv(MONGODB_URL_KEY)
        if not mongo_db_url:
            logging.error(f"Environment variable '{MONGODB_URL_KEY}' is not set.")
            raise Exception(f"Environment variable '{MONGODB_URL_KEY}' is not set.")
        return mongo_db_url

    def __init__(self, database_name: str = DATABASE_NAME) -> None:
        """
        Initializes a connection to the MongoDB database.

        Parameters:
        ----------
        database_name : str, optional
            Name of the MongoDB database to connect to. Default is set by DATABASE_NAME constant.

        Raises:
        ------
        MyException
            If there is an issue connecting to MongoDB.
        """
        try:
            if MongoDBClient.client is None:
                # Get MongoDB URL and establish connection
                mongo_db_url = self.get_mongo_url()
                MongoDBClient.client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)
                logging.info("MongoDB connection established successfully.")

            # Use the shared client instance
            self.client = MongoDBClient.client
            self.database = self.client[database_name]
            self.database_name = database_name
            logging.info(f"Connected to MongoDB database: {database_name}")

        except Exception as e:
            logging.error(f"Failed to connect to MongoDB: {str(e)}")
            raise MyException(e, sys)
