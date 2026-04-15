# SentiVision

SentiVision은 개인 창작 사용자가 캔버스 드로잉의 색감을 통해 감정 톤을 분석하고 기록할 수 있는 제품을 목표로 합니다.
현재 저장소는 Python CLI 분석 엔진을 포함하며, 앱/API 개발을 위한 검증 파이프라인으로 함께 운영합니다.

## About

프로젝트의 제품 방향은 다음과 같습니다.

- 앱 경험: SwiftUI 기반 드로잉, 분석, 피드백, 히스토리
- API 계층: 분석(`POST /analyze`), 피드백(`POST /feedback`), 상태 확인(`GET /health`)
- 데이터/검증: CLI 기반 분석, 시각화 산출물, CSV 보정 루프

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

## GitHub Pages (Jekyll)

AI 포트폴리오용 Jekyll 페이지 파일이 루트에 포함되어 있습니다.

- 설정 파일: `_config.yml`
- 메인 페이지: `index.md`

GitHub 저장소 설정에서 **Pages > Build and deployment > Source**를 현재 브랜치의 **`/(root)`** 로 지정하면 바로 배포할 수 있습니다.
