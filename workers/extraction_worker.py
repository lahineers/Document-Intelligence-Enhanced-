import json
import pika
from sqlmodel import Session

print("WORKER STARTING", flush=True)

import models
from db import engine
from services.ingestion_service import IngestionService

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

    except Exception as e:

        print("Waiting for RabbitMQ...", flush=True)
        print(e)

        time.sleep(5)

channel = connection.channel()

channel.queue_declare(
    queue="document.extraction.queue",
    durable=True
)


def callback(ch, method, properties, body):

    print("MESSAGE RECEIVED", flush=True)

    message = json.loads(body)

    document_id = message["document_id"]

    print(f"DOC ID: {document_id}", flush=True)

    try:

        print("STARTING INGESTION", flush=True)

        with Session(engine) as session:

            IngestionService.ingest_document(
                document_id,
                session
            )

        print("INGESTION COMPLETE", flush=True)

        ch.basic_ack(
            delivery_tag=method.delivery_tag
        )

        print(
            f"Successfully processed {document_id}",
            flush=True
        )

    except Exception as e:

        print(
            f"Processing failed: {e}",
            flush=True
        )

channel.basic_qos(
    prefetch_count=1
)

channel.basic_consume(
    queue="document.extraction.queue",
    on_message_callback=callback
)

print("Waiting for messages...")

channel.start_consuming()