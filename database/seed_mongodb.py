"""Load sample MongoDB student profiles from mongodb_seed.json."""
import json
from pathlib import Path
from pymongo import MongoClient

ROOT = Path(__file__).resolve().parents[1]
config_file = ROOT / "config.json"
config = json.loads(config_file.read_text(encoding="utf-8"))
mongo = config["mongodb"]
client = MongoClient(mongo.get("uri", "mongodb://localhost:27017"))
collection = client[mongo.get("database", "student_pipeline")][mongo.get("collection", "student_profiles")]
docs = json.loads((ROOT / "database/mongodb_seed.json").read_text(encoding="utf-8"))
collection.delete_many({})
if docs:
    collection.insert_many(docs)
collection.create_index("student_id", unique=True)
print(f"Inserted {len(docs)} MongoDB student profiles.")
client.close()
