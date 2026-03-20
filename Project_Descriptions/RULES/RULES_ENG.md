# SentiVision iOS Technical Decision Document (Before Development Starts)

## 1) Purpose

This document defines the required tech stack and data strategy before migrating the current Python-based pipeline to an iOS app.

Current implementation baseline:
- Input image analysis
- Saliency-based key region extraction
- Dominant color extraction (KMeans)
- Emotion prediction (KNN)
- Dataset enhancement via user feedback

## 2) Do We Need Server Infrastructure Right Now?

Conclusion: For MVP, on-device only development is feasible without server/cloud.

Required:
- iOS UI framework
- Image processing
- Color clustering
- Emotion classification
- Local storage

Optional:
- Backend API
- Cloud DB
- User accounts/sync

## 3) Recommended Stack (MVP)

### 3.1 App Layer
- UI: SwiftUI
- Async model: async/await
- Architecture: MVVM with separated UseCases

Why:
- Fast implementation
- Strong fit with the iOS native ecosystem
- Easier unit-level testing

### 3.2 Image Processing
- Vision + Core Image
- Optional: Accelerate(vDSP) for optimization

Roles:
- Image resize
- Color space/pixel processing
- Saliency-like feature extraction

### 3.3 Color Extraction/Clustering
- Phase 1: Swift-based KMeans (k=3)
- Optimization: Accelerate-based tuning

### 3.4 Emotion Classification
- Phase 1: Swift distance-based KNN (suitable for small datasets)
- Phase 2: Core ML migration (better performance/maintainability)

## 4) DB Selection

### 4.1 Recommended Priority
1. SwiftData (if targeting iOS 17+)
2. Core Data (if lower iOS versions must be supported)
3. File-based (JSON/CSV) for prototype only

Given the current project context, SwiftData is the most practical choice.

### 4.2 Data to Store
- Analysis logs
  - Image identifier
  - 3 dominant RGB values
  - Predicted emotion
  - User-corrected emotion
  - Timestamp
- Expanded training samples
  - R, G, B
  - emotion
  - source (system/user)

## 5) When Server/Cloud Becomes Necessary

Introduce backend when these needs arise:
- Cross-device sync
- User-specific backup
- Real-time model/label updates
- Operational dashboard/analytics

Candidates:
- Fast start: Firebase or Supabase
- Custom operation: FastAPI + PostgreSQL + Object Storage

## 6) Technology Selection Matrix

### 6.1 Local Storage
- SwiftData
  - Pros: modern iOS integration, concise code
  - Cons: target OS constraint
- Core Data
  - Pros: mature and stable, broad lower-version support
  - Cons: more boilerplate initially

Recommended decision:
- If minimum target is iOS 17+: SwiftData
- If below iOS 17 is included: Core Data

### 6.2 Classification Logic
- Direct Swift KNN implementation
  - Pros: fast MVP, easy to debug
  - Cons: performance can drop as data grows
- Core ML conversion
  - Pros: stronger inference performance and deployment quality
  - Cons: additional model conversion/validation pipeline

Recommended decision:
- Release 1: Swift KNN
- Release 2: Core ML migration

## 7) Recommended Initial Module Composition

- Presentation
  - ImagePickerView
  - AnalysisResultView
  - FeedbackView
- Domain
  - SaliencyExtractor
  - DominantColorExtractor
  - EmotionClassifier
  - SaveFeedbackUseCase
- Data
  - EmotionDatasetRepository
  - AnalysisLogRepository
  - LocalDatabase (SwiftData/Core Data)

## 8) Pre-Development Checklist

- Finalize iOS minimum supported version (17+ or not)
- Finalize local DB choice (SwiftData/Core Data)
- Finalize KNN implementation path (direct vs Core ML)
- Finalize CSV seeding method (bundle seed)
- Finalize privacy policy for image/data storage

## 9) Proposed Next Steps (No Coding Yet)

1. Draft a 1-page product requirements summary
2. Define screen flow (capture/select -> analyze -> feedback -> save)
3. Finalize initial data model
4. Confirm iOS minimum target and DB strategy
5. Start Xcode project setup afterward

## 10) User Decisions Applied (2026-03-18)

The following are now fixed decisions.

1. Emotion categories are fixed.
2. Users choose emotion from a predefined list grouped by higher-level categories (e.g., positive/negative/neutral).
3. User feedback is reflected into the dataset only after validation.
4. Analysis trigger starts as automatic analysis.
5. Development starts offline-first, then adds sharing features for exhibition/gallery scenarios.

## 11) Emotion Taxonomy (Fixed Labels)

### 11.1 Top-Level Groups
- Positive
- Negative
- Neutral

### 11.2 Example Sub-Labels
- Positive: joy, comfort, excitement, hope
- Negative: anxiety, anger, sadness, frustration
- Neutral: calm, neutral/no emotion, focus, observation

Operational rules:
- Do not change the label set during a release cycle.
- If labels must change, migrate by version (e.g., v1 -> v2).

## 12) Policy for Reflecting Feedback After Validation

### 12.1 Why Validation Is Required
- Immediate reflection of impulsive user labels can contaminate the dataset.
- Contaminated samples can quickly degrade model quality.

### 12.2 Reflection Pipeline
1. Store user feedback
2. Compute validation score
3. Queue as reflection candidate
4. Reflect into dataset if threshold is met
5. Store reflection history logs

### 12.3 Validation Score Rules (Draft)
- Score range: 0 to 100
- Components:
  - Agreement score (max 40): higher when user says prediction matches better
  - Reliability score (max 20): higher when recent responses from same user are stable
  - Repeatability score (max 25): higher when similar color clusters repeatedly map to same label
  - Data quality score (max 15): based on input quality (tiny region/noise checks)

Reflection criteria:
- Score >= 70: candidate for reflection
- Score >= 85: immediate reflection allowed
- Score < 70: do not reflect in dataset, store logs only

### 12.4 Additional Safeguards
- Limit max reflections for continuous same-session input (e.g., 20/day)
- Auto-hold when extreme label bias is detected
- Store base dataset and user-reflected dataset separately

## 13) Automatic Analysis Trigger Policy

Default behavior:
- Run analysis automatically after a short delay (e.g., 0.8s) once drawing stops

Exception handling:
- Skip analysis when canvas changes are too small
- Debounce analysis calls during continuous drawing to avoid over-triggering

UX notes:
- Show status indicator (analyzing/completed)
- Provide optional manual "Analyze Again" action

## 14) Offline-First, Then Sharing Expansion Strategy

### 14.1 Phase 1 (Offline)
- All analysis and storage are on-device
- Save only to local DB (SwiftData/Core Data)

### 14.2 Phase 2 (Sharing Features)
- Add exhibition/gallery-oriented sharing capabilities:
  - Artwork upload
  - Emotion tag display
  - Public/private visibility control
  - Curated feed

### 14.3 Phase 3 (Backend Introduction)
- Build backend for sync and sharing
- Recommended setup:
  - API: FastAPI or BaaS(Firebase/Supabase)
  - DB: PostgreSQL
  - Image storage: Object Storage

## 15) Details to Finalize Next

1. Final fixed label set (including Korean/English bilingual support)
2. Exact UI phrasing and 5-point scale definition for agreement question
3. Tuned weights for validation scoring
4. Sharing visibility scope (friends/public) and report/moderation policy
