from prometheus_client import Counter, Histogram

CHAT_REQUESTS = Counter(
    "chat_requests_total",
    "Total chat requests",
    ["agent"],
)

CHAT_ERRORS = Counter(
    "chat_errors_total",
    "Total chat errors",
    ["error_type"],
)

CHAT_LATENCY = Histogram(
    "chat_request_duration_seconds",
    "Time spent processing chat requests",
    ["agent"],
)