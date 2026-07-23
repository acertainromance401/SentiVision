# Changelog

All notable changes to this project are documented in this file.

## [Unreleased] - iPad Canvas Demo Updates

### Added (iPadCanvasDemo)

- Emotion family classification CSV data (`emotion_family_classification.csv`) with 10 emotion families
  - 120+ emotions mapped to primary/secondary family roles with weighted connections
  - Families: 고요(serenity), 활력(vitality), 신비(mystery), 권위(authority), 긴장(tension), 연결(connection), 온기(warmth), 회복(recovery), 집중(focus), 그늘(shadow)
- Enhanced `EmotionDistributionSceneView.swift` with:
  - `EmotionFamilyMembership` struct for emotion-to-family mapping
  - `loadEmotionFamilyMemberships()` and `parseEmotionFamilyCSV()` for CSV parsing
  - `addFamilyNetworkOverlay()` infrastructure (currently disabled for cleaner UI)
  - Detailed debug logging for data loading and matching

### Changed (iPadCanvasDemo)

- 3D emotion distribution visualization cleaned up:
  - Removed axes, grid lines, and emotion labels for minimal point-cloud display
  - Points now display as 0.04-radius colored spheres (point-only rendering)
  - Maintained RGB normalization (-1.2 to 1.2 range per axis)
- Data pipeline improved:
  - Emotion names now consistently normalized to uppercase for reliable CSV matching
  - Real device deployment workflow established (build → direct device test, skipping simulator)

### Technical Notes

- Real device testing on iPad (M3) with iOS 16.0+
- Emotion data loading: 120+ points from `color_emotion_labeled_augmented.csv`
- Family mapping: integrated but network visualization deferred pending UX refinement
- Build signing: Apple Development Team (VQZUAA6R4Z, VQZUAA6R4Z)

## [1.0.1] - 2026-05-28

### Added

- AI palette analysis API endpoint (`POST /analyze`) in `src/api/server.js`
- Prometheus metrics endpoint (`GET /metrics`) and structured request logs
- Mini eval script (`scripts/mini-eval.js`) for lightweight model behavior checks
- Production runbook with rollback plan (`docs/runbook/production-runbook.md`)
- Observability dashboard guide (`docs/observability/dashboard.md`)
- Retrospective document (`RETROSPECTIVE.md`)
- 3-minute demo script and checklist (`docs/demo/VIDEO_DEMO.md`)

### Changed

- Docker image runtime switched to Node API service for deployable AI endpoint
- Docker Compose now includes API service and Prometheus scrape target
- Build/Test workflow now runs mini eval in CI
- Frontend now includes direct AI analyze demo UI panel
