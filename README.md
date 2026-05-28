# SentiVision

SentiVision은 개인 창작 사용자가 캔버스 드로잉의 색감을 통해 감정 톤을 분석하고 기록할 수 있는 제품을 목표로 합니다.
현재 저장소는 Python CLI 분석 엔진을 포함하며, 앱/API 개발을 위한 검증 파이프라인으로 함께 운영합니다.

## About

프로젝트의 제품 방향은 다음과 같습니다.

- 앱 경험: SwiftUI 기반 드로잉, 분석, 피드백, 히스토리
- API 계층: 분석(`POST /analyze`), 피드백(`POST /feedback`), 상태 확인(`GET /health`)
- 데이터/검증: CLI 기반 분석, 시각화 산출물, CSV 보정 루프

## Final Submission Evidence

필수 제출 기준을 다음 산출물로 충족합니다.

- 공개 저장소 기본 문서: `README.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `LICENSE`
- 동작 가능한 AI 기능(API + UI): `src/api/server.js`, `src/api/aiService.js`, `frontend/index.html`
- PR 게이트 CI/CD: `.github/workflows/ci-matrix.yml`, `.github/workflows/build-test-deploy.yml`
- main 배포: `.github/workflows/aws-ecs-deploy.yml`, `.github/workflows/jekyll-gh-pages.yml`
- 헬스체크: `GET /health` (`src/api/server.js`)
- 롤백 계획: `docs/runbook/production-runbook.md`
- 관측성(로그/메트릭/대시보드): `GET /metrics`, `docker-compose.yml`, `prometheus.yml`, `docs/observability/dashboard.md`
- 테스트: `__tests__/`, `tests/test_smoke.py`, `e2e/frontend.spec.js`
- 보안: `.github/dependabot.yml`, `.github/workflows/security-scans.yml`
- 문서: `docs/adr/0002-experiment-decision-persevere.md`, `docs/runbook/production-runbook.md`, `CHANGELOG.md`
- 릴리스 태그: `v1.0.1`
- 회고: `RETROSPECTIVE.md`
- 3분 이내 영상 데모 스크립트: `docs/demo/VIDEO_DEMO.md`

## AI API Quick Start

로컬 API 실행:

1. `npm ci`
2. `npm run start:api`

검증 명령:

- Health: `curl -s http://localhost:8080/health`
- Analyze:
	`curl -s http://localhost:8080/analyze -H 'Content-Type: application/json' -d '{"colors":[{"hex":"#FF6B2C","weight":0.6},{"hex":"#38BDF8","weight":0.4}]}'`
- Metrics: `curl -s http://localhost:8080/metrics | head`

## UI Preview

홈 화면 시안(사용자 제공 Stitch 결과물):

![SentiVision Home Screen](Project_Descriptions/images/sentivision-home-screen.png)

## Project

상세 실행 방법과 폴더별 사용 가이드는 아래 문서를 참고하세요.

- test/README.md

참고:
- `test/` 폴더는 개선된 CLI 검증 파이프라인과 데이터 자산을 담는 현행 작업 영역입니다.
- `base_model/` 폴더는 변경 전 원본 파이프라인으로, 비교 기준(baseline)으로 유지합니다.
- `base_model/README.md`에는 사용자 원안 아이디어를 기준으로 한 문제의식, 파이프라인 검증 범위, baseline 역할 구분이 정리되어 있습니다.
- 레퍼런스 문서: Project_Descriptions/reference/user-idea-report-1940200.pdf
- 제품 방향과 설계 의도는 `Project_Descriptions/` 문서 세트를 기준으로 봅니다.

## Environment

이 저장소는 Public으로 공개되어 있으므로 민감정보가 담긴 `.env` 파일은 커밋하지 않습니다.

로컬 실행 시:

1. `.env.example`을 복사해 `.env`를 생성합니다.
2. 실제 로컬 값으로 변경해 사용합니다.

예시 키:
- `GF_SECURITY_ADMIN_USER`
- `GF_SECURITY_ADMIN_PASSWORD`

## Project Descriptions

- Project_Descriptions/Development_Process_and_Tools_Proposal.md
- Project_Descriptions/PRD_SentiVision.md
- Project_Descriptions/Project_Description.md
- Project_Descriptions/User_Journey_Scenario_SentiVision.md
- Project_Descriptions/WBS_SentiVision.md
- Project_Descriptions/Wireframe_SentiVision.md

## Current CLI Pipeline

현재 구현된 분석 파이프라인은 다음과 같습니다.

1. 색상-감정 CSV를 로드해 KNN 분류기를 학습합니다.
2. 입력 이미지에서 현저성 영역을 추출합니다.
3. KMeans로 주요 색상 3개를 추출합니다.
4. 감정을 예측하고 시각화 산출물을 생성합니다.
5. 사용자 피드백으로 CSV를 갱신합니다.

추가 분석 스크립트:
- `test/test_model_comparison.py`: KNN vs RandomForest 성능 비교(Train/Test 분리, 교차검증, 대시보드 생성)
- `test/run_all_analysis.py`: `main_.py` + `test_model_comparison.py` 순차 실행

주요 출력 규칙:
- `test/main_.py`는 실행 시각 기반 접두사(`main_YYYYMMDD_HHMMSS_*`)로 이미지를 저장합니다.
- `test/test_model_comparison.py`는 `comparison_YYYYMMDD_HHMMSS_*` 대시보드/비교 이미지를 저장합니다.

이 파이프라인은 최종 앱 제품 자체가 아니라, 앱/API 개발을 검증하는 기준선 역할을 합니다.

## DORA Metrics 자동 수집 파이프라인

이 저장소에는 주간/이벤트 기반 성능 지표 워크플로가 포함되어 있습니다.

- 워크플로우 파일: .github/workflows/lead-time.yml
- 워크플로우 파일: .github/workflows/deployment-frequency.yml
- 워크플로우 파일: .github/workflows/change-failure-rate.yml
- 워크플로우 파일: .github/workflows/mttr.yml
- 워크플로우 파일: .github/workflows/throughput.yml

### 수집 지표

- DORA Lead Time: PR 생성부터 merge까지 소요 시간
- DORA Deployment Frequency: main 브랜치 반영 빈도(프록시)
- DORA Change Failure Rate: incident 이슈 수 / main 반영 수(프록시)
- DORA MTTR: incident 이슈의 평균 복구 시간
- Throughput: 최근 7일 닫힌 이슈 수

### 운영 규칙

- 장애/운영 이슈에는 반드시 incident 라벨을 붙입니다.
- Actions 탭에서 각 워크플로를 Run workflow로 수동 실행할 수 있습니다.
- 각 실행 결과는 GitHub Actions Job Summary에 표 형태로 기록됩니다.

### 참고

- 현재 저장소 특성상 실제 배포 이벤트 대신 main 반영을 배포 프록시로 사용합니다.
- 실제 배포 파이프라인이 생기면 deployment 이벤트 기반으로 전환하는 것을 권장합니다.

## Additional Links

- Repository: https://github.com/acertainromance401/SentiVision
- Actions: https://github.com/acertainromance401/SentiVision/actions
- Issues: https://github.com/acertainromance401/SentiVision/issues

## OSS Governance

이 저장소는 오픈소스 협업을 위한 기본 정책 문서를 제공합니다.

- License: `LICENSE` (MIT)
- Contribution Guide: `CONTRIBUTING.md`
- Code of Conduct: `CODE_OF_CONDUCT.md`

선택 과제 문서:

- License 비교/선정 기준: `docs/oss/license-comparison.md`
- Inner Source 도입 로드맵: `docs/oss/innersource-roadmap.md`

## Frontend 자동 배포 + PR 프리뷰

정적 프런트 페이지(`frontend/index.html`)는 GitHub Pages로 자동 배포됩니다.

- 프로덕션 배포 워크플로우: `.github/workflows/jekyll-gh-pages.yml`
- PR 프리뷰 워크플로우: `.github/workflows/frontend-pr-preview.yml`
- 프런트 소스: `frontend/index.html`

배포 URL 패턴:

- Production: `https://acertainromance401.github.io/SentiVision/`
- PR Preview: `https://acertainromance401.github.io/SentiVision/pr-preview/pr-<PR번호>/`

초기 설정 1회:

1. GitHub 저장소 설정에서 **Pages > Build and deployment > Source**를 `Deploy from a branch`로 선택
2. Branch를 `gh-pages` / `root`로 지정

## Docker 배포 파이프라인 전략

- 전략 문서: `docs/deployment/docker-pipeline-strategy.md`
- Docker 이미지 빌드/검증/GHCR 푸시 워크플로우: `.github/workflows/docker-image.yml`

핵심 흐름:

1. Dockerfile 변경 감지
2. 이미지 빌드
3. 컨테이너 헬스체크(`/health`)
4. 레지스트리 푸시(`latest`, `sha`)
5. 배포 대상(클라우드) 업데이트

## AWS ECS 자동 배포 + 헬스체크/모니터링

AWS(ECS Fargate) 기반 자동 배포 워크플로우를 제공합니다.

- 워크플로우: `.github/workflows/aws-ecs-deploy.yml`
- 태스크 정의: `infra/aws/task-definition.json`

포함 기능:

- OIDC 기반 AWS 인증
- ECR 이미지 빌드/푸시
- ECS 서비스 롤링 배포
- 외부 헬스체크 URL 호출(`/health`)
- CloudWatch CPU/Memory 알람 자동 생성

필수 Secrets:

- `AWS_ROLE_TO_ASSUME`
- `ECS_HEALTHCHECK_URL` (예: `https://api.example.com`)

## Feature Flags / A-B Test / Canary

구현 파일:

- Feature flag 코드: `src/featureFlags.js`
- A/B 할당 로직: `src/abTesting.js`
- 이벤트 추적 로깅: `src/eventTracker.js`
- 실험 데모 실행: `experiments/ab-assignment-demo.js`
- Canary 롤아웃 설정: `experiments/canary-rollout-config.json`
- Canary 롤백 시뮬레이터: `experiments/canary-rollout-simulator.js`

실행 로그:

- 실험 로그: `experiments/logs/ab-events.ndjson`
- 롤아웃 로그: `experiments/logs/canary-rollout-log.json`

실행 명령:

- `npm run demo:flags-ab`
- `npm run demo:canary`

## User Scenario Experiments (10 LLM Personas)

관련 파일:

- 페르소나 데이터: `experiments/user-research/personas.json`
- 시나리오 정의: `experiments/user-research/scenarios.json`
- 피드백 생성/평가 코드: `experiments/user-research/generate_persona_feedback.js`
- 피드백 데이터(10명): `experiments/user-research/persona_feedback.json`
- 피드백 리포트: `experiments/user-research/persona_feedback_report.md`

2주 A/B 테스트:

- 2주 지표 데이터: `experiments/ab-test/two_week_ab_metrics.csv`
- 분석 코드: `experiments/ab-test/analyze_two_week_ab.js`
- 분석 리포트: `experiments/ab-test/ab_two_week_report.md`

결정 기록:

- ADR: `docs/adr/0002-experiment-decision-persevere.md`

자동화(선택과제):

- 실험 백로그 이슈 템플릿: `.github/ISSUE_TEMPLATE/experiment_backlog.yml`
- 주간 지표 수집/리포팅 워크플로우: `.github/workflows/weekly-experiment-report.yml`

실행 명령:

- `npm run report:personas`
- `npm run report:ab-two-week`
