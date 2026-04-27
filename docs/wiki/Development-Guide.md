# Development Guide

SentiVision 협업 개발 기준입니다.

## Branch Strategy

- 기본: `main` 보호 브랜치
- 작업: `feat/<issue>-<slug>`, `fix/<issue>-<slug>`, `docs/<issue>-<slug>`
- 모든 변경은 PR 기반으로 병합

예시:

- `feat/11-color-emotion-preprocessing`
- `feat/12-rest-api-endpoint`
- `feat/10-model-pipeline`

## Commit Convention

Conventional Commits를 사용합니다.

```text
<type>(<scope>): <subject>
```

예시:

- `feat(api): add /analyze REST endpoint`
- `feat(model): extract KNN emotion classifier`
- `docs(wiki): add troubleshooting guide`

## Pull Request Rules

- PR 템플릿 준수
- `Closes #<issue>` 명시
- 리뷰 코멘트 태그 사용
  - `[MUST]` 머지 전 필수
  - `[SHOULD]` 강력 권고
  - `[CONSIDER]` 선택

## ADR Process

아키텍처/운영 의사결정은 ADR로 기록합니다.

- 위치: `docs/adr/`
- 템플릿: `docs/adr/template.md`
- 파일명 규칙: `NNNN-short-title.md`

## Next Docs

- 초기 온보딩: [Getting Started](Getting-Started.md)
- 장애 대응: [Troubleshooting](Troubleshooting.md)
