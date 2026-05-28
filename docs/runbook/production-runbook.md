# Production Runbook

## Purpose

This runbook defines deployment validation, health checks, incident response, and rollback for SentiVision.

## Deployment Path

- PR gate: `.github/workflows/ci-matrix.yml`
- Main deploy: `.github/workflows/aws-ecs-deploy.yml`
- Container verification: `.github/workflows/docker-image.yml`

## Pre-deploy Checklist

1. CI matrix green on pull request
2. Security scan workflow reviewed
3. Mini eval check passed (`node scripts/mini-eval.js`)
4. Health endpoint returns 200 in staging/prod

## Post-deploy Verification

1. `GET /health` responds with status `ok`
2. `GET /metrics` contains key counters
3. CloudWatch ECS CPU/Memory alarms are active
4. Recent logs show `status` 2xx for `/analyze`

## Rollback Plan

Trigger rollback when one or more conditions hold:

- `/health` fails consecutively for 5 minutes
- Analyze error rate exceeds 5%
- p95 latency regresses more than 2x baseline

Rollback steps:

1. Freeze rollout by stopping new deployment workflow runs.
2. In ECS, switch service task definition to previous stable revision.
3. Force new deployment of previous revision.
4. Verify `/health` and `/metrics` recovery.
5. Open incident issue with root-cause summary.

## Incident Commands (example)

- Check API health:
  - `curl -fsS "$ECS_HEALTHCHECK_URL/health"`
- Check metrics sample:
  - `curl -fsS "$ECS_HEALTHCHECK_URL/metrics" | head`

## Ownership

- Primary owner: Repository maintainers (CODEOWNERS)
- Escalation: Open issue with label `incident`
