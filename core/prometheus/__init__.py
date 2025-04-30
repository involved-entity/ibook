from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter("fastapi_request_count", "Total number of requests", ["method", "endpoint", "http_status"])

REQUEST_LATENCY = Histogram("fastapi_request_latency_seconds", "Request latency in seconds", ["method", "endpoint"])
