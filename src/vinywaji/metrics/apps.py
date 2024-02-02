from django.apps import AppConfig
from django.conf import settings
from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource


class MetricsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "vinywaji.metrics"
    label = "vinywaji_metrics"

    def ready(self):
        super().ready()
        self.init_instrumentation()

    def init_instrumentation(self):
        from vinywaji.metrics import async_instruments

        resource = Resource(
            attributes={
                SERVICE_NAME: "vinywaji",
                SERVICE_VERSION: settings.VERSION,
            }
        )
        metric_reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(),
            export_interval_millis=15_000,
        )
        meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
        metrics.set_meter_provider(meter_provider)
        DjangoInstrumentor().instrument()
        async_instruments.create_async_instruments()
