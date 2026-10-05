import os

import pandas as pd
from pymongo import MongoClient


def get_mongodb_client(config):
    """Create a MongoDB client using local configuration/environment variables."""
    uri = os.getenv("MONGO_URI", config.get("uri", "mongodb://localhost:27017"))
    return MongoClient(uri, serverSelectionTimeoutMS=int(config.get("server_selection_timeout_ms", 5000)))


def extract_mongodb(config, logger):
    """Read student profile documents from the local MongoDB database."""
    logger.info("MongoDB extraction started")
    client = get_mongodb_client(config)
    try:
        db_name = os.getenv("MONGO_DB", config.get("database", "student_pipeline"))
        collection_name = os.getenv("MONGO_COLLECTION", config.get("collection", "student_profiles"))
        collection = client[db_name][collection_name]
        documents = list(collection.find({}, {"_id": 0}))
        df = pd.DataFrame(documents)
        logger.info("MongoDB records: %s", len(df))
        return df
    finally:
        client.close()
