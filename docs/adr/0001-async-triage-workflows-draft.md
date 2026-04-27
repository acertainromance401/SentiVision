# ADR 0001: Adopt Draft Automation for Triage, SLA, and Weekly Summary

- Date: 2026-04-27
- Status: Proposed
- Deciders: maintainers
- Technical Story: repository operations improvement

## Context

이슈 증가에 따라 응답 지연, SLA 누락, 주간 진행상황 집계의 수작업 비용이 커지고 있습니다.

## Decision

다음 3개의 GitHub Actions 초안 워크플로우를 도입합니다.

- 자동 응답 (`auto-response.yml`)
- SLA 추적 (`sla-tracking.yml`)
- 주간 요약 (`weekly-summary.yml`)

## Options Considered

1. 수동 운영 유지
2. 외부 SaaS 도입
3. GitHub Actions 기반 내부 자동화 (채택)

## Consequences

- Positive: 초기 운영 비용 절감, 응답 일관성 향상
- Negative: 토큰 권한/실패 처리 설계 필요
- Risks: 잘못된 자동 댓글, 과도한 알림

## Follow-up Actions

- [ ] 민감 이벤트에 대한 allowlist 적용
- [ ] SLA 기준값 합의 및 환경변수화
- [ ] 주간 요약 포맷 확정

## References

- Workflow files: `.github/workflows/*.yml`
