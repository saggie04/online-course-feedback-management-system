from dotenv import load_dotenv
from pymongo import MongoClient
import os

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]

col = db["test_collection"]
res = col.insert_one({"hello": "world"})
print("Inserted id:", res.inserted_id)
print("Found:", col.find_one({"_id": res.inserted_id}))
