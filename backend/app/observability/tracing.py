from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()

# Configure tracer
provider = TracerProvider()
processor = BatchSpanProcessor(
    JaegerExporter(
        agent_host_name="jaeger",
        agent_port=6831,
    )
)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("paios")


def instrument_app(app):
    FastAPIInstrumentor.instrument_app(app)
    logger.info("OpenTelemetry instrumentation enabled")
