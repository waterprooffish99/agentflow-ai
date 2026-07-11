import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import DefaultDict, Optional

import structlog
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.celery import CeleryInstrumentor

from app.core.config import settings

logger = structlog.get_logger()

@dataclass
class ObservabilityStore:
    request_count: int = 0
    error_count: int = 0
    total_request_latency_ms: float = 0.0
    route_hits: DefaultDict[str, int] = field(default_factory=lambda: defaultdict(int))
    route_latency_ms: DefaultDict[str, float] = field(default_factory=lambda: defaultdict(float))
    ai_requests: int = 0
    ai_tokens_prompt: int = 0
    ai_tokens_completion: int = 0

    def track_request(self, route: str, latency_ms: float, is_error: bool) -> None:
        self.request_count += 1
        self.total_request_latency_ms += latency_ms
        self.route_hits[route] += 1
        self.route_latency_ms[route] += latency_ms
        if is_error:
            self.error_count += 1

    def track_ai_usage(self, prompt_tokens: int = 0, completion_tokens: int = 0) -> None:
        self.ai_requests += 1
        self.ai_tokens_prompt += max(prompt_tokens, 0)
        self.ai_tokens_completion += max(completion_tokens, 0)

    def snapshot(self) -> dict:
        avg_latency = (
            self.total_request_latency_ms / self.request_count if self.request_count else 0.0
        )
        error_rate = self.error_count / self.request_count if self.request_count else 0.0
        return {
            "requests_total": self.request_count,
            "errors_total": self.error_count,
            "error_rate": round(error_rate, 6),
            "avg_latency_ms": round(avg_latency, 2),
            "ai_requests_total": self.ai_requests,
            "ai_prompt_tokens": self.ai_tokens_prompt,
            "ai_completion_tokens": self.ai_tokens_completion,
            "routes": {
                route: {
                    "hits": hits,
                    "avg_latency_ms": round(self.route_latency_ms[route] / hits, 2) if hits else 0.0,
                }
                for route, hits in self.route_hits.items()
            },
            "timestamp": time.time(),
        }


metrics = ObservabilityStore()

def setup_tracing(app=None, engine=None):
    """Initialize OpenTelemetry tracing."""
    if not settings.otel_enabled:
        return

    resource = Resource(attributes={
        SERVICE_NAME: "agentflow-api",
        "environment": settings.app_env,
    })

    provider = TracerProvider(resource=resource)
    
    if settings.otel_exporter_otlp_endpoint:
        processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint))
        provider.add_span_processor(processor)

    trace.set_tracer_provider(provider)

    if app:
        FastAPIInstrumentor.instrument_app(app)
    if engine:
        SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)
    
    RedisInstrumentor().instrument()
    CeleryInstrumentor().instrument()
    
    logger.info("tracing_initialized", endpoint=settings.otel_exporter_otlp_endpoint)

def get_tracer(name: str):
    return trace.get_tracer(name)
