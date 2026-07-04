# SentiVision Product Summary

작성일: 2026-06-26
문서 버전: v1.0

## 1. 한 줄 정의
SentiVision은 사용자가 그림을 그리고 색을 고른 뒤, 그 결과를 감정 전시 카드처럼 해석해주는 iPad 우선 프리미엄 감성 컴퓨팅 제품이다.

## 2. 제품 구조

| 구성 | 역할 | 과금 |
|---|---|---|
| iPad 제작 앱 | 드로잉, 색 선택, 감정 전시, 전시 카드 저장 | 유료 |
| iPhone 감상 앱 | 작품과 감정 전시만 감상하는 동반 앱 | 무료 |
| 공용 분석/아카이브 | 색상-감정 분석, 피드백 저장, 기록 보관 | 공통 |

핵심 구조는 단순하다.
- iPad에서 직접 그리고 해석을 만든다.
- iPhone에서는 감상만 한다.
- iPhone 무료 앱이 iPad 유료 제작 앱으로 자연스럽게 이어지는 전환 경로가 된다.

## 3. 핵심 경험
1. 사용자는 iPad 캔버스에서 자유롭게 그림을 그린다.
2. 앱은 선택 색과 구성 요소를 바탕으로 감정 해석을 계산한다.
3. 결과는 단순 예측값이 아니라 전시 해설처럼 제시된다.
4. 사용자는 감정 수정이나 메모를 남겨 결과를 보정할 수 있다.
5. 모든 결과는 한 장의 전시 카드로 아카이브에 쌓인다.
6. iPhone 감상 앱에서는 이 전시 카드만 가볍게 감상한다.

## 4. 제품 원칙
- 감정 해석은 진단이 아니라 전시형 해석으로 표현한다.
- 입력은 텍스트보다 드로잉과 색 선택을 우선한다.
- 결과는 단발성 화면이 아니라 축적 가능한 기록으로 남긴다.
- 프리미엄 톤과 완성도 높은 인터랙션을 유지한다.
- 무료 iPhone 앱은 독립 완결형이 아니라 iPad 앱으로 이어지는 유입 채널이다.

## 5. 범위 요약
### 포함
- iPad 드로잉 기반 감정 전시
- 피드백과 메모 입력
- 개인 아카이브
- 무료 iPhone 감상 앱
- 분석 API와 CLI 검증 엔진

### 제외
- 의료/임상 진단
- 실시간 멀티유저 협업
- iPhone에서의 그림 제작
- 저품질 광고 기반 무료 모델

## 6. 현재 구현 상태
- Python CLI 분석 파이프라인 운영 중
- KNN/KMeans 기반 색상-감정 검증 가능
- 그림 입력용 연구 스크립트에서 `baseline_laplacian`, `paint_region`, `paint_region_conservative` 비교 가능
- 시각화 PNG 및 CSV 보정 루프 존재
- 보강본 CSV(`test/color_emotion_labeled_augmented.csv`)를 기준 데이터로 사용
- 앱/API 설계 문서 정리 완료

## 7. 참고 문서
- PRD: [PRD_SentiVision.md](PRD_SentiVision.md)
- Project Description: [Project_Description.md](Project_Description.md)
- User Journey: [User_Journey_Scenario_SentiVision.md](User_Journey_Scenario_SentiVision.md)
- Wireframe: [Wireframe_SentiVision.md](Wireframe_SentiVision.md)
- ScreenFlow: [ScreenFlow_SentiVision.md](ScreenFlow_SentiVision.md)
- WBS: [WBS_SentiVision.md](WBS_SentiVision.md)
- Development Process: [Development_Process_and_Tools_Proposal.md](Development_Process_and_Tools_Proposal.md)
