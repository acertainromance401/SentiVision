# SentiVision

이미지의 주요 색상(RGB)을 기반으로 감정을 예측하는 Python 프로젝트입니다.

## About

SentiVision은 색상 중심 신호를 사용해 감정 경향을 추정하는 실험 프로젝트입니다.
현재 구현은 RGB 기반 데이터셋과 이미지 주요 색상 추출 흐름을 중심으로 구성되어 있습니다.

## Project

상세 실행 방법과 폴더별 사용 가이드는 아래 문서를 참고하세요.

- test/README.md

## Project Descriptions

링크의 Project_Descriptions 항목을 현재 저장소에도 추가했습니다.

- 추천 문서: [Project_Descriptions/Development_Process_and_Tools_Proposal.md](Project_Descriptions/Development_Process_and_Tools_Proposal.md) (현재 구현 기준 개발 절차/도구 요약)

- Project_Descriptions/Development_Process_and_Tools_Proposal.md
- Project_Descriptions/PRD_SentiVision.md
- Project_Descriptions/Project_Description.md
- Project_Descriptions/User_Journey_Scenario_SentiVision.md
- Project_Descriptions/WBS_SentiVision.md
- Project_Descriptions/Wireframe_SentiVision.md

## Color Emotion Pipeline

프로젝트의 핵심 처리 흐름은 다음과 같습니다.

1. 색상-감정 라벨 CSV를 불러와 분류기를 학습합니다.
2. 입력 이미지에서 주요 영역을 추출합니다.
3. 주요 색상을 기반으로 감정 점수를 계산/예측합니다.
4. 사용자 피드백으로 데이터셋을 확장할 수 있습니다.

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
