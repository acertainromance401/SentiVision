# TDD Red-Green-Refactor Notes

## Scope
- feature flags
- environment/target-user toggles
- A/B stable assignment
- experiment event tracking
- package export contract

## Cycle Summary
1. Red
- 각 기능별 기대 동작을 Jest 테스트로 먼저 정의
- 초기 상태에서 테스트 실패를 기준선으로 사용

2. Green
- `src/featureFlags.js`, `src/abTesting.js`, `src/eventTracker.js`, `index.js` 구현/보완
- 테스트를 통과시키는 최소 변경 적용

3. Refactor
- env key 매핑(`FLAG_REALTIME_MOOD_HINTS`) 안정화
- 테스트 픽스처/모듈 초기화(`jest.resetModules`)로 부작용 제거
- 커버리지 임계치(80%)를 설정해 회귀 방지

## Core Features Covered (5+)
1. unknown flag safety fallback
2. env var based toggle on/off
3. target user based toggle enable
4. deterministic A/B assignment consistency
5. unknown experiment error handling
6. exposure event log persistence
7. package export compatibility checks
