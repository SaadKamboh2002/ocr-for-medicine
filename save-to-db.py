from pymongo import MongoClient
from meds import extract_medicines_from_image

# Connect to local MongoDB
client = MongoClient("mongodb://localhost:27017/")

# selecting the ocr database
db = client["admin"]

users_collection = db["meds"]

# Insert a single document
# user = extract_medicines_from_image("test.jpg")
# user = { 'Name': 'Abdullah', 'Age': 59, 'City': 'Karachi' }

# insert_result = users_collection.insert_one(user)
# print("Inserted document ID:", insert_result.inserted_id)

for item in users_collection.find():
...     print(item["Name"])