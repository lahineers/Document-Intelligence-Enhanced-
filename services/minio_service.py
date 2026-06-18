from minio import Minio

from core.settings import settings


class MinioService:

    def __init__(self):
        self.client = Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure
        )

        self.bucket = settings.minio_bucket
    
    def upload_file(self, file_path: str, object_key: str):
        self.client.fput_object(
            bucket_name=self.bucket,
            object_name=object_key,
            file_path=file_path
        )

    def download_file(self, object_key: str, destination_path: str):
        self.client.fget_object(
            bucket_name=self.bucket,
            object_name=object_key,
            file_path=destination_path
        )