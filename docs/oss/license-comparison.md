# OSS License Comparison and Selection Criteria

## Goal

SentiVision에 적합한 OSS 라이선스를 선택하기 위해 대표 라이선스를 비교합니다.

## Compared Licenses

| License | Type | Commercial Use | Modification | Patent Grant | Copyleft | Compliance Cost |
|---|---|---|---|---|---|---|
| MIT | Permissive | Yes | Yes | No explicit grant | No | Low |
| Apache-2.0 | Permissive | Yes | Yes | Yes (explicit) | No | Medium |
| GPL-3.0 | Strong Copyleft | Yes | Yes | Implicit/terms-based | Yes (strong) | High |

## Practical Considerations for SentiVision

- 프로젝트 성격: 학습/실험 + 앱/API 확장 가능성이 있는 공개 저장소
- 협업 목표: 외부 기여 장벽을 낮추고, 재사용을 쉽게 해야 함
- 법무/운영 부담: 초기 단계에서는 단순한 컴플라이언스가 유리

## Selection Criteria

1. 기여 허들을 낮추는가
2. 재사용/배포 시 법적 부담이 과도하지 않은가
3. 기업/상용 환경에서 채택 가능성이 높은가
4. 특허 관련 리스크를 어떻게 다루는가

## Recommendation

현재 저장소는 **MIT**를 유지합니다.

근거:

- 초기 커뮤니티 확장에 유리 (가장 단순한 조건)
- 코드 재사용과 실험 속도에 유리
- 현 저장소 운영 수준(소규모/빠른 반복)과 적합

## When to Reconsider

다음 조건이 생기면 Apache-2.0 전환을 검토합니다.

- 외부 기업 협업 증가
- 특허 관련 우려가 현실화
- SDK/API 배포 범위가 커져 라이선스 명확성이 중요해짐

## Decision Log

- Current: MIT (`LICENSE`)
- Next review trigger: 기업 파트너십/상용 연계 시점
