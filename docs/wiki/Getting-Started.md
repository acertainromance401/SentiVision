# Getting Started

SentiVision 개발을 시작하는 최소 절차입니다.

## Prerequisites

- macOS 또는 Linux
- Python 3.12+
- Git
- GitHub CLI (`gh`)

## Setup

1. 저장소 클론

```bash
git clone https://github.com/acertainromance401/SentiVision.git
cd SentiVision
```

2. 가상환경 준비

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt  # 파일이 없으면 필요한 패키지 개별 설치
```

3. 기본 데이터/모듈 검증

```bash
python3 -m src.model.emotion_classifier train
python3 -m src.model.emotion_classifier predict 255 87 51
```

## First Run

현재 검증용 CLI는 원본 데이터셋 대신 보강본 기준으로 동작합니다.

- 전처리 파이프라인 실행:

```bash
python3 -c "from src.data.preprocessing import run_pipeline; print(run_pipeline('test/color_emotion_labeled_augmented.csv').summary())"
```

- 연구 비교 스크립트 실행:

```bash
python3 test/research_compare_extraction.py
```

이 스크립트는 `baseline_laplacian`, `paint_region`, `paint_region_conservative`를 비교해
그림 입력에 더 맞는 색 추출 방향을 검증하는 용도입니다.

## Next Docs

- 개발 규칙/브랜치 전략: [Development Guide](Development-Guide.md)
- 자주 막히는 이슈 해결: [Troubleshooting](Troubleshooting.md)
