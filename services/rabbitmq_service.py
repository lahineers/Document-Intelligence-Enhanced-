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
                credentials=credentials
            )
        )

        self.channel = self.connection.channel()

        self.channel.queue_declare(
            queue="document.extraction.queue",
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


rabbitmq_service=RabbitMQService()