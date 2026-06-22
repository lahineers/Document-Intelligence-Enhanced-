import pika
import json

credentials = pika.PlainCredentials(
    "Nihal",
    "Nihal373707"
)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="localhost",
        port=5672,
        credentials=credentials,
        heartbeat=600,
        blocked_connection_timeout=600
    )
)

channel = connection.channel()

channel.basic_publish(
    exchange="",
    routing_key="document.extraction.queue",
    body=json.dumps({
        "document_id": "740a3d48-ce2e-4f9b-8728-ce05290dea99"
    })
)

print("Published")
connection.close()