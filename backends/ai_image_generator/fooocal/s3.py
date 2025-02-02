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