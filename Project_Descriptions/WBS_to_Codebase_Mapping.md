# WBS-to-Codebase 매핑 및 구현 우선순위

작성일: 2026-03-27  
기준 버전: WBS v1.5, PRD v1.0  

---

## 1. WBS 항목별 코드베이스 매핑

| WBS 항목 | 산출물 | 현재 코드 위치 | 현재 상태 | 필요 작업 |
|---------|--------|-------------|---------|---------|
| **1. 프로젝트 관리** | 주간 계획/회고, 리스크 로그 | 없음 | 미시작 | GitHub Projects 또는 Wiki 설정 |
| **2. 요구사항/문서 정합화** | `Project_Descriptions` 세트 | `Project_Descriptions/*.md` | 완료 (2026-03-25) | 문제 정의 정렬 상태 주간 점검 |
| **3. 캔버스 UX 설계** | 와이어프레임, 화면 흐름도 | `Project_Descriptions/Wireframe_SentiVision.md` | 완료 (설계 단계) | SwiftUI 프로토타입 구현 필요 |
| **4. API 설계/구현** | API 명세, FastAPI 코드 | 설계만 완료 / 구현 미작 | 설계 단계 | FastAPI 프로젝트 생성 + 4.1~4.4 구현 |
| **5. 분석 엔진/데이터 파이프라인** | KNN/KMeans 로직, 데이터 품질 리포트 | `test/main_.py`, `test/test_model_comparison.py` | 진행 중 (CLI) | 엔진 모듈화 + API 연동 + 학습 파이프라인 |
| **6. 피드백 루프** | CSV 업데이트, 피드백 처리 로그 | `test/main_.py`, `test/outputs/comparison_user_feedback.csv` | 진행 중 (CLI) | 앱 피드백 수집 UI + API 엔드포인트 |
| **7. 시각화/리포팅** | RGB 3D, Saliency, 감정-색상 차트, 성능 대시보드 | `test/outputs/` | 완료 (타임스탬프 PNG 생성) | 앱 내 시각화 UI 통합 필요 |
| **8. 테스트/검증** | pytest API 테스트, 사용자 시나리오 테스트 | `test/test_model_comparison.py`, `test/fixed_validation_indices.json` | 진행 중 | `tests/` 폴더 생성 + pytest 작성 |
| **9. 운영/배포 준비** | KPI 수집, DORA 연계, 배포 체크리스트 | 없음 | 미시작 | CI/CD 파이프라인 설정 |

---

## 2. 주요 코드 요소별 상세 매핑

### WBS 5 — 분석 엔진/데이터 파이프라인

#### 현 위치: `test/main_.py`, `test/test_model_comparison.py`

| 함수/로직 | 위치 | 기능 | 상태 | 마이그레이션 경로 |
|---------|------|------|------|---------|
| `emotion_from_rgb(knn_model, r, g, b)` | `test/main_.py` | RGB 0~255 → 감정 예측 | ✅ 완료 | API `/analyze` 엔드포인트의 핵심 로직 |
| KNN 학습 | `test/main_.py` | 데이터셋 기반 KNN 초기화 | ✅ 완료 | 모듈 분리 + 모델 저장/로드 기능 추가 |
| RandomForest 학습 | `test/test_model_comparison.py` | 모델 비교용 보조 분류기 학습 | ✅ 완료 | 실험 트랙 유지 또는 API 후보 모델 평가 |
| KMeans 클러스터링 | `test/main_.py`, `test/test_model_comparison.py` | 현저성 마스크 내 주요색 추출 | ✅ 완료 | 팔레트 정규화 로직과 결합 |
| CSV 업데이트 루프 | `test/main_.py` | 피드백 반영, 중복 제거 | ✅ 완료 | 데이터베이스 또는 API 기반 관리로 전환 |

**MLP 권장사항**: 
- 단계 1: `emotion_from_rgb()` 추출 → `sentipy/models/emotion.py` 
- 단계 2: KNN 모델 저장 → `sentipy/models/knn_model.pkl`
- 단계 3: API 래퍼 → `sentipy/api/routes.py` 에서 호출

---

### WBS 4 — API 설계/구현

#### 목표: FastAPI 구현

| 엔드포인트 | 메서드 | 입력 | 출력 | 현재 상태 | 매핑소스 |
|---------|--------|------|------|---------|---------|
| `/health` | GET | 없음 | `{"status": "ok"}` | 미작 | 기본 헬스체크 |
| `/analyze` | POST | `palette: List[RGB], weights?: List[float]` | `predicted_emotion, confidence_scores, palette_hex` | 미작 | WBS 4.1, FR-2, `emotion_from_rgb()` 활용 |
| `/feedback` | POST | `predicted_emotion, corrected_emotion, palette, note?` | `{"feedback_id": "uuid", "status": "saved"}` | 미작 | WBS 4.2, FR-3, CSV 쓰기 로직 |

**구현 계획**:
- `main.py` (FastAPI 앱 초기화)
- `models.py` (Pydantic 스키마 정의)
- `routes/analyze.py` (분석 엔드포인트, `emotion_from_rgb()` 호출)
- `routes/feedback.py` (피드백 저장, CSV 업데이트)
- `config.py` (환경변수, 모델 경로, 데이터셋 경로)

---

### WBS 3 — 캔버스 UX 설계

#### 현 위치: `Project_Descriptions/Wireframe_SentiVision.md`

| 화면 | 정의 | 필요 SwiftUI 컴포넌트 | 의존성 | 상태 |
|------|------|---------|--------|------|
| HomePage | 최근 감정 + 최근 7일 분석수 + "새 그림 시작" | List, Card, Button | WBS 6 (히스토리 데이터) | 설계 완료 |
| CanvasView | 그리기 영역 + 팔레트 하단 표시 | Canvas, @State palette | iOS 14+ Canvas API | 설계 완료 |
| AnalysisLoading | 단계형 로딩 메시지 | ProgressView, Text | WBS 5 (API 응답) | 설계 완료 |
| ResultCard | 감정 + 점수 + 색상 스와치 | VStack, Rectangle (color) | WBS 5 (API 응답) | 설계 완료 |
| FeedbackForm | 감정 선택 + 메모 입력 | Picker, TextField, Button | WBS 6 (저장) | 설계 완료 |
| HistoryView | 과거 분석 기록 나열 | List, NavigationLink | WBS 6 (데이터 조회) | 설계 완료 |

**구현 계획**:
- 프로토타입: 단계 1 = HomePage + CanvasView (터치 감지, 색상 추출)
- 단계 2 = API 연동 (AnalysisLoading → ResultCard)
- 단계 3 = 피드백 (FeedbackForm)

---

## 3. 의존성 그래프

```
프로젝트 관리 (WBS 1)
    ↓
문서 정합화 (WBS 2) ← 기준선
    ↓
┌─────────────────────────────────────┐
│   병렬 트랙 (4~7주 권장)              │
├─────────────────────────────────────┤
│  • 캔버스 UX 설계 (WBS 3) ─────┐     │
│  • 분석 엔진 모듈화 (WBS 5) ─┐ │    │
│  • 피드백 루프 설계 (WBS 6) ──┼──┐  │
│  • API 설계/구현 (WBS 4) ←····┤ │  │
└───────────────────────────│──┼──┘  │
        ↓                    ↓  ↓      │
    시각화 (WBS 7) ──────────┘  └─────┘
        ↓
    테스트 (WBS 8)
        ↓
    운영/배포 (WBS 9)
```

**핵심 크리티컬 패스**:
1. WBS 2 (문서) — 완료
2. WBS 5 (분석 엔진 모듈화) + WBS 4 (API 구현) — 병렬
3. WBS 3 (캔버스 UX) + WBS 6 (피드백)
4. WBS 7 (시각화 통합) → WBS 8 (테스트) → WBS 9 (배포)

---

## 3.1 문제 정의 반영 체크리스트

- 현황/배경: 텍스트·음성 입력 중심 감정 분석의 마찰 비용이 문서에 명시되어 있는가
- 사용자 문제: 기록 중단, 의도-결과 불일치, 누적 인사이트 부재가 여정에 반영되어 있는가
- 대안 한계: 일반 드로잉 앱 및 단순 색채 심리 정보의 한계가 요구사항에 반영되어 있는가
- 해결 필요성: 저마찰 감정 인터페이스와 피드백 루프의 필요가 KPI 또는 마일스톤에 연결되어 있는가

---

## 4. 구현 우선순위 로드맵

### Phase 1: 기초 (2주, WBS 1~2)
- ✅ 문서 정합화 (완료)
- GitHub Projects 보드 설정
- 팀 온보딩 및 개발 환경 설정

**산출물**: 개발 보드, 환경 설정 완료

---

### Phase 2: 백엔드 + 데이터 (3주, WBS 4~5)

#### Step 1: 분석 엔진 모듈화 (1주)
- `test/main_.py` → `sentipy/models/emotion.py` 추출
- KNN 모델 저장 (`.pkl` 또는 ONNX)
- 데이터 로더 + 정규화 로직 모듈화
- 단위 테스트 작성

**코드 예**:
```python
# sentipy/models/emotion.py
def emotion_from_rgb(model, r, g, b):
    """Returns emotion label for RGB triplet."""
    ...

def load_knn_model(model_path):
    """Load pre-trained KNN model."""
    ...

# sentipy/data/loader.py
def load_dataset(csv_path):
    """Load and normalize dataset."""
    ...
```

#### Step 2: FastAPI 프로젝트 생성 (1주)
```
sentipy/
├── main.py                 # FastAPI 앱
├── config.py              # 환경 변수
├── models.py              # Pydantic 스키마
├── routes/
│   ├── __init__.py
│   ├── analyze.py         # POST /analyze
│   └── feedback.py        # POST /feedback
├── schemas/
│   └── emotion.py
└── tests/
    └── test_routes.py
```

#### Step 3: API 엔드포인트 구현 (1주)
- `/health` (GET) — 상태 확인
- `/analyze` (POST) — palette → emotion (1번 호출당 ~100ms)
- `/feedback` (POST) — CSV 업데이트

**산출물**: 로컬 테스트 완료 FastAPI 서버

---

### Phase 3: 프론트엔드 기초 (2주, WBS 3)

#### Step 1: 프로토타입 (1주)
- HomePage (최근 분석 표시)
- CanvasView (기본 드로잉)
- 터치 → RGB 추출 로직

#### Step 2: API 연동 (1주)
- URL 설정 (localhost/production)
- AnalysisLoading UI
- ResultCard 렌더링
- 에러 처리

**산출물**: iOS 시뮬레이터에서 분석 요청 → 결과 표시 동작 확인

---

### Phase 4: 피드백 + 히스토리 (2주, WBS 6)

#### Step 1: 피드백 수집 (1주)
- FeedbackForm (감정 수정 + 메모)
- 로컬 저장소 (SwiftData 또는 Core Data)

#### Step 2: 히스토리 조회 (1주)
- HistoryView (과거 분석 기록)
- 필터링/정렬

**산출물**: 앱 내 피드백 루프 완성

---

### Phase 5: 시각화 + 테스트 (2주, WBS 7~8)

#### Step 1: 시각화 통합 (1주)
- ResultCard에 감정 점수 그래프 추가
- 색상 팔레트 시각화 (RGB 스와치)

#### Step 2: 테스트 작성 (1주)
- API unit test (pytest)
- iOS UI 시나리오 테스트
- CLI 회귀 테스트 (`test/main_.py` 검증)
- 고정 검증 인덱스 기반 모델 비교 테스트 (`test/test_model_comparison.py` 검증)

**산출물**: 테스트 커버리지 70% 이상

---

### Phase 6: 운영/배포 (1주, WBS 9)

#### Step 1: CI/CD 파이프라인 (1주)
- GitHub Actions (FastAPI 배포)
- TestFlight (iOS 빌드 배포)
- KPI 수집 (로그 → 대시보드)

**산출물**: 자동화 배포 체크리스트 완성

---

## 5. 주요 마일스톤

| 마일스톤 | 예상 시점 | 목표 | 검증 방법 |
|---------|---------|------|---------|
| **M1: MVP 준비** | 3주차 | 백엔드 API 완성 + 프론트엔드 프로토타입 | `curl POST /analyze` 성공 |
| **M2: 통합 완성** | 6주차 | 앱 → API 연동 완료 + 피드백 루프 작동 | iOS 시뮬레이터 E2E 테스트 |
| **M3: 품질 검증** | 9주차 | 테스트 커버리지 70% + 버그 수정 | pytest + 사용자 테스트 |
| **M4: 배포 준비** | 12주차 | CI/CD 완성 + 운영 문서 작성 | GitHub Actions 성공 |

---

## 6. 현재 상태 요약 (2026-03-27)

| 항목 | 상태 | 예상 소요 |
|------|------|---------|
| 문서 정합화 | ✅ 완료 | 사료됨 |
| CLI 검증 엔진 | ✅ 완료 | 지속 유지 |
| API 설계 | ✅ 완료 | 사료됨 |
| API 구현 | ⏳ 미시작 | 2~3주 |
| 캔버스 UX 설계 | ✅ 완료 | 사료됨 |
| 캔버스 구현 | ⏳ 미시작 | 2~3주 |
| 피드백 로직 | 🔄 부분 완료 (CLI만) | 1~2주 |
| 테스트 자동화 | 🔄 부분 완료 (CLI 비교 스크립트) | 1~2주 |
| 배포 자동화 | ❌ 미시작 | 1~2주 |

**다음 액션 (즉시)**:
1. FastAPI `main.py` 생성 + `/health` 엔드포인트 구현
2. `test/main_.py` 에서 `emotion_from_rgb()` 추출 → 모듈화
3. iOS 프로토타입 리포 생성 + CanvasView 기본 구현

