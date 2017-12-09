from pymongo import MongoClient

client = MongoClient()
test_db = client.SEEHEAR

collection = test_db.hot100.find()
for record in collection:
    print record