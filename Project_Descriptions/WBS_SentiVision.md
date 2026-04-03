# WBS: SentiVision

작성일: 2026-03-27  
문서 버전: v1.5

## 1. 개요
본 WBS는 PRD(v1.0) 의도에 맞춰 캔버스 기반 감성 분석 앱 개발을 중심으로 작업을 분해한다. 현재 CLI 파이프라인은 검증 트랙으로 병행 유지한다.

## 2. WBS 구조

### 1. 프로젝트 관리
1.1 마일스톤/우선순위 관리  
1.2 주간 진행 점검  
1.3 리스크/이슈 관리

산출물
- 주간 계획/회고
- 리스크 로그

---

### 2. 요구사항/문서 정합화
2.1 PRD 기반 용어/범위 통일  
2.2 User Journey/Wireframe/WBS 동기화  
2.3 데이터셋 프로파일 업데이트  
2.4 문제 정의 반영 점검 (현황/페인포인트/대안 한계/해결 필요성)

산출물
- `Project_Descriptions` 문서 세트

---

### 3. 캔버스 UX 설계
3.1 홈/새 그림 시작 화면 설계  
3.2 캔버스 입력/팔레트 표시 UX 설계  
3.3 색상 선택 다양화 UX 설계 (색상휠/HEX/RGB/프리셋/스포이트)  
3.4 결과/히스토리 화면 설계

산출물
- 와이어프레임
- 화면 흐름도
- ScreenFlow 문서

---

### 4. API 설계/구현
4.1 `POST /analyze` 스키마 설계  
4.2 `POST /feedback` 스키마 설계  
4.3 `GET /health` 구현  
4.4 입력 유효성 검증 로직 구현

산출물
- API 명세
- FastAPI 서비스 코드(목표)

---

### 5. 분석 엔진/데이터 파이프라인
5.1 KNN 학습/예측 로직 유지  
5.2 현저성 + KMeans 주요색 추출 유지  
5.3 데이터 정규화/오탈자 매핑 정책 적용  
5.4 결측/중복 처리 정책 반영  
5.5 모델 비교 파이프라인(KNN vs RandomForest) 운영

산출물
- `test/main_.py`
- `test/test_model_comparison.py`
- `test/run_all_analysis.py`
- 데이터 품질 리포트

---

### 6. 피드백 루프
6.1 앱 피드백 수집/저장  
6.2 CSV 반영 규칙 적용  
6.3 품질 개선 로그 기록

산출물
- `test/color_emotion_labeled_updated.csv`
- 피드백 처리 로그

---

### 7. 시각화/리포팅
7.1 RGB 3D 분포 산출  
7.2 Saliency 맵 산출  
7.3 주요 색상-감정 산출  
7.4 성능 비교 대시보드 산출

산출물
- `test/outputs/main_YYYYMMDD_HHMMSS_rgb_3d_distribution.png`
- `test/outputs/main_YYYYMMDD_HHMMSS_saliency_maps.png`
- `test/outputs/main_YYYYMMDD_HHMMSS_dominant_color_emotions.png`
- `test/outputs/comparison_YYYYMMDD_HHMMSS_performance_dashboard.png`
- `test/outputs/comparison_YYYYMMDD_HHMMSS_knn_rf_color_pair.png`

---

### 8. 테스트/검증
8.1 API 테스트(pytest)  
8.2 앱 사용자 시나리오 테스트  
8.3 CLI 회귀 테스트  
8.4 고정 검증 인덱스 기반 모델 비교 테스트

산출물
- 테스트 리포트

---

### 9. 운영/배포 준비
9.1 KPI 수집 체계 정리  
9.2 DORA 워크플로 연계  
9.3 배포 체크리스트 정리

산출물
- 운영 지표 문서
- 배포 체크리스트

## 3. 주차별 매핑(권장)
- 1~4주: 1, 2, 3, 4
- 5~8주: 4, 5, 6
- 9~12주: 6, 7, 8
- 13~16주: 8, 9

## 4. 시각화: 작업 흐름

```mermaid
flowchart LR
  A[문서 정합화] --> B[캔버스 UX 설계]
  B --> C[API 구현]
  C --> D[분석/데이터 품질 게이트]
  D --> E[피드백 루프]
  E --> F[테스트/운영]
```
