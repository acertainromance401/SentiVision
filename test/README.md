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
└── test
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
python test/main_.py
```

실행 중 입력:

1. 분석할 이미지 경로 입력
2. 예측 감정 피드백 입력
   - Enter/yes/y/예: 기존 예측 유지
   - 다른 텍스트 입력: 해당 감정으로 CSV에 반영

예시:

```text
분석할 이미지 파일 경로를 입력하세요: test/C500x500.jpeg
```

## 코드 분석 (main_.py)

아래는 `main_.py`의 함수별 책임과 입출력, 동작 포인트를 정리한 표입니다.

| 함수 | 목적 | 입력 | 출력 | 비고 |
|---|---|---|---|---|
| `setup_plot_style()` | Matplotlib 기본 폰트/마이너스 표시 설정 | 없음 | 없음 | 실행 환경(헤드리스/GUI) 차이로 인한 한글/기호 깨짐을 줄임 |
| `finalize_plot(filename)` | 플롯을 화면 표시 또는 파일 저장으로 마무리 | `filename: str` | 없음 | 백엔드가 Agg면 `outputs/`에 저장, 아니면 `plt.show()` |
| `emotion_from_rgb(knn_model, r, g, b)` | 단일 RGB를 정규화해 감정 라벨 예측 | KNN 모델, `r/g/b` | `predicted_emotion: str` | 내부에서 `(r,g,b)/255` 후 `predict()` 수행 |
| `normalize_emotion_label(label)` | 감정 라벨 공백/대소문자/오타 정규화 | `label: Any` | `normalized_label: str` | 예: `CORWARDICE` -> `COWARDICE` |
| `save_feedback_rows(new_rows)` | 사용자 피드백을 CSV에 안전하게 병합 저장 | `new_rows: list[dict]` | 없음 | 스키마 정렬, 라벨 정규화, `(R,G,B,emotion)` 중복 제거 |
| `main()` | 학습-추론-시각화-피드백 반영 전체 파이프라인 실행 | 사용자 입력(이미지 경로, 감정 피드백) | 콘솔 로그, PNG 파일, CSV 갱신 | 실패 시 `sys.exit(1)`로 종료 |

### main() 단계별 흐름

1. CSV 로드 후 감정 라벨 정규화 (`main_.py` 137~143행)
2. RGB를 0~1로 정규화하고 KNN(`n_neighbors=3`) 학습 (`main_.py` 145~156행)
3. 훈련셋 예측/정확도 출력 (`main_.py` 158~168행)
4. 학습 데이터 RGB 3D 시각화 생성 (`main_.py` 170~183행)
5. 입력 이미지 로드(BGR->RGB) 후 100x100 리사이즈 (`main_.py` 185~201행)
6. Laplacian 기반 salient mask 생성 (`main_.py` 203~213행)
7. 현저 픽셀만 추출해 KMeans로 대표 색상 추출 (`main_.py` 215~234행)
8. 대표 색상별 감정 예측/시각화 (`main_.py` 236~267행)
9. 사용자 피드백(정답 감정) 수집 (`main_.py` 269~292행)
10. 신규 라벨을 CSV에 반영 (`main_.py` 294~295행)

### 입력/출력 파일 정리

- 입력 데이터: `test/color_emotion_labeled_updated.csv`
- 입력 이미지: 실행 중 사용자가 입력한 파일 경로
- 출력 이미지:
	- `test/outputs/rgb_3d_distribution.png`
	- `test/outputs/saliency_maps.png`
	- `test/outputs/dominant_color_emotions.png`
- 피드백 반영 대상: `test/color_emotion_labeled_updated.csv`

### 예외/실패 처리

- 이미지 경로가 잘못되어 `cv2.imread()`가 실패하면 즉시 종료
- 현저 픽셀이 하나도 없으면 즉시 종료
- CSV 저장 중 예외 발생 시 에러 메시지를 출력하고 종료하지 않고 복귀

### 현재 코드 해석 시 주의점

- 출력되는 정확도는 훈련 데이터 기준 정확도이므로 일반화 성능 지표와 다를 수 있음
- 현저성 임계값(현재 10)과 KMeans 클러스터 수(기본 3)는 결과에 큰 영향을 줌
- 사용자 피드백 누적에 따라 동일 RGB라도 라벨 분포가 달라질 수 있음

## 출력 결과

아래 시각화 결과가 생성/갱신됩니다.

- test/outputs/rgb_3d_distribution.png
- test/outputs/saliency_maps.png
- test/outputs/dominant_color_emotions.png

또한 사용자 피드백이 있을 경우 데이터셋 파일이 갱신됩니다.

- test/color_emotion_labeled_updated.csv

## 라이선스 및 고지

- 프로젝트 라이선스: LICENSE
- 서드파티 고지: test/THIRD_PARTY_NOTICES.md
- MIT 라이선스 원문: test/LICENSES/MIT-sophiwoods-color-associations.txt
