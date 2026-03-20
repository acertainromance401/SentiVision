# SentiVision Project Description

작성일: 2026-03-20  
통합 문서 버전: v1.1

## 문서 바로가기
- 개발 과정/도구 제안서: [Development_Process_and_Tools_Proposal.md](Development_Process_and_Tools_Proposal.md)
- PRD: [PRD_SentiVision.md](PRD_SentiVision.md)
- WBS: [WBS_SentiVision.md](WBS_SentiVision.md)
- Wireframe: [Wireframe_SentiVision.md](Wireframe_SentiVision.md)
- User Journey: [User_Journey_Scenario_SentiVision.md](User_Journey_Scenario_SentiVision.md)

---

## 1. 프로젝트 한눈에 보기
SentiVision은 단일 Python 스크립트 기반의 이미지 색상-감정 분석 프로젝트다.

현재 구현 범위
- 입력 이미지 분석: 현저성 기반 주요 영역 추출
- 색상 추출: KMeans로 주요 색상 3개 도출
- 감정 예측: RGB 기반 KNN 분류
- 시각화 출력: 3종 PNG 파일 생성
- 사용자 피드백 반영: 데이터셋 CSV 갱신

---

## 2. 실행 및 산출물

실행 파일
- `test/main_.py`

입력 데이터
- `test/color_emotion_labeled_updated.csv`
- `test/colorassociations_warmth - colorwarmth.csv`

실행 명령
```bash
python test/main_.py
```

출력 파일
- `test/outputs/rgb_3d_distribution.png`
- `test/outputs/saliency_maps.png`
- `test/outputs/dominant_color_emotions.png`

---

## 3. 문서 통합 요약

### 3-1. PRD 요약
- 핵심 목표: 이미지 색상 기반 감정 예측 + 피드백 루프
- 현재 형태: API/앱이 아닌 로컬 CLI 분석 도구
- 확장 방향: 분석 모듈 분리 후 API/앱 연계

### 3-2. WBS 요약
- 기획/요구사항 정리
- 분석 파이프라인 안정화
- 테스트/품질 관리
- 문서화 및 운영 지표 관리

### 3-3. Wireframe 요약
- 실제 구현은 UI가 아닌 CLI이므로, Wireframe은 향후 UI 단계의 설계 문서로 유지

### 3-4. User Journey 요약
- 실제 사용자 여정은 "스크립트 실행 -> 이미지 입력 -> 결과 확인 -> 피드백 반영" 흐름

---

## 4. 시스템 구성 (현재)

### 4-1. 분석 로직
- 데이터셋 로딩/정규화
- KNN 분류기 학습
- 이미지 전처리 및 현저성 추출
- KMeans 기반 주요 색상 클러스터링

### 4-2. 결과 표현
- 콘솔 로그: 예측 감정 및 정확도
- 시각화 파일: RGB 분포, 현저성 맵, 주요 색상-감정 결과

### 4-3. 데이터 갱신 정책
- 사용자 정정 입력이 있을 때만 CSV 갱신
- 중복 레코드(`R,G,B,emotion`) 제거

---

## 5. 운영/컴플라이언스
- 데이터 출처 및 라이선스 고지는 [test/THIRD_PARTY_NOTICES.md](../test/THIRD_PARTY_NOTICES.md)와 [test/LICENSES/MIT-sophiwoods-color-associations.txt](../test/LICENSES/MIT-sophiwoods-color-associations.txt) 기준으로 관리
- 저장소의 DORA 지표 워크플로는 [README.md](../README.md) 기준으로 운영

---

## 6. 최종 수용 기준
- 문서의 범위가 실제 구현(스크립트 기반 분석)과 일치한다.
- 입력/출력 파일 경로가 현재 저장소 구조와 일치한다.
- 향후 확장(API/UI)은 현재 구현과 분리해 명시한다.
