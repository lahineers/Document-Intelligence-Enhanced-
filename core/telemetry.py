from opentelemetry import trace

from opentelemetry.sdk.resources import Resource

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

import logging

from opentelemetry.sdk._logs import (
    LoggerProvider,
    LoggingHandler
)

from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter

from openinference.instrumentation.openai import OpenAIInstrumentor
#from openinference.instrumentation.agno import AgnoInstrumentor


def setup_telemetry():

    resource = Resource.create(
        {
            "service.name": "docintelli-api",
        }
    )

    # Tracing
    trace_provider = TracerProvider(
        resource=resource
    )

    trace_provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(
                endpoint=(
                    "http://host.docker.internal:4318/v1/traces"
                )
            )
        )
    )

    trace.set_tracer_provider(
        trace_provider
    )

    OpenAIInstrumentor().instrument()
   # AgnoInstrumentor().instrument()

    # Logging
    logger_provider = LoggerProvider(
        resource=resource
    )

    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(
            OTLPLogExporter(
                endpoint=(
                    "http://host.docker.internal:4318/v1/logs"
                )
            )
        )
    )

    logging_handler = LoggingHandler(
        level=logging.INFO,
        logger_provider=logger_provider
    )

    root_logger = logging.getLogger()

    root_logger.setLevel(
        logging.INFO
    )

    root_logger.addHandler(
        logging_handler
    )