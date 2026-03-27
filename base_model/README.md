# SentiVision

이미지의 주요 색상(RGB)을 기반으로 감정을 예측하는 Python 프로젝트입니다.

## 개요

이 프로젝트는 다음 흐름으로 동작합니다.

1. 색상-감정 라벨 CSV를 불러와 KNN 분류기를 학습합니다.
2. 입력 이미지에서 현저성(saliency) 영역을 추출합니다.
3. KMeans로 주요 색상 3개를 뽑아 감정을 예측합니다.
4. 사용자 피드백을 받아 CSV 데이터셋을 확장할 수 있습니다.

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
