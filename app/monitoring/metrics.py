from prometheus_client import Counter, Histogram, Gauge, start_http_server

from prometheus_client import REGISTRY

REQUEST_COUNT = Counter(
    "bot_requests_total", 
    "Total requests to bot", 
    ["event_type", "status"],
    registry=REGISTRY
)
RESPONSE_TIME = Histogram(
    "bot_response_time_seconds", 
    "Time spent processing request",
    ["event_type", "status"],
    registry=REGISTRY
)
SERVICE_HEALTH = Gauge(
    "service_health",
    "Health status of services (1 = healthy, 0 = unhealthy)",
    ["service"],
    registry=REGISTRY
)

_metrics_initialized = False

def setup_metrics(port: int = 8001) -> None:
    """Запуск HTTP-эндпойнта с метриками Prometheus."""
    global _metrics_initialized
    if _metrics_initialized:
        return
        
    start_http_server(port)
    _metrics_initialized = True
