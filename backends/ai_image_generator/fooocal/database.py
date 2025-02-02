from pymongo import MongoClient

class Database:
    def __init__(self, connection_uri: str, database_name: str, collection_name: str):
        self.connection = MongoClient(connection_uri)
        self.database = self.connection[database_name]
        self.collection = self.database[collection_name]

    def save(self, data):
        self.collection.update_one(
            {"_id": data["_id"]},
            {"$set": data},
            upsert=True
        )
