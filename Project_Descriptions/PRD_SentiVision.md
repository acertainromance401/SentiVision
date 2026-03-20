# PRD: SentiVision

작성일: 2026-03-20  
문서 버전: v1.1

## 1. 제품 개요
SentiVision은 입력 이미지의 주요 색상을 추출하고, RGB-감정 라벨 데이터셋을 바탕으로 감정을 예측하는 Python 기반 CLI 프로젝트다.

## 2. 문제 정의
- 이미지 색감이 전달하는 정서 톤을 정량적으로 확인하기 어렵다.
- 감정 예측 결과를 사용자가 직접 정정하고 데이터셋에 반영하는 루프가 필요하다.

## 3. 목표
- 입력 이미지에서 주요 색상 3개를 추출한다.
- 각 주요 색상에 대한 감정 예측 결과를 출력한다.
- 시각화 결과를 파일로 저장한다.
- 사용자 피드백을 통해 데이터셋을 확장한다.

## 4. 비목표 (Out of Scope)
- 의료/임상 목적의 감정 진단
- 실시간 서비스형 API 운영
- 모바일 앱 UI 제공

## 5. 타겟 사용자
- 색채 기반 감정 분석을 실험해보고 싶은 개발자/학습자
- 시각화 결과와 함께 색상-감정 매핑을 점검하고 싶은 사용자

## 6. 현재 구현 기준 사용자 흐름
1. 사용자는 스크립트를 실행한다: `python test/main_.py`
2. 이미지 경로를 입력한다.
3. 시스템은 현저성 기반 픽셀 추출 + KMeans로 주요 색상을 계산한다.
4. KNN으로 각 색상의 감정을 예측해 콘솔에 출력한다.
5. 시각화 이미지를 `test/outputs/`에 저장한다.
6. 사용자가 예측을 정정하면 `test/color_emotion_labeled_updated.csv`에 반영한다.

## 7. 기능 요구사항

### FR-1. 데이터 로딩
- 시스템은 `test/color_emotion_labeled_updated.csv`를 로드해야 한다.
- RGB 값을 0~1 범위로 정규화해야 한다.

### FR-2. 감정 분류 모델
- 시스템은 KNeighborsClassifier(`n_neighbors=3`)를 학습해야 한다.
- 주요 색상 RGB 입력에 대해 감정 라벨을 예측해야 한다.

### FR-3. 이미지 분석
- 시스템은 입력 이미지를 로드하고 리사이즈(100x100)해야 한다.
- Laplacian 기반 현저성 마스크를 생성해야 한다.
- KMeans(`k=3`)로 주요 색상을 추출해야 한다.

### FR-4. 결과 시각화
- 시스템은 아래 산출물을 생성해야 한다.
  - `test/outputs/rgb_3d_distribution.png`
  - `test/outputs/saliency_maps.png`
  - `test/outputs/dominant_color_emotions.png`

### FR-5. 사용자 피드백 반영
- 사용자 입력이 Enter/yes/y/예 인 경우 CSV를 수정하지 않는다.
- 다른 감정 텍스트 입력 시 `(R, G, B, emotion)` 레코드를 CSV에 추가한다.
- 중복 레코드(`R,G,B,emotion`)는 제거해야 한다.

## 8. 비기능 요구사항
- 성능: 단일 이미지 분석이 로컬 환경에서 실용적인 시간 내 완료되어야 한다.
- 안정성: 잘못된 이미지 경로 입력 시 오류 메시지를 출력하고 종료해야 한다.
- 재현성: 동일 입력에서 동일 랜덤 시드(`KMeans random_state=42`)로 유사한 결과를 제공해야 한다.
- 컴플라이언스: 데이터셋 라이선스/출처 고지 문서를 유지해야 한다.

## 9. 기술 스택 및 범위
- 언어: Python
- 주요 라이브러리: pandas, numpy, scikit-learn, opencv-python, matplotlib
- 실행 형태: 단일 CLI 스크립트 (`test/main_.py`)

## 10. 성공 지표 (KPI)
- 실행 성공률: 정상 이미지 입력 기준 스크립트 완주 비율
- 피드백 반영률: 예측 정정 입력이 CSV에 반영되는 비율
- 산출물 생성률: 3개 시각화 파일 생성 성공 비율

## 11. 마일스톤 (현실화 버전)
- M1: 데이터셋 로딩/학습/예측 파이프라인 안정화
- M2: 시각화 산출물 품질 개선
- M3: 피드백 루프 안정화 및 데이터 품질 정리
- M4: API/앱 연동을 위한 인터페이스 분리(향후)

## 12. 데이터셋 및 관련 파일
- 주 데이터셋: `test/color_emotion_labeled_updated.csv`
- 보조 데이터셋: `test/colorassociations_warmth - colorwarmth.csv`
- 서드파티 고지: `test/THIRD_PARTY_NOTICES.md`
- 라이선스 원문: `test/LICENSES/MIT-sophiwoods-color-associations.txt`
