from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource  # Add this
from opentelemetry.semconv.resource import ResourceAttributes  # Add this

from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import os
import time
import requests
from requests.exceptions import RequestException
import logging

logger = logging.getLogger(__name__)



# Prometheus metrics
REQUEST_COUNT = Counter(
    "app_request_count_total",
    "Request count by endpoint and status",
    ["endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds",
    "Request latency by endpoint",
    ["endpoint"]
)

ERROR_COUNT = Counter(
    "app_error_count_total",
    "Error count by type",
    ["error_type"]
)

def wait_for_tempo(tempo_host="tempo", tempo_port="3200", max_retries=5, retry_delay=2):
    for i in range(max_retries):
        try:
            response = requests.get(f"http://{tempo_host}:{tempo_port}/ready")
            if response.status_code == 200:
                return True
        except RequestException:
            pass
        time.sleep(retry_delay)
    return False

def setup_monitoring(app):
    # Wait for Tempo to be ready
    if not wait_for_tempo():
        logger.warning("Tempo not available, but continuing anyway...")

    # Create a Resource to identify your service
    resource = Resource.create({
        ResourceAttributes.SERVICE_NAME: "product-api",  # This will be the service name in Tempo
        ResourceAttributes.DEPLOYMENT_ENVIRONMENT: "development"
    })

    # Set up OpenTelemetry tracer
    tracer_provider = TracerProvider(resource=resource)
    otlp_exporter = OTLPSpanExporter(
        endpoint=os.getenv("TEMPO_ENDPOINT", "tempo:4317"),
        insecure=True
    )
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)
    
    # Set the tracer provider
    trace.set_tracer_provider(tracer_provider)
    
    # Initialize FastAPI instrumentation with service name
    FastAPIInstrumentor().instrument_app(
        app,
        tracer_provider=tracer_provider,
        excluded_urls="metrics",
        server_request_hook=lambda span, scope: span.update_name(f"{scope['method']} {scope.get('route_name', '')}")
    )
    
    return trace.get_tracer("fastapi-app")  # Set service name here