# Discussions Category Design

GitHub Discussions 운영 카테고리 설계안입니다.

## Target Categories

- Announcements: 릴리즈/운영 공지
- General: 일반 커뮤니티 대화
- Ideas: 기능 제안 및 RFC 접수
- Q&A: 사용/설치/오류 문의
- Polls: 의사결정 투표
- Show and tell: 결과 공유

## Logical Extensions (운영 규약)

GitHub API 제약으로 커스텀 카테고리 자동 생성은 어려우므로, 아래를 라벨/접두어로 운영합니다.

- RFC: `Ideas` 카테고리 + 제목 접두어 `[RFC]`
- Support: `Q&A` 카테고리 사용
- Operations: `Announcements` 또는 `General` + 태그 `[OPS]`

## Moderation Rules

- RFC는 배경, 제안, 대안, 영향 분석 필수
- Q&A는 재현 절차/환경 정보 필수
- 운영 공지는 SLA/상태 변화 수치 포함 권장

## Related Docs

- [Development Guide](Development-Guide.md)
- [Troubleshooting](Troubleshooting.md)
