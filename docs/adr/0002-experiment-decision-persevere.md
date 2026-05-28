# ADR 0002: Experiment Decision - Persevere

## Status

Accepted

## Context

- 10명의 서로 다른 LLM 페르소나 패턴 기반 사용자 피드백을 수집했다.
- Feature Flag 기반 A/B 테스트를 2주간 운영했다.
- 핵심 지표(activation, feedback submit, D7 retention, session length)를 비교했다.

## Data Sources

- `experiments/user-research/persona_feedback.json`
- `experiments/user-research/persona_feedback_report.md`
- `experiments/ab-test/two_week_ab_metrics.csv`
- `experiments/ab-test/ab_two_week_report.md`

## Decision

Persevere

## Rationale

- B variant가 A 대비 activation/feedback/D7 retention에서 일관된 개선을 보였다.
- 사용자 피드백에서 "결과 해석 가능성"과 "추천 액션"에 대한 긍정 반응이 증가했다.
- 즉각적인 제품 방향 전환(Pivot)보다는, 현재 방향을 유지하며 점진 개선하는 것이 합리적이다.

## Follow-up Actions

1. B variant를 기본값으로 점진 확장(10% -> 50% -> 100%)
2. 접근성/프라이버시 관련 피드백 개선 항목을 다음 스프린트 백로그로 이관
3. 주간 리포트 자동화를 통해 지표 저하 시 롤백 트리거 점검
