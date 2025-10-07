# MongoDB Database Inspection Commands

## Option 1: Using Python Script
```bash
python check-db.py
```

## Option 2: Using MongoDB Shell (if you have mongo CLI installed)
```bash
# Connect to MongoDB
mongo

# Switch to your database
use admin

# Show collections
show collections

# Count documents in meds collection
db.meds.count()

# Show all documents
db.meds.find().pretty()

# Show first 5 documents
db.meds.find().limit(5).pretty()

# Find specific documents (example)
db.meds.find({"Name": "Abdullah"}).pretty()

# Show only specific fields
db.meds.find({}, {"Name": 1, "Age": 1}).pretty()

# Get collection stats
db.meds.stats()
```

## Option 3: Using MongoDB Compass (GUI)
1. Download MongoDB Compass (free GUI tool)
2. Connect to: mongodb://localhost:27017
3. Browse your databases and collections visually

## Option 4: Quick Python One-liners
```python
# Quick check in Python
from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017/")
db = client["admin"]
collection = db["meds"]

# Count documents
print(f"Total documents: {collection.count_documents({})}")

# Show all documents
for doc in collection.find():
    print(doc)

# Show just names
for doc in collection.find():
    print(doc.get("Name", "No name field"))
```