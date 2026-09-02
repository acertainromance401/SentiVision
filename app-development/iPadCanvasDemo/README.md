# iPadCanvasDemo

SentiVision iPad demo app source.

Last verified: 2026-09-02

## Features

- **3D Emotion Distribution Visualization**: Displays 120+ emotion points in 3D RGB color space
- **Emotion Family Classification**: Integrates emotion-to-family mappings (primary/secondary roles)
- **Point Cloud Rendering**: Clean visualization with only colored sphere points (no axes/grid/labels)
- **PencilKit Canvas**: Integrated drawing interface with pen, eraser, color palette, and stroke control
- **On-device Analysis**: Extracts foreground pixels, clusters up to three dominant colors, and maps them to bundled emotion samples
- **Emotion Exhibition**: Shows interpretation, confidence, dominant colors, emotion scores, and family summary
- **Local Archive**: Saves and reopens exhibition cards with `UserDefaults`

## Folder Layout

- `iPadCanvasDemo.xcodeproj` - Xcode project
- `iPadCanvasDemo/iPadCanvasDemo/App` - app source files
  - `EmotionDistributionSceneView.swift` - 3D SceneKit visualization with emotion point rendering
  - `CanvasRootView.swift` - Main tab container and analysis flow
  - `LocalEmotionAnalysisService.swift` - On-device color and emotion analysis
  - `EmotionArchiveView.swift` - Local exhibition archive
- `iPadCanvasDemo/iPadCanvasDemo/Data` - bundled CSV data
  - `color_emotion_labeled_augmented.csv` - 120+ emotion points with RGB values
  - `emotion_family_classification.csv` - emotion-to-family mappings (10 families, 120+ emotions)
- `iPadCanvasDemo/iPadCanvasDemo/Info.plist` - app configuration

## Build & Run

### Xcode IDE
1. Open `app-development/iPadCanvasDemo/iPadCanvasDemo.xcodeproj` in Xcode
2. Select scheme: `iPadCanvasDemo`
3. Select destination: iPad (real device or simulator)
4. Build & Run: `⌘R`

### Command Line (Real Device)
```bash
cd app-development/iPadCanvasDemo
xcodebuild -project iPadCanvasDemo.xcodeproj \
  -scheme iPadCanvasDemo \
  -destination 'platform=iOS,id=<DEVICE_ID>' \
  build
```

## Data Integration

### Emotion Points CSV
Located: `iPadCanvasDemo/Data/color_emotion_labeled_augmented.csv`
- Format: `emotion, R, G, B, color_name, color_label`
- Usage: Loaded into `EmotionDistributionPoint` struct with normalized 3D positions (-1.2 to 1.2 range)

### Emotion Family Classification CSV
Located: `iPadCanvasDemo/Data/emotion_family_classification.csv`
- Format: `emotion, family, role, weight, sample_count`
- Families (10 total): 고요, 활력, 신비, 권위, 긴장, 연결, 온기, 회복, 집중, 그늘
- Roles: `primary` (weight 1.0) or `secondary` (weight 0.65)
- Usage: Enables future emotion family clustering/filtering

## Architecture

### EmotionDistributionSceneView
- **UIViewRepresentable** wrapper for SceneKit visualization
- **EmotionDistributionSceneBuilder**: Constructs 3D scene with lights, camera, and emotion points
- **Point Rendering**: 0.04-radius colored spheres per emotion
- **Data Flow**: 
  1. Load emotion points from CSV
  2. Load emotion family memberships from CSV
  3. Normalize positions to 3D space
  4. Render points with per-emotion RGB color

### Current Features
- ✅ 3D point cloud rendering (120+ emotions)
- ✅ Dynamic camera setup (0,0,5.4 position)
- ✅ Clean point-only visualization (no visual clutter)
- ✅ Emotion family data integration
- ✅ Real device deployment
- ✅ First-run profile and baseline setup
- ✅ PencilKit drawing to local analysis flow
- ✅ Result exhibition and local archive

### Deferred/Experimental Features
- ⏸️ Emotion family network overlay (lines connecting points to family centroids) - Currently disabled
- ⏸️ Family-based point clustering visualization
- ⏸️ Interactive point selection/detail view
- ⏸️ Corrected emotion and note feedback
- ⏸️ Advanced color wheel/HEX/RGB/eyedropper input
- ⏸️ Remote API sync, authentication, and database storage

## Notes

- Target: iPad (iOS 16.0+)
- Build Config: Debug
- Device Signing: Apple Development Team (VQZUAA6R4Z)
- Tested on: iPad (M3)
