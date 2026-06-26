# Docker 기반 배포 파이프라인 전략

## 목표
- 변경 감지 -> 이미지 빌드/검증 -> 레지스트리 푸시 -> 환경별 배포를 일관된 파이프라인으로 자동화
- 배포 직후 헬스체크 및 관측(모니터링/알림)을 표준화

## 파이프라인 단계
1. 소스 변경 감지
- 대상: Dockerfile, docker 디렉터리, 배포 워크플로우 파일
- 트리거: push(main), workflow_dispatch

2. 이미지 빌드
- buildx 기반 멀티아키텍처 확장 가능 구조
- 태그 정책
- latest: 최신 안정 배포 포인터
- sha: 롤백/추적 가능한 불변 태그

3. 컨테이너 실행 검증
- 이미지 빌드 후 임시 컨테이너 실행
- /health 엔드포인트 HTTP 200 확인
- 실패 시 로그 수집 후 파이프라인 중단

4. 레지스트리 푸시
- GHCR 또는 ECR로 푸시
- 최소 권한 토큰 사용

5. 환경 배포
- 대상 런타임(ECS, Cloud Run, Kubernetes 등)으로 롤링 배포
- wait-for-stability를 켜서 완료 여부 확인

6. 사후 검증/모니터링
- 배포 후 외부 헬스체크 URL 호출
- 지표 기반 알람 설정(CPU, Memory, 응답 지연, 5xx)

## 브랜치 전략
- main: production
- feature/*: PR preview (프런트)
- release 태그: 이미지/패키지 버전 고정 배포

## 장애 대응
- sha 태그 이미지로 즉시 롤백
- 알람 발생 시 최근 성공 task definition으로 복구

## 보안 권장사항
- 장기 액세스 키 대신 OIDC + AssumeRole 사용
- 이미지 스캔 결과를 배포 게이트에 반영
- Secrets는 GitHub Secrets/Cloud Secret Manager에 저장
