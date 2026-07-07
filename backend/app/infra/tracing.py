"""Configuracao de tracing com OpenTelemetry.

Fornece instrumentacao para FastAPI e HTTP, com exportacao
via console (dev) ou OTLP (producao com Jaeger/Zipkin).

Uso (feito automaticamente em app/main.py):
    setup_tracing(service_name="rag-api", otlp_endpoint=None)
"""

import logging
from typing import Optional

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

logger = logging.getLogger(__name__)


class TracingManager:
    """Gerencia a configuracao de tracing da aplicacao.

    Attributes:
        service_name: Nome do servico para identificacao nos spans.
        otlp_endpoint: URL do collector OTLP (ex: http://jaeger:4318/v1/traces).
            Se None, usa ConsoleSpanExporter (dev).
    """

    def __init__(
        self,
        service_name: str = "rag-api",
        otlp_endpoint: Optional[str] = None,
    ):
        self._service_name = service_name
        self._otlp_endpoint = otlp_endpoint
        self._provider: Optional[TracerProvider] = None

    # ── API publica ─────────────────────────────────────────────────

    def setup(self) -> None:
        """Inicializa o tracing: provider, exporters e instrumentacao."""
        if self._provider is not None:
            logger.warning("Tracing ja foi inicializado")
            return

        resource = Resource(attributes={SERVICE_NAME: self._service_name})
        self._provider = TracerProvider(resource=resource)

        # Exportador padrao (console)
        self._provider.add_span_processor(
            BatchSpanProcessor(ConsoleSpanExporter())
        )

        # Exportador OTLP (se configurado)
        if self._otlp_endpoint:
            logger.info(
                "OTLP exporter configurado para %s", self._otlp_endpoint
            )
            self._provider.add_span_processor(
                BatchSpanProcessor(
                    OTLPSpanExporter(endpoint=self._otlp_endpoint)
                )
            )
        else:
            logger.info(
                "OTLP endpoint nao configurado — usando console exporter"
            )

        trace.set_tracer_provider(self._provider)
        logger.info(
            "Tracing inicializado para servico: %s", self._service_name
        )

    def instrument_app(self, app) -> None:
        """Instrumenta a aplicacao FastAPI."""
        FastAPIInstrumentor.instrument_app(app)

    def instrument_httpx(self) -> None:
        """Instrumenta o cliente HTTP (httpx)."""
        HTTPXClientInstrumentor().instrument()

    def get_tracer(self) -> trace.Tracer:
        """Retorna um tracer para criacao de spans manuais."""
        return trace.get_tracer(self._service_name)

    def shutdown(self) -> None:
        """Finaliza o tracing (exporta spans pendentes)."""
        if self._provider:
            self._provider.shutdown()
            logger.info("Tracing finalizado")

    @classmethod
    def create_span(
        cls, name: str, attributes: Optional[dict] = None
    ) -> trace.Span:
        """Cria e retorna um span manual (para uso como decorator/CM).

        Uso:
            with TracingManager.create_span("meu-span") as span:
                ...
        """
        tracer = trace.get_tracer(__name__)
        return tracer.start_as_current_span(name, attributes=attributes)


# Instancia global (configurada em main.py)
tracing_manager = TracingManager()
