from services.minio_service import MinioService

minio_service = MinioService()

minio_service.download_file(
    object_key="raw/test.pdf",
    destination_path="storage/downloaded.pdf"
)

print("Download successful")