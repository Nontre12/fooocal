from flask import Flask, jsonify
from pymongo import MongoClient
from bson import ObjectId  # Required to convert ObjectId to string

app = Flask(__name__)

@app.route("/images")
def example():
    with MongoClient("mongodb://root:root@mongo:27017/") as client:
        database = client["fooocal"]
        collection = database["generated-images"]

        # Convert _id to string for JSON serialization
        docs = [
            {"_id": str(doc["_id"]), "image_file_name": doc["image_file_name"]}
            for doc in collection.find({}, {"_id": 1, "image_file_name": 1}).sort("_id", -1)
        ]

    return jsonify(docs)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
