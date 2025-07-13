from prometheus_client import Counter, Histogram, start_http_server

REQUEST_COUNT = Counter(
    "bot_requests_total", "Total requests to bot", ["status"]
)
RESPONSE_TIME = Histogram(
    "bot_response_time_seconds", "Time spent processing request"
)


def setup_metrics(port: int = 8001) -> None:
    """Запуск HTTP-эндпойнта с метриками Prometheus."""
    start_http_server(port)
