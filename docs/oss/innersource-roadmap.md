# Inner Source Adoption Roadmap

## Purpose

조직 내부 팀 간 협업 품질을 높이기 위해 SentiVision 저장소에 Inner Source 운영 모델을 단계적으로 도입합니다.

## Principles

- Open by default (내부 공개 기본)
- Async-first collaboration (이슈/PR/Discussions 중심)
- Lightweight governance (최소 규칙, 명확한 책임)

## Roadmap

### Phase 1: Foundation (0-1 month)

- OSS 기본 문서 정비: README, LICENSE, CONTRIBUTING, CODE_OF_CONDUCT
- PR 템플릿/CODEOWNERS/브랜치 보호 규칙 정착
- Discussions 운영 시작 (RFC 포맷, Q&A, Announcements)

Success signals:

- 신규 기여자가 문서만으로 첫 PR 생성 가능
- PR 리뷰 태그([MUST]/[SHOULD]) 사용률 증가

### Phase 2: Collaboration Scale (1-3 months)

- 팀별 모듈 소유권 명시 (`src/model`, `src/api`, `src/data`)
- 주간 요약 자동화로 운영 가시성 확보
- SLA 추적 기반 이슈 triage 리듬 고정

Success signals:

- 평균 첫 리뷰 응답 시간 단축
- 리뷰 라운드 수 안정화

### Phase 3: Productization (3-6 months)

- ADR 기반 기술 의사결정 프로세스 정식화
- 릴리즈 노트/버전 정책(semver) 도입
- 내부 재사용 패키지화(모델/전처리/평가 모듈)

Success signals:

- 타 팀 재사용 사례 확보
- 중복 구현 감소

## Governance Model

- Maintainer: 병합 승인/릴리즈 책임
- Code Owner: 모듈 품질 게이트 책임
- Contributor: 이슈 기반 구현/문서화 책임

## KPI Suggestions

- First response time (Issues/PR)
- PR lead time
- Review turnaround time
- Weekly merged PR count
- Reuse count (internal consumers)

## Risks and Mitigation

- Risk: 규칙 과잉으로 기여 감소
- Mitigation: 최소 규칙 유지, 템플릿 자동화

- Risk: 소유권 불명확
- Mitigation: CODEOWNERS와 ADR에서 책임 명시

- Risk: 문서 최신성 저하
- Mitigation: PR 체크리스트에 문서 업데이트 항목 포함
