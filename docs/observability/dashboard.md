# Observability Dashboard Guide

## Scope

SentiVision API observes four layers:

- Request logs (stdout JSON)
- Health endpoint (`GET /health`)
- Metrics endpoint (`GET /metrics`)
- Dashboard stack (Prometheus + Grafana)

## Local Dashboard Startup

1. Start stack:
   - `docker compose up --build`
2. Open endpoints:
   - API: `http://localhost:8080/health`
   - Metrics: `http://localhost:8080/metrics`
   - Prometheus: `http://localhost:9090`
   - Grafana: `http://localhost:3000`

## Recommended Prometheus Queries

- Total requests:
  - `sentivision_requests_total`
- Analyze request volume:
  - `sentivision_analyze_requests_total`
- Analyze error rate:
  - `sentivision_analyze_errors_total / sentivision_analyze_requests_total`
- Avg response duration (ms):
  - `sentivision_response_duration_ms_sum / sentivision_response_duration_ms_count`
- API uptime:
  - `sentivision_uptime_seconds`

## Dashboard Panels (suggested)

1. Stat: Total requests
2. Stat: Analyze errors
3. Time series: Analyze requests over time
4. Time series: Average response duration (ms)
5. Gauge: Uptime seconds

## Logging Format

API writes one JSON log line per request:

- `time`: UTC ISO timestamp
- `method`: HTTP method
- `path`: endpoint path
- `status`: response status code
- `durationMs`: request duration

This format is compatible with log shippers and SIEM ingestion.
