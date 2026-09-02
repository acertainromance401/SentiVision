# app-development

이 폴더에는 현재 iPad용 데모 앱이 들어 있습니다.

최종 검증일: 2026-09-02

## Contents

- `iPadCanvasDemo/` - SwiftUI, PencilKit, SceneKit으로 만든 SentiVision iPad 데모

## Implemented Flow

1. 개인 프로필, 기준 감정·색상, 체감 강도를 설정합니다.
2. PencilKit 캔버스에서 기본 팔레트와 펜 도구로 그림을 그립니다.
3. 앱이 온디바이스에서 전경 픽셀, 최대 3개 대표색, 감정과 감정 패밀리를 계산합니다.
4. 결과와 3D RGB 분포를 확인하고 전시 카드를 로컬 아카이브에 저장합니다.

Node API는 이 앱에 연결되어 있지 않으며 별도의 배포·관측성 프로토타입입니다. 감정 수정·메모, 고급 색상 선택, 개인 분포 학습 반영은 후속 작업입니다.

## Open

1. `app-development/iPadCanvasDemo/iPadCanvasDemo.xcodeproj` 를 Xcode에서 엽니다.
2. `iPadCanvasDemo` 스킴을 선택합니다.
3. iPad 실기기 또는 Simulator에서 실행합니다. 최근 검증은 iPad 실기기를 기준으로 수행했습니다.
