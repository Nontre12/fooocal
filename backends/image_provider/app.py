import os, pika, json, uuid
from flask import Flask, jsonify, request
from flask_compress import Compress
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)
Compress(app)

MONGO_URI = "mongodb://root:root@mongo:27017/"
MONGO_DATABASE = "fooocal"
MONGO_COLLECTION = "generated-images"

rabbitmq_host = os.environ.get("RABBITMQ_HOST", "rabbitmq")
rabbitmq_username = os.environ.get("RABBITMQ_USER", "root")
rabbitmq_password = os.environ.get("RABBITMQ_PASSWORD", "root")

class Rabbit:
    def __init__(self, hostname: str, username: str, password: str):
        self.credentials = pika.PlainCredentials(username, password)
        self.connection_parameters = pika.ConnectionParameters(
            host=hostname, credentials=self.credentials
        )
        self.connection = pika.BlockingConnection(self.connection_parameters)
        self.channel = self.connection.channel()

    def produce(self, queue_name: str, body):
        self.channel.queue_declare(queue=queue_name)
        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=body
        )


@app.route("/images", methods=["GET"])
def get_images():
    with MongoClient(MONGO_URI) as client:
        database = client[MONGO_DATABASE]
        collection = database[MONGO_COLLECTION]

        docs = [
            {
                "_id": str(doc["_id"]),
                "image_file_name": doc["image_file_name"],
                #"prompt": doc["prompt"],
                "status": doc.get("status", "DONE")
            }
            for doc in collection.find({}, {}).sort("_id", -1)
        ]

    return jsonify(docs)

@app.route("/images", methods=["POST"])
def post_image():
    data = request.get_json()

    prompt = data["prompt"]
    width = int(data.get("width", 832))
    height = int(data.get("height", 1216))
    steps = int(data.get("steps", 20))
    guidance_scale = float(data.get("guidance_scale", 7.0))
    seed = int(data.get("seed", 0))

    image_file_name = str(uuid.uuid4()) + '.png'

    with MongoClient(MONGO_URI) as client:
        database = client[MONGO_DATABASE]
        collection = database[MONGO_COLLECTION]

        record_id = collection.insert_one(
            {
                "image_file_name": image_file_name,
                "prompt": prompt,
                "width": width,
                "height": height,
                "steps": steps,
                "guidance_scale": guidance_scale,
                "seed": seed,
                "status": "QUEUED"
            }
        ).inserted_id

    rabbitmq = Rabbit(
        hostname=rabbitmq_host,
        username=rabbitmq_username,
        password=rabbitmq_password
    )

    rabbitmq.produce(
        'generate_ai_image',
        json.dumps({
            "_id": str(record_id),
            "image_file_name": image_file_name,
            "prompt": prompt,
            "width": width,
            "height": height,
            "steps": steps,
            "guidance_scale": guidance_scale,
            "seed": seed,
            "status": "QUEUED"
        })
    )

    return jsonify({
        "success": True,
        "message": "Image generation queued"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
