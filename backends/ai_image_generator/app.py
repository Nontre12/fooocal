import os

os.environ["PYTORCH_HIP_ALLOC_CONF"] = "expandable_segments:True"
os.environ["TORCH_ROCM_AOTRITON_ENABLE_EXPERIMENTAL"] = "1"

import time, uuid, json, pika
import torch
from diffusers import FluxPipeline
from minio import Minio


class S3Bucket:
    def __init__(
        self,
        endpoint: str,
        bucket_name: str,
        access_key: str,
        secret_key: str,
        secure: bool = True,
    ):
        self.endpoint = endpoint
        self.bucket_name = bucket_name
        self.access_key = access_key
        self.secret_key = secret_key
        self.secure = secure

        self.client = Minio(
            endpoint=self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure,
        )

        found = self.client.bucket_exists(bucket_name)
        if not found:
            self.client.make_bucket(bucket_name)

    def push_object(
        self,
        source_file: str,
        destination_file: str,
        content_type="application/octet-stream",
    ):
        self.client.fput_object(
            bucket_name=self.bucket_name,
            object_name=destination_file,
            file_path=source_file,
            content_type=content_type,
        )


class Rabbit:
    def __init__(self, hostname: str, username: str, password: str):
        self.credentials = pika.PlainCredentials(username, password)
        self.conneciton_parameters = pika.ConnectionParameters(
            host=hostname, credentials=self.credentials
        )
        self.connection = pika.BlockingConnection(self.conneciton_parameters)
        self.channel = self.connection.channel()

    def consume(self, queue_name: str, callback: callable):
        self.channel.queue_declare(queue=queue_name)
        self.channel.basic_consume(
            queue=queue_name, on_message_callback=callback, auto_ack=True
        )
        self.channel.start_consuming()


class ImageGenerator:
    def __init__(self):
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()

        self.pipe = FluxPipeline.from_pretrained(
            "black-forest-labs/FLUX.1-dev", torch_dtype=torch.bfloat16
        )
        self.pipe.enable_model_cpu_offload()

    def prompt(self, prompt: str):
        SEED = 0
        GUIDANCE_SCALE = 3.5
        HEIGHT = 1216
        WIDTH = 832
        STEPS = 20

        out = self.pipe(
            prompt=prompt,
            guidance_scale=GUIDANCE_SCALE,
            height=HEIGHT,
            width=WIDTH,
            num_inference_steps=STEPS,
            generator=torch.Generator("cpu").manual_seed(SEED),
        ).images[0]

        return out


def main():
    # sleep for available dependency services
    time.sleep(5)

    s3_endpoint = os.environ.get("S3_ENDPOINT", "minio:9000")
    s3_bucket = os.environ.get(
        "S3_BUCKET", "backend-ai-generated-images"
    )
    s3_access_key = os.environ.get("S3_ACCESS_KEY", "")
    s3_secret_key = os.environ.get("S3_SECRET_KEY", "")

    rabbitmq_host = os.environ.get("RABBITMQ_HOST", "rabbitmq")
    rabbitmq_username = os.environ.get("RABBITMQ_USER", "root")
    rabbitmq_password = os.environ.get("RABBITMQ_PASSWORD", "root")

    s3_bucket = S3Bucket(
        endpoint=s3_endpoint,
        bucket_name=s3_bucket,
        access_key=s3_access_key,
        secret_key=s3_secret_key,
        secure=False,
    )

    rabbitmq = Rabbit(
        hostname=rabbitmq_host, username=rabbitmq_username, password=rabbitmq_password
    )

    image_generator = ImageGenerator()

    def prompt(ch, method, properties, body):
        print(f" [x] Received {body}")

        # Parse the JSON string
        try:
            data = json.loads(body)
            prompt = data.get("prompt")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return

        if not prompt:
            print("No 'prompt' found in the message body.")
            return

        source_file = "./generated.png"
        destination_file_name = uuid.uuid4()
        destination_file = f"{destination_file_name}.png"

        out = image_generator.prompt(prompt=prompt)
        out.save(source_file)

        s3_bucket.push_object(
            source_file=source_file,
            destination_file=destination_file,
            content_type="image/png",
        )

        if os.path.exists(source_file):
            os.remove(source_file)

    rabbitmq.consume("generate_ai_image", callback=prompt)


if __name__ == "__main__":
    main()
