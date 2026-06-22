import json
import pika

from core.settings import settings


class RabbitMQService:

    def __init__(self):

        credentials = pika.PlainCredentials(
            settings.rabbitmq_user,
            settings.rabbitmq_password
        )

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=settings.rabbitmq_host,
                port=settings.rabbitmq_port,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=600
            )
        )

        self.channel = self.connection.channel()

        self.channel.queue_declare(
            queue="document.extraction.queue",
            durable=True
        )
        self.channel.queue_declare(
            queue="document.chunking.queue",
            durable=True
        )

        self.channel.queue_declare(
            queue="document.embedding.queue",
            durable=True
        )
        self.channel.queue_declare(
            queue="document.summary.queue",
            durable=True
        )


    def publish_message(
        self,
        queue_name: str,
        message: dict
    ):

        self.channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2
            )
        )

    def close(self):
        self.connection.close()
