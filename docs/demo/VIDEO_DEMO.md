# 3-Minute Demo Script

## Target Length

- 2 minutes 30 seconds to 3 minutes 00 seconds

## Demo Flow

1. (0:00-0:20) Repository governance files
   - Show `README.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `LICENSE`
2. (0:20-1:00) PR gate and security
   - Show `.github/workflows/ci-matrix.yml`
   - Show `.github/workflows/security-scans.yml` and `.github/dependabot.yml`
3. (1:00-1:50) AI API live run
   - `node src/api/server.js`
   - `curl -s http://localhost:8080/health`
   - `curl -s http://localhost:8080/analyze -H 'Content-Type: application/json' -d '{"colors":[{"hex":"#FF6B2C","weight":0.6},{"hex":"#38BDF8","weight":0.4}]}'`
4. (1:50-2:20) Observability
   - `curl -s http://localhost:8080/metrics | head`
   - Open Prometheus/Grafana from docker-compose stack
5. (2:20-2:45) Deployment and rollback
   - Show `.github/workflows/aws-ecs-deploy.yml`
   - Show `docs/runbook/production-runbook.md` rollback section
6. (2:45-3:00) Release and retrospective
   - Show release tag `v1.0.1`
   - Show `CHANGELOG.md` and `RETROSPECTIVE.md`

## Recording Checklist

- Include terminal font size large enough for readability
- Keep command output visible at least 3 seconds per key proof point
- Mention health check and rollback trigger explicitly
- End with repository URL and release tag on screen

## Video Link Placeholder

- Add final uploaded URL here after recording:
  - `VIDEO_DEMO_URL: <to-be-added>`
