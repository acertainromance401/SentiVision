# Troubleshooting

자주 발생하는 문제와 해결 방법입니다.

## 1) `gh` 인증/권한 오류

증상:

- `gh api` 호출 시 `401` 또는 권한 부족

해결:

```bash
gh auth status
gh auth refresh -s repo -s project -s read:org
```

## 2) Python 의존성 충돌 (SciPy/Numpy)

증상:

- `A NumPy version >=... is required for this version of SciPy`

해결:

```bash
source .venv/bin/activate
pip install "numpy<2.3" "scipy>=1.11" -U
pip install -U scikit-learn pandas matplotlib
```

## 3) PR 생성 시 본문 깨짐

증상:

- 한글 본문이 터미널 인코딩 영향으로 깨짐

해결:

```bash
gh pr create --title "..." --body-file /tmp/pr_body.md
```

## 4) Branch protection API 422

증상:

- `gh api`의 `-f key=null` 전송 시 스키마 에러

해결:

- JSON 파일을 만들어 `curl -d @file.json`로 전송

## Next Docs

- 설치/첫 실행: [Getting Started](Getting-Started.md)
- 개발 표준: [Development Guide](Development-Guide.md)
