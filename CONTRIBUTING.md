# Contributing to SentiVision

SentiVision 프로젝트에 기여해주셔서 감사합니다!  
이 문서는 코드 기여 방법, 브랜치 전략, 커밋 규칙을 안내합니다.

---

## 목차
1. [브랜치 전략](#1-브랜치-전략)
2. [Conventional Commits](#2-conventional-commits)
3. [Pull Request 가이드](#3-pull-request-가이드)
4. [코드 리뷰 가이드](#4-코드-리뷰-가이드)
5. [개발 환경 설정](#5-개발-환경-설정)
6. [테스트 실행](#6-테스트-실행)

---

## 1. 브랜치 전략

**GitHub Flow** 기반으로 운영합니다.

```
main
 └─ feat/<issue-number>-<short-description>   # 기능 개발
 └─ fix/<issue-number>-<short-description>    # 버그 수정
 └─ refactor/<short-description>              # 리팩터링
 └─ docs/<short-description>                  # 문서 작업
 └─ chore/<short-description>                 # 설정/빌드 변경
```

### 브랜치 명명 규칙

| 접두사 | 용도 | 예시 |
|--------|------|------|
| `feat/` | 새 기능 | `feat/10-model-pipeline` |
| `fix/` | 버그 수정 | `fix/14-emotion-consistency` |
| `refactor/` | 리팩터링 | `refactor/knn-module` |
| `docs/` | 문서 | `docs/api-reference` |
| `chore/` | 빌드/CI | `chore/update-dependencies` |

### 작업 흐름

```bash
# 1. 최신 main에서 브랜치 생성
git switch main && git pull origin main
git switch -c feat/10-model-pipeline

# 2. 작업 후 커밋
git add <files>
git commit -m "feat(model): add KNN pipeline with normalization"

# 3. Push 및 PR 생성
git push origin feat/10-model-pipeline
gh pr create --title "feat(model): add KNN pipeline" --body-file .github/PULL_REQUEST_TEMPLATE.md
```

---

## 2. Conventional Commits

커밋 메시지는 **[Conventional Commits](https://www.conventionalcommits.org/)** 규칙을 따릅니다.

### 형식

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### Type 목록

| Type | 설명 |
|------|------|
| `feat` | 새로운 기능 추가 |
| `fix` | 버그 수정 |
| `refactor` | 기능 변경 없는 코드 개선 |
| `test` | 테스트 추가/수정 |
| `docs` | 문서 수정 |
| `chore` | 빌드, 패키지, 설정 변경 |
| `perf` | 성능 개선 |
| `ci` | CI/CD 파이프라인 변경 |

### Scope 예시

`model`, `api`, `data`, `ui`, `infra`, `test`, `analytics`

### 커밋 예시

```bash
# 기능
git commit -m "feat(model): add RGB normalization to KNN classifier"

# 버그 수정
git commit -m "fix(model): resolve inconsistent emotion prediction on edge colors"

# 리팩터링
git commit -m "refactor(data): extract preprocessing pipeline to separate module"

# Breaking Change
git commit -m "feat(api)!: change /analyze response schema to include confidence score"
```

### 금지 사항

```bash
# ❌ 나쁜 예
git commit -m "fix bug"
git commit -m "수정"
git commit -m "WIP"

# ✅ 좋은 예
git commit -m "fix(api): handle None return from KNN prediction"
```

---

## 3. Pull Request 가이드

### PR 생성 전 체크리스트

- [ ] `main`에서 최신 변경사항을 rebase했는가?
- [ ] 자체 코드 리뷰를 완료했는가?
- [ ] 관련 테스트를 추가/수정했는가?
- [ ] PR 템플릿을 모두 작성했는가?

### PR 크기 가이드

| 크기 | 변경 라인 수 | 권장사항 |
|------|------------|---------|
| Small | < 100줄 | 적극 권장 |
| Medium | 100~300줄 | 허용 |
| Large | 300~500줄 | 분리 권고 |
| XL | > 500줄 | 반드시 분리 |

### PR 제목 형식

```
<type>(<scope>): <subject> (#issue-number)
```

예: `feat(model): add color emotion pipeline with KNN (#10)`

---

## 4. 코드 리뷰 가이드

### 리뷰 태그 시스템

모든 리뷰 코멘트는 아래 태그로 시작합니다:

| 태그 | 의미 | 처리 |
|------|------|------|
| `[MUST]` | 반드시 수정 필요 — 머지 블로킹 | 수정 후 재요청 |
| `[SHOULD]` | 강력 권고 — 수정 권장 | 수정 or 근거 설명 |
| `[CONSIDER]` | 개선 제안 — 선택적 | 논의 후 결정 |
| `[QUESTION]` | 이해를 위한 질문 | 답변 필수 |
| `[PRAISE]` | 잘 된 부분 칭찬 | — |
| `[NIT]` | 미세한 스타일 지적 | 무시 가능 |

### 리뷰 코멘트 예시

```markdown
[MUST] 이 함수는 `img is None`일 때 예외 처리가 없습니다.
`sys.exit()` 대신 `ValueError`를 raise하여 호출자가 처리할 수 있도록 해주세요.

[SHOULD] KNN의 `n_neighbors=3`이 하드코딩되어 있습니다.
환경 변수나 설정 파일로 분리하는 것을 권장합니다.

[CONSIDER] 이 부분은 `@functools.lru_cache`를 적용하면 반복 호출 시 성능이 향상될 수 있습니다.

[QUESTION] `salient_mask` 임계값(10)의 근거가 있나요? 실험값인지 궁금합니다.
```

### 리뷰어 기대사항

1. **24시간 내** 첫 리뷰 시작 (최소 `[QUESTION]` 이상)
2. 코드뿐 아니라 **테스트, 문서**도 리뷰
3. 부정적 피드백은 **코드**를 지적하되, **사람**을 지적하지 않음
4. 승인(Approve) 기준: `[MUST]` 항목 모두 해소

### PR 작성자 기대사항

1. `[MUST]` 코멘트는 **반드시** 수정 후 `Resolved` 처리
2. `[SHOULD]` 미수용 시 이유를 코멘트로 설명
3. 큰 수정 후 **re-request review** 필수

---

## 5. 개발 환경 설정

```bash
# 리포지토리 클론
git clone https://github.com/acertainromance401/SentiVision.git
cd SentiVision

# 가상환경 생성 및 활성화
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일 수정
```

### 주요 의존성

| 패키지 | 버전 | 용도 |
|--------|------|------|
| `opencv-python` | ≥4.8 | 이미지 처리 |
| `scikit-learn` | ≥1.3 | KNN 모델 |
| `pandas` | ≥2.0 | 데이터 처리 |
| `matplotlib` | ≥3.7 | 시각화 |
| `numpy` | ≥1.24 | 수치 연산 |

---

## 6. 테스트 실행

```bash
# 전체 테스트
python3 -m pytest test/ -v

# 특정 테스트
python3 -m pytest test/test_model_comparison.py -v

# 커버리지 포함
python3 -m pytest test/ --cov=src --cov-report=term-missing
```

---

## 문의

이슈나 질문은 [GitHub Issues](https://github.com/acertainromance401/SentiVision/issues)에 등록해주세요.  
라벨 `question` 또는 `documentation`을 사용하면 빠른 응답을 받을 수 있습니다.
