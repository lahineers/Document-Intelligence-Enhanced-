from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str

    upload_dir: str = "storage/uploads"

    embedding_model: str = "nvidia/embed-v1"

    llm_model: str = "nvidia/nemotron-3-ultra-550b-a55b"

    nvidia_api_key: str

    chunk_size: int = 1000

    chunk_overlap: int = 200

    minio_endpoint: str

    minio_access_key: str

    minio_secret_key: str

    minio_bucket: str

    minio_secure: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()