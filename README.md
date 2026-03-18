# SentiVision

이미지의 주요 색상(RGB)을 기반으로 감정을 예측하는 Python 프로젝트입니다.

## 실행 문서

프로젝트 실행/사용법은 아래 문서를 참고하세요.

- test/README.md

## Metrics (GitHub Actions)

이 저장소에는 주간/이벤트 기반 성능 지표 워크플로가 포함되어 있습니다.

- DORA Lead Time: PR 생성부터 merge까지 소요 시간
- DORA Deployment Frequency: main 브랜치 반영 빈도(프록시)
- DORA Change Failure Rate: incident 이슈 수 / main 반영 수(프록시)
- DORA MTTR: incident 이슈의 평균 복구 시간
- Throughput: 최근 7일 닫힌 이슈 수

워크플로 파일:

- .github/workflows/lead-time.yml
- .github/workflows/deployment-frequency.yml
- .github/workflows/change-failure-rate.yml
- .github/workflows/mttr.yml
- .github/workflows/throughput.yml

### 운영 규칙

- 장애/운영 이슈에는 반드시 `incident` 라벨을 붙이세요.
- Actions 탭에서 각 워크플로를 `Run workflow`로 수동 실행할 수 있습니다.
- 각 실행 결과는 GitHub Actions Job Summary에 표 형태로 기록됩니다.

### 참고

- 현재 저장소 특성상 실제 배포 이벤트 대신 `main` 반영을 배포 프록시로 사용합니다.
- 실제 배포 파이프라인이 생기면 `deployment` 이벤트 기반으로 전환하는 것을 권장합니다.
