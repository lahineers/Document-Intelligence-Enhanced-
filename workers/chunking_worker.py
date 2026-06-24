import json
import pika
from sqlmodel import Session

print("CHUNKING WORKER STARTING", flush=True)

import models

from db import engine
from models.document import Document

from services.minio_service import minio_service
from services.chunking_service import ChunkingService
from services.document_chunk_service import DocumentChunkService
from services.rabbitmq_service import RabbitMQService

from core.settings import settings

import time


credentials = pika.PlainCredentials(
    settings.rabbitmq_user,
    settings.rabbitmq_password
)

while True:

    try:

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=settings.rabbitmq_host,
                port=settings.rabbitmq_port,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=600
            )
        )

        print("RabbitMQ Connected", flush=True)
        break

    except Exception:

        print("Waiting for RabbitMQ...", flush=True)
        time.sleep(5)

channel = connection.channel()

channel.queue_declare(
    queue="document.chunking.queue",
    durable=True
)


def callback(ch, method, properties, body):

    message = json.loads(body)

    document_id = message["document_id"]

    print(
        f"CHUNKING DOCUMENT {document_id}",
        flush=True
    )

    try:

        with Session(engine) as session:

            document = session.get(
                Document,
                document_id
            )

            if not document:
                raise ValueError(
                    f"Document not found: {document_id}"
                )

            markdown_content = (
                minio_service.download_text(
                    document.markdown_object_key
                )
            )

            print(
                f"Downloaded markdown: {document.markdown_object_key}",
                flush=True
            )

            document.processing_status = "chunking"
            session.add(document)
            session.commit()

            chunks = (
                ChunkingService.chunk_document(
                    markdown_content
                )
            )

            DocumentChunkService.create_chunks_for_document(
                document_id,
                chunks,
                session
            )

            document.processing_status = "chunked"

            session.add(document)
            session.commit()

            print(
                f"Created {len(chunks)} chunks",
                flush=True
            )

            rabbitmq_service = RabbitMQService()

            rabbitmq_service.publish_message(
                "document.embedding.queue",
                {
                    "document_id": str(document_id)
                }
            )

            print(
                f"Published embedding job for {document_id}",
                flush=True
            )

            rabbitmq_service.publish_message(
                "document.summary.queue",
                {
                    "document_id": str(document_id)
                }
            )

            print(
                f"Published summary job for {document_id}",
                flush=True
            )

            rabbitmq_service.close()

        ch.basic_ack(
            delivery_tag=method.delivery_tag
        )

        print(
            f"Chunking complete for {document_id}",
            flush=True
        )

    except Exception as e:

        print(
            f"Chunking failed: {e}",
            flush=True
        )

        ch.basic_ack(
            delivery_tag=method.delivery_tag
        )


channel.basic_qos(
    prefetch_count=1
)

channel.basic_consume(
    queue="document.chunking.queue",
    on_message_callback=callback
)

print(
    "Waiting for chunking jobs...",
    flush=True
)

channel.start_consuming()