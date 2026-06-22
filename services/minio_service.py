from minio import Minio

from core.settings import settings
 
from io import BytesIO

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


    def upload_bytes(self, data: bytes, object_key: str, content_type: str):
        self.client.put_object(
            bucket_name=self.bucket,
            object_name=object_key,
            data=BytesIO(data),
            length=len(data),
            content_type=content_type
        )

    def download_bytes(self, object_key: str) -> bytes:
        response = self.client.get_object(
            bucket_name=self.bucket,
            object_name=object_key
        )

        try:
            return response.read()

        finally:
            response.close()
            response.release_conn()


    def download_text(self, object_key: str) -> str:
        return (
            self.download_bytes(
                object_key
            )
            .decode("utf-8")
        )

    
    def upload_text(self, text: str, object_key: str):
        self.upload_bytes(
            data=text.encode("utf-8"),
            object_key=object_key,
            content_type="text/markdown"
        )


minio_service = MinioService()