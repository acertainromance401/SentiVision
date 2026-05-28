# Changelog

All notable changes to this project are documented in this file.

## [1.0.1] - 2026-05-28

### Added

- AI palette analysis API endpoint (`POST /analyze`) in `src/api/server.js`
- Prometheus metrics endpoint (`GET /metrics`) and structured request logs
- Mini eval script (`scripts/mini-eval.js`) for lightweight model behavior checks
- Production runbook with rollback plan (`docs/runbook/production-runbook.md`)
- Observability dashboard guide (`docs/observability/dashboard.md`)
- Retrospective document (`RETROSPECTIVE.md`)
- 3-minute demo script and checklist (`docs/demo/VIDEO_DEMO.md`)

### Changed

- Docker image runtime switched to Node API service for deployable AI endpoint
- Docker Compose now includes API service and Prometheus scrape target
- Build/Test workflow now runs mini eval in CI
- Frontend now includes direct AI analyze demo UI panel
