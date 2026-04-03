# SentiVision

이미지의 주요 색상(RGB)을 기반으로 감정을 예측하는 Python 프로젝트입니다.

## 개요

이 프로젝트는 다음 흐름으로 동작합니다.

1. 색상-감정 라벨 CSV를 불러와 KNN 분류기를 학습합니다.
2. 입력 이미지에서 현저성(saliency) 영역을 추출합니다.
3. KMeans로 주요 색상 3개를 뽑아 감정을 예측합니다.
4. 사용자 피드백을 받아 CSV 데이터셋을 확장할 수 있습니다.

## 아이디어 기반 배경 (사용자 원안 반영)

이 base_model은 사용자 원안 아이디어의 핵심 가설을 기술 검증용으로 고정한 기준선(baseline)입니다.

핵심 의도
- 창작 흐름을 끊는 텍스트/음성 입력 대신, 그림의 색감만으로 감정 상태를 해석한다.
- 예측 결과를 사용자 피드백으로 정정해 데이터셋을 보정하고, 다음 분석 품질을 점진적으로 높인다.

base_model에서 검증하는 항목
- 색상 기반 감정 추론 파이프라인: 현저성 추출 -> KMeans 대표 색상 추출 -> KNN 감정 매핑
- 사용자 피드백 반영 루프: 예측 감정 유지/수정 입력 -> CSV 데이터셋 업데이트
- 시각화 산출물 생성: RGB 분포, saliency map, 대표 색상-감정 결과

역할 구분
- base_model: 원안 아이디어의 최소 실행 가능 구조를 보존하는 기준선
- test: 개선된 검증 파이프라인과 모델 비교 실험 영역

관련 기획 문서
- Project_Descriptions/reference/user-idea-report-1940200.pdf
- Project_Descriptions/Project_Description.md
- Project_Descriptions/PRD_SentiVision.md
- Project_Descriptions/Wireframe_SentiVision.md

## 현재 폴더 구조

```text
.
├── LICENSE
├── README.md
└── base_model
	├── C500x500.jpeg
	├── LICENSES
	│   └── MIT-sophiwoods-color-associations.txt
	├── THIRD_PARTY_NOTICES.md
	├── color_emotion_labeled_updated.csv
	├── colorassociations_warmth - colorwarmth.csv
	├── main_.py
	└── outputs
		├── dominant_color_emotions.png
		├── rgb_3d_distribution.png
		└── saliency_maps.png
```

## 요구 사항

- Python 3.10+
- pip

필수 패키지:

- pandas
- matplotlib
- opencv-python
- scikit-learn
- numpy

## 설치

프로젝트 루트에서 실행:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pandas matplotlib opencv-python scikit-learn numpy
```

## 실행 방법

프로젝트 루트에서 실행:

```bash
python base_model/main_.py
```

실행 중 입력:

1. 분석할 이미지 경로 입력
2. 예측 감정 피드백 입력
   - Enter/yes/y/예: 기존 예측 유지
   - 다른 텍스트 입력: 해당 감정으로 CSV에 반영

예시:

```text
분석할 이미지 파일 경로를 입력하세요: base_model/C500x500.jpeg
```

## 출력 결과

아래 시각화 결과가 생성/갱신됩니다.

- base_model/outputs/rgb_3d_distribution.png
- base_model/outputs/saliency_maps.png
- base_model/outputs/dominant_color_emotions.png

또한 사용자 피드백이 있을 경우 데이터셋 파일이 갱신됩니다.

- base_model/color_emotion_labeled_updated.csv

## 라이선스 및 고지

- 프로젝트 라이선스: LICENSE
- 서드파티 고지: base_model/THIRD_PARTY_NOTICES.md
- MIT 라이선스 원문: base_model/LICENSES/MIT-sophiwoods-color-associations.txt
