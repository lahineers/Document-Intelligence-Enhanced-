import json
import pika
import time

from sqlmodel import Session

print(
    "SUMMARY WORKER STARTING",
    flush=True
)

import models

from db import engine
from models.document import Document

from services.minio_service import (
    minio_service
)

from services.document_summary_service import (
    DocumentSummaryService
)

from core.settings import settings


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
    queue="document.summary.queue",
    durable=True
)


def callback(
    ch,
    method,
    properties,
    body
):

    message = json.loads(body)

    document_id = (
        message["document_id"]
    )

    print(
        f"SUMMARY DOCUMENT {document_id}",
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
                f"Downloaded markdown: "
                f"{document.markdown_object_key}",
                flush=True
            )

            DocumentSummaryService.generate_summary(
                document_id,
                markdown_content,
                session
            )

            print(
                f"Summary created for {document_id}",
                flush=True
            )

        ch.basic_ack(
            delivery_tag=method.delivery_tag
        )

    except Exception as e:

        print(
            f"Summary failed: {e}",
            flush=True
        )

        try:
            ch.basic_ack(
                delivery_tag=method.delivery_tag
            )

        except Exception as ack_error:

            print(
                f"Ack failed: {ack_error}",
                flush=True
            )


channel.basic_qos(
    prefetch_count=1
)

channel.basic_consume(
    queue="document.summary.queue",
    on_message_callback=callback
)

print(
    "Waiting for summary jobs...",
    flush=True
)

channel.start_consuming()