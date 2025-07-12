from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter("bot_requests_total", "Total bot requests", ["status"])
RESPONSE_TIME = Histogram("bot_response_time_seconds", "Bot response time")
