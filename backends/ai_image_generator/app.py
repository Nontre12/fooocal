import os, time, json, threading
from bson import ObjectId

from fooocal.diffusers import ImageGeneratorFactory
from fooocal.database import Database
from fooocal.s3 import S3Bucket
from fooocal.broker import Rabbit

def main():
    os.environ["PYTORCH_HIP_ALLOC_CONF"] = "expandable_segments:True"
    os.environ["TORCH_ROCM_AOTRITON_ENABLE_EXPERIMENTAL"] = "1"
    # sleep for available dependency services
    time.sleep(5)

    s3_endpoint = os.environ.get("S3_ENDPOINT", "minio:9000")
    s3_bucket = os.environ.get("S3_BUCKET", "generated-images")
    s3_access_key = os.environ.get("S3_ACCESS_KEY", "")
    s3_secret_key = os.environ.get("S3_SECRET_KEY", "")

    rabbitmq_host = os.environ.get("RABBITMQ_HOST", "rabbitmq")
    rabbitmq_username = os.environ.get("RABBITMQ_USER", "root")
    rabbitmq_password = os.environ.get("RABBITMQ_PASSWORD", "root")

    URI = "mongodb://root:root@mongo:27017/"

    database = Database(
        connection_uri=URI,
        database_name='fooocal',
        collection_name='generated-images'
    )

    s3_bucket = S3Bucket(
        endpoint=s3_endpoint,
        bucket_name=s3_bucket,
        access_key=s3_access_key,
        secret_key=s3_secret_key,
        secure=False,
    )

    rabbitmq = Rabbit(
        hostname=rabbitmq_host,
        username=rabbitmq_username,
        password=rabbitmq_password
    )

    image_generator_factory = ImageGeneratorFactory()
    image_generator = image_generator_factory.get_image_generator(model_name="black-forest-labs/FLUX.1-dev")

    def send_heartbeats():
        """ Continuously sends heartbeats to RabbitMQ to keep the connection alive. """
        while True:
            try:
                rabbitmq.process_data_events()
                time.sleep(30) 
            except Exception as e:
                print(f"Heartbeat thread error: {e}")
                break 

    def prompt(channel, method_frame, properties, body):
        print(f" [x] Received {body}")

        # Parse the JSON string
        try:
            data = json.loads(body)

            object_id = data.get("_id")
            image_file_name = data.get("image_file_name")

            prompt = data.get("prompt")
            width = int(data.get("width", 832))
            height = int(data.get("height", 1216))
            steps = int(data.get("steps", 20))
            guidance_scale = float(data.get("guidance_scale", 7.0))
            seed = int(data.get("seed", 0))


        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return

        if not prompt:
            print("No 'prompt' found in the message body.")
            return

        source_file = "./generated.png"
        destination_file = image_file_name

        object_id = ObjectId(object_id)

        database.save({
            "_id": object_id,
            "status": "IN_PROGRESS"
        })

        out = image_generator.prompt(
            prompt=prompt,
            width=width,
            height=height,
            steps=steps,
            guidance_scale=guidance_scale,
            seed=seed
        )
        
        out.save(source_file)

        s3_bucket.push_object(
            source_file=source_file,
            destination_file=destination_file,
            content_type="image/png",
        )

        if os.path.exists(source_file):
            os.remove(source_file)

        database.save({
            "_id": object_id,
            "status": "DONE"
        })

        channel.basic_ack(delivery_tag=method_frame.delivery_tag)

    heartbeat_thread = threading.Thread(target=send_heartbeats, daemon=True)
    heartbeat_thread.start()

    rabbitmq.consume("generate_ai_image", callback=prompt)


if __name__ == "__main__":
    main()
