# SentiVision

이미지의 주요 색상(RGB)을 기반으로 감정을 예측하는 Python 프로젝트입니다.

## 개요

이 프로젝트는 다음 흐름으로 동작합니다.

1. 색상-감정 라벨 CSV를 불러와 KNN 분류기를 학습합니다.
2. 입력 이미지에서 현저성(saliency) 영역을 추출합니다.
3. KMeans로 주요 색상 3개를 뽑아 감정을 예측합니다.
4. 사용자 피드백을 받아 CSV 데이터셋을 확장할 수 있습니다.
5. 별도 비교 스크립트에서 KNN vs RandomForest 성능을 비교합니다.

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
	├── run_all_analysis.py
	├── test_model_comparison.py
	└── outputs
		├── main_YYYYMMDD_HHMMSS_*.png
		└── comparison_YYYYMMDD_HHMMSS_*.png
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

모델 비교 실행:

```bash
python test/test_model_comparison.py
```

메인 + 비교 일괄 실행:

```bash
python test/run_all_analysis.py
```

### 비교 스크립트 사용 흐름

`test/test_model_comparison.py` 실행 시 실제 흐름은 아래와 같습니다.

1. `test/color_emotion_labeled_updated.csv` 로드
2. 고정 검증셋 파일(`test/fixed_validation_indices.json`) 로드 또는 최초 1회 생성
3. 학습셋으로 KNN, RandomForest 재학습
4. 고정 검증셋 기준 Accuracy, F1, Confusion Matrix 평가
5. 반복 분할 평가로 RF 우세 여부를 추가 판정
6. 이미지 경로 입력
7. 이미지의 salient 영역에서 대표 색상 3개 추출
8. 각 색상에 대해 KNN, RF 감정 예측 비교
9. 사용자가 최종 감정을 번호 선택으로 입력
10. 중복/충돌 검사 후 `test/color_emotion_labeled_updated.csv` 반영
11. 수정 전 CSV 백업 및 업데이트 이력 저장

### 실제 입력 예시

```text
$ python test/test_model_comparison.py

[Step 1] CSV 로드 및 데이터 준비
[Step 2] 고정 검증셋 분리
[Step 3] 모델 학습
[Step 4] 성능 평가 (테스트 셋)
[Step 5] 교차검증
[Step 5-1] 반복 분할 평가
[Step 6] 시각화
[Step 7] 실시간 이미지 분석 (선택)
분석할 이미지 파일 경로 입력 (또는 Enter 스킵): test/C500x500.jpeg

[결과] 추출 색상 감정 예측 (KNN vs RandomForest)
----------------------------------------------------------------------
Color 1 RGB(30, 38, 56)
	KNN          : DARKNESS
	RandomForest : DESPAIR ✗

Color 2 RGB(142, 157, 154)
	KNN          : BALANCE
	RandomForest : RESERVED ✗

Color 3 RGB(71, 92, 126)
	KNN          : DEPRESSION
	RandomForest : DEPRESSION ✓

[Step 8] 사용자 감정 입력(선택)
- Enter: RF 예측값 사용
- 번호 입력: 기존 라벨 목록 중 하나 선택

[선택 가능한 감정 라벨 목록]
- 활력/행동
 1. ALERTNESS   2. COURAGE   3. DYNAMIC

- 안정/회복
14. BALANCE    15. CALMNESS  16. COMFORT

...

[1] RGB(30, 38, 56)
	KNN: DARKNESS
	RF : DESPAIR
	최종 감정 번호 입력 (Enter=RF 사용, ?=목록 다시 보기): 15

[2] RGB(142, 157, 154)
	KNN: BALANCE
	RF : RESERVED
	최종 감정 번호 입력 (Enter=RF 사용, ?=목록 다시 보기):

[3] RGB(71, 92, 126)
	KNN: DEPRESSION
	RF : DEPRESSION
	최종 감정 번호 입력 (Enter=RF 사용, ?=목록 다시 보기): 51
```

위 예시는 다음 의미입니다.

- 첫 번째 색상: 사용자가 `CALMNESS`를 직접 선택
- 두 번째 색상: Enter를 눌러 RF 예측값 `RESERVED` 사용
- 세 번째 색상: 사용자가 `MYSTERY`를 직접 선택

### 사용자 입력 규칙

1. Enter
	 - RF 예측값을 그대로 최종 감정으로 사용
2. 숫자 입력
	 - 감정군별 메뉴에서 해당 번호의 감정을 선택
3. `?`
	 - 감정군별 라벨 목록을 다시 출력

### CSV 반영 규칙

사용자 입력 결과는 `test/color_emotion_labeled_updated.csv`에 직접 반영됩니다.

반영 전 검사:

1. 완전 중복
	 - 같은 `RGB + emotion` 이 이미 있으면 저장하지 않음
2. 충돌 항목
	 - 같은 RGB에 다른 emotion 이 이미 있으면 추가 저장 여부를 다시 확인

### 버전 관리 및 이력

CSV 수정 전:

- `test/dataset_versions/color_emotion_labeled_updated_YYYYMMDD_HHMMSS.csv` 백업 생성

CSV 수정 후:

- `test/model_update_history.csv` 에 변경 이력 누적

기록 항목:

- 수정 전후 행 수
- 신규 추가 수
- 중복 스킵 수
- 충돌 스킵/추가 수
- KNN/RF 검증 성능
- 반복 평가 평균 성능
- RF margin 우세 여부

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

## 코드 분석 (test_model_comparison.py)

주요 기능:
- 고정 검증셋 기반 KNN, RandomForest 성능 비교
- Accuracy, F1, Confusion Matrix 대시보드 생성
- 동일 입력 이미지에 대해 대표 색상별 KNN/RF 예측 결과 비교
- 사용자 최종 감정 선택형 입력 후 학습 CSV 직접 반영
- 데이터셋 백업 및 업데이트 이력 관리

주요 출력:
- `comparison_YYYYMMDD_HHMMSS_performance_dashboard.png`
- `comparison_YYYYMMDD_HHMMSS_knn_rf_color_pair.png`
- `test/dataset_versions/color_emotion_labeled_updated_YYYYMMDD_HHMMSS.csv`
- `test/model_update_history.csv`

보조 설정:
- `SAVE_EXTRA_DEBUG_PLOTS=False` 기본값으로 디버그 플롯 과다 생성을 방지

### 입력/출력 파일 정리

- 입력 데이터: `test/color_emotion_labeled_updated.csv`
- 입력 이미지: 실행 중 사용자가 입력한 파일 경로
- 고정 검증셋: `test/fixed_validation_indices.json`
- 출력 이미지:
	- `test/outputs/main_YYYYMMDD_HHMMSS_rgb_3d_distribution.png`
	- `test/outputs/main_YYYYMMDD_HHMMSS_saliency_maps.png`
	- `test/outputs/main_YYYYMMDD_HHMMSS_dominant_color_emotions.png`
	- `test/outputs/comparison_YYYYMMDD_HHMMSS_performance_dashboard.png`
	- `test/outputs/comparison_YYYYMMDD_HHMMSS_knn_rf_color_pair.png`
- 피드백 반영 대상: `test/color_emotion_labeled_updated.csv`
- CSV 백업: `test/dataset_versions/`
- 업데이트 이력: `test/model_update_history.csv`

### 예외/실패 처리

- 이미지 경로가 잘못되어 `cv2.imread()`가 실패하면 즉시 종료
- 현저 픽셀이 하나도 없으면 즉시 종료
- CSV 저장 중 예외 발생 시 에러 메시지를 출력하고 종료하지 않고 복귀

### 현재 코드 해석 시 주의점

- 비교 스크립트의 핵심 평가는 고정 검증셋 기준으로 수행됨
- 반복 분할 평가는 학습셋 내부에서만 수행되어 검증셋 누수를 방지함
- 현저성 임계값(현재 10)과 KMeans 클러스터 수(기본 3)는 결과에 큰 영향을 줌
- 사용자 피드백 누적에 따라 동일 RGB라도 라벨 분포가 달라질 수 있음
- 같은 RGB에 다른 감정을 추가하는 경우 충돌 데이터가 되므로 사용자 확인 절차가 있음

## 출력 결과

아래 시각화 결과가 생성/갱신됩니다.

- test/outputs/main_YYYYMMDD_HHMMSS_rgb_3d_distribution.png
- test/outputs/main_YYYYMMDD_HHMMSS_saliency_maps.png
- test/outputs/main_YYYYMMDD_HHMMSS_dominant_color_emotions.png
- test/outputs/comparison_YYYYMMDD_HHMMSS_performance_dashboard.png
- test/outputs/comparison_YYYYMMDD_HHMMSS_knn_rf_color_pair.png

또한 사용자 피드백이 있을 경우 데이터셋 파일이 갱신됩니다.

- test/color_emotion_labeled_updated.csv

## 라이선스 및 고지

- 프로젝트 라이선스: LICENSE
- 서드파티 고지: test/THIRD_PARTY_NOTICES.md
- MIT 라이선스 원문: test/LICENSES/MIT-sophiwoods-color-associations.txt
