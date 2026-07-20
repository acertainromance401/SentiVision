# SentiVision Project Description

작성일: 2026-03-25  
통합 문서 버전: v1.6

## 문서 바로가기
- 한 장 요약: [Product_Summary_SentiVision.md](Product_Summary_SentiVision.md)
- 개발 과정/도구 제안서: [Development_Process_and_Tools_Proposal.md](Development_Process_and_Tools_Proposal.md)
- PRD: [PRD_SentiVision.md](PRD_SentiVision.md)
- WBS: [WBS_SentiVision.md](WBS_SentiVision.md)
- Wireframe: [Wireframe_SentiVision.md](Wireframe_SentiVision.md)
- User Journey: [User_Journey_Scenario_SentiVision.md](User_Journey_Scenario_SentiVision.md)

---

## 1. 프로젝트 한눈에 보기
SentiVision은 사용자가 마음껏 그림을 그린 다음, 그 과정에서 선택된 색을 바탕으로 감정을 해석해주는 iPad 우선 프리미엄 앱을 목표로 한다.  
결과는 예측값처럼 제시하지 않고, 작품 옆 해설문처럼 조용하고 사유적인 방식으로 보여준다.

현재 저장소에는 Python CLI 분석 파이프라인이 구현되어 있으며, 이 파이프라인은 앱 동작과 색상-감정 맵핑을 검증하는 기준 엔진으로 유지한다.
최근 연구 기준에서는 원본 baseline과 별도로 `paint_region` 계열의 그림 중심 추출 로직을 실험하고 있으며,
보강본 CSV(`test/color_emotion_labeled_augmented.csv`)를 현재 검증 기준으로 사용한다.
또한 `app-development/iPadCanvasDemo`에는 초기 세팅, 개인 분포, 캔버스 경험을 함께 담은 iPad 데모 앱이 포함되어 있다.
향후에는 iPhone에서 작품만 감상하는 동반 앱을 추가해, 제작 경험과 감상 경험을 분리하는 방향도 고려한다.
이 iPhone 동반 앱은 무료 감상용으로 제공하고, 작품을 직접 그리는 iPad 유료 앱으로 자연스럽게 이어지도록 하는 진입점 역할을 하게 한다.

### 1.1 앱 역할 분리

| 앱 | 역할 | 과금 |
|---|---|---|
| iPad 제작 앱 | 드로잉, 초기 세팅, 감정 전시, 전시 카드 저장 | 유료 |
| iPhone 감상 앱 | 작품과 전시 카드 감상, 아카이브 탐색 | 무료 |
| 공용 계층 | 분석 로직, 피드백 저장, 개인 분포 보정 | 공통 |

문제 정의 정렬 요약 (PRD v1.1 기준)
- 핵심 문제: 사용자가 설명하기 어려운 감정을 그림으로 풀어내고, 그 색을 바탕으로 자연스럽게 해석받을 수 있는 도구가 부족하다.
- 사용자 페인포인트: 텍스트/음성 입력 부담, 그림을 그리는 흐름이 끊기는 경험, 허술한 앱 품질에 대한 거부감.
- 제품 방향: 자유로운 드로잉을 먼저 보장하고, 그 결과를 전시형 아카이브로 누적하는 프리미엄 경험 제공.

현재 구현 범위 (CLI 검증 엔진)
- RGB-감정 CSV 로드 및 KNN 학습
- 현저성 기반 픽셀 추출
- KMeans 주요 색상 3개 추출
- 감정 예측 및 시각화 PNG 3종 생성
- 사용자 피드백 반영을 통한 CSV 갱신
- 모델 비교 스크립트(KNN vs RandomForest) 실행 및 성능 대시보드 생성
- 통합 실행 스크립트로 메인/비교 분석 파이프라인 일괄 실행

목표 구현 범위 (앱/API)
- iPad 우선 캔버스 드로잉 및 이미지 업로드 UI
- 초기 세팅(기준 색상, 기준 감정, 체감 조절)
- 개인 분포 시각화 및 선택 점 상세 표시
- 분석/피드백 계약 연동 가능 구조
- 감정 전시 결과 화면과 개인 아카이브 제공
- 각 작품을 1개의 전시 카드로 저장하는 개인 미술관 경험 제공
- 유료 앱에 맞는 고품질 인터랙션과 프리미엄 UI 마감
- iPhone 감상용 동반 앱으로 전시 카드만 보는 흐름 확장 가능성 확보
- 무료 iPhone 감상 앱에서 유료 iPad 제작 앱으로 유도하는 제품 구조 고려

---

## 2. 제품 구조

### 2-1. 앱 레이어
- Swift/SwiftUI 기반 iPad 캔버스 입력
- 초기 세팅/프로필 UI
- 결과 카드/개인 분포 시각화
- 피드백/기록 UI
- 프리미엄 톤의 타이포그래피, 여백, 애니메이션
- iPhone 감상 전용 화면은 후속 앱으로 분리 가능

### 2-2. API 레이어
- 분석 요청 수신 및 결과 반환
- 피드백 저장 및 품질 루프 반영
- health endpoint 운영

### 2-3. 분석/데이터 레이어 (현행 자산)
- `test/main_.py` 기반 분석 로직 (개선 버전)
- `test/test_model_comparison.py` 기반 모델 성능 비교 로직
- `test/research_compare_extraction.py` 기반 baseline/paint_region 비교 로직
- `test/run_all_analysis.py` 기반 일괄 실행 로직
- `test/color_emotion_labeled_augmented.csv` 기반 학습/예측
- 시각화 산출물 및 데이터셋 갱신

### 2-4. 베이스라인 (원본 비교용)
- `base_model/` 폴더는 개선 전 원본 파이프라인을 보존한다.
- 개선 결과 비교 및 회귀 검증 시 기준선으로 활용한다.

---

## 3. 실행 및 산출물 (현재 기준)

이 섹션의 내용은 모두 `test/` 폴더 아래 검증용 자산을 기준으로 한다.

실행 파일
- `test/main_.py`
- `test/test_model_comparison.py`
- `test/run_all_analysis.py`

입력 데이터
- `test/color_emotion_labeled_updated.csv`
- `test/colorassociations_warmth - colorwarmth.csv`

실행 명령
```bash
python test/main_.py
```

출력 파일
- `test/outputs/main_YYYYMMDD_HHMMSS_rgb_3d_distribution.png`
- `test/outputs/main_YYYYMMDD_HHMMSS_saliency_maps.png`
- `test/outputs/main_YYYYMMDD_HHMMSS_dominant_color_emotions.png`
- `test/outputs/comparison_YYYYMMDD_HHMMSS_performance_dashboard.png`
- `test/outputs/comparison_YYYYMMDD_HHMMSS_knn_rf_color_pair.png`

---

## 4. 문서 통합 요약
- PRD: 색 기반 감정 해석, 전시형 결과 표현, 데이터 품질 게이트 정의
- User Journey: Welcome -> Create -> Interpretation -> Emotional Exhibition -> Archive 흐름 정의
- WBS: 앱/UI, API, 데이터/CLI를 병렬 트랙으로 분해
- Wireframe: 조용한 전시 공간을 닮은 화면 구조와 상호작용 정의
- `test/` 문서: 현재 CLI 검증 절차와 산출물 확인 방법 정의

---

## 5. 시각화: 제품 파이프라인

```mermaid
flowchart LR
  U[사용자 드로잉] --> C[캔버스 팔레트 추출]
  C --> A[POST /analyze]
  A --> R[예측 감정/점수 반환]
  R --> F[피드백 입력]
  F --> P[POST /feedback]
  P --> D[데이터셋 보정]
  D --> V[CLI 검증]
```

---

## 6. 운영/컴플라이언스
- 데이터 출처/라이선스 고지는 [test/THIRD_PARTY_NOTICES.md](../test/THIRD_PARTY_NOTICES.md), [test/LICENSES/MIT-sophiwoods-color-associations.txt](../test/LICENSES/MIT-sophiwoods-color-associations.txt) 기준으로 관리
- 저장소 운영 지표는 [README.md](../README.md)의 DORA 워크플로 가이드를 따른다.

---

## 7. 최종 수용 기준
- 문서 전반이 PRD v1.1의 목적(색 기반 감정 해석과 전시형 경험)을 일관되게 반영한다.
- 앱/API 계획과 CLI 기반 현재 구현 범위를 함께 명시한다.
- 파일 경로와 산출물 설명이 저장소 구조와 일치한다.
