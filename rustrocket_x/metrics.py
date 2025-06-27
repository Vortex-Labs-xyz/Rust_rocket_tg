from prometheus_client import Counter, Histogram, start_http_server

RUNS = Counter("rrx_runs_total", "Total CLI runs")
ERRORS = Counter("rrx_errors_total", "Failed runs")
LATENCY = Histogram("rrx_duration_seconds", "Execution time")

def init_metrics(port: int = 9100):
    start_http_server(port) 