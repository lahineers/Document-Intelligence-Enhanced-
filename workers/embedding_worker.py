import json
import pika
from sqlmodel import Session

print("EMBEDDING WORKER STARTING", flush=True)

import models

from models.document import Document

from db import engine

from services.chunk_embedding_service import (
    ChunkEmbeddingService
)

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

        print(
            "RabbitMQ Connected",
            flush=True
        )

        break

    except Exception:

        print(
            "Waiting for RabbitMQ...",
            flush=True
        )

        time.sleep(5)

channel = connection.channel()

channel.queue_declare(
    queue="document.embedding.queue",
    durable=True
)


def callback(
    ch,
    method,
    properties,
    body
):

    message = json.loads(body)

    document_id = message["document_id"]

    print(
        f"EMBEDDING DOCUMENT {document_id}",
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

            document.processing_status = (
                "embedding"
            )

            session.add(document)
            session.commit()

            embeddings = (
                ChunkEmbeddingService
                .create_embeddings_for_document(
                    document_id,
                    session
                )
            )

            document.processing_status = (
                "completed"
            )

            session.add(document)
            session.commit()

            print(
                f"Created {len(embeddings)} embeddings",
                flush=True
            )

        ch.basic_ack(
            delivery_tag=method.delivery_tag
        )

        print(
            f"Embedding complete for {document_id}",
            flush=True
        )

    except Exception as e:

        print(
            f"Embedding failed: {e}",
            flush=True
        )

        try:

            with Session(engine) as session:

                document = session.get(
                    Document,
                    document_id
                )

                if document:

                    document.processing_status = (
                        "failed"
                    )

                    session.add(document)
                    session.commit()

        except Exception:
            pass

        ch.basic_ack(
            delivery_tag=method.delivery_tag
        )


channel.basic_qos(
    prefetch_count=1
)

channel.basic_consume(
    queue="document.embedding.queue",
    on_message_callback=callback
)

print(
    "Waiting for embedding jobs...",
    flush=True
)

channel.start_consuming()