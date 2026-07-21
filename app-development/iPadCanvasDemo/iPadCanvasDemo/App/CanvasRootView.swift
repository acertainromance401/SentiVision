import PencilKit
import SwiftUI

struct CanvasRootView: View {
    private enum Tab: Hashable {
        case distribution
        case canvas
        case archive
    }

    private enum ToolMode: String, CaseIterable {
        case pen = "Pen"
        case eraser = "Eraser"
    }

    private let palette: [Color] = [
        .black, .red, .orange, .yellow, .green, .mint, .blue, .indigo, .purple, .pink, .brown
    ]

    @AppStorage(SentiVisionStorageKey.setupCompleted) private var setupCompleted = false
    @AppStorage(SentiVisionStorageKey.profileName) private var profileName = ""
    @AppStorage(SentiVisionStorageKey.baselineEmotion) private var baselineEmotion = "CALMNESS"
    @AppStorage(SentiVisionStorageKey.baselineColorHex) private var baselineColorHex = "7FD3E5"
    @AppStorage(SentiVisionStorageKey.perceptionStrength) private var perceptionStrength = 0.65

    @State private var drawing = PKDrawing()
    @State private var selectedColor: Color = .black
    @State private var strokeWidth: CGFloat = 8
    @State private var toolMode: ToolMode = .pen
    @State private var activeTab: Tab = .distribution
    @State private var showingSetup = false
    @State private var currentAnalysis: EmotionAnalysisResult?
    @State private var archiveEntries: [EmotionArchiveEntry] = EmotionArchiveStore.load()
    @State private var analysisErrorMessage: String?

    var body: some View {
        Group {
            if setupCompleted {
                mainContent
            } else {
                InitialSetupView {
                    setupCompleted = true
                }
            }
        }
        .sheet(isPresented: $showingSetup) {
            InitialSetupView {
                showingSetup = false
                setupCompleted = true
            }
        }
        .alert("분석할 수 없습니다", isPresented: Binding(
            get: { analysisErrorMessage != nil },
            set: { if !$0 { analysisErrorMessage = nil } }
        )) {
            Button("확인", role: .cancel) {
                analysisErrorMessage = nil
            }
        } message: {
            Text(analysisErrorMessage ?? "캔버스에 최소한 하나의 선을 그려주세요.")
        }
    }

    private var mainContent: some View {
        VStack(spacing: 0) {
            profileBanner

            TabView(selection: $activeTab) {
                EmotionDistributionView(
                    analysisResult: currentAnalysis,
                    onSaveToArchive: saveCurrentAnalysis,
                    onStartNewArtwork: {
                        activeTab = .canvas
                    }
                )
                    .tabItem {
                        Label("Analysis", systemImage: "sparkles")
                    }
                    .tag(Tab.distribution)

                NavigationStack {
                    VStack(spacing: 16) {
                        DrawingCanvasView(
                            drawing: $drawing,
                            selectedColor: selectedColor,
                            strokeWidth: strokeWidth,
                            isEraser: toolMode == .eraser
                        )
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                        .background(Color.white)
                        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
                        .overlay(
                            RoundedRectangle(cornerRadius: 24, style: .continuous)
                                .strokeBorder(.secondary.opacity(0.18), lineWidth: 1)
                        )
                        .padding(.horizontal)
                        .padding(.top)

                        controlPanel
                            .padding(.horizontal)
                            .padding(.bottom, 12)
                    }
                    .background(
                        LinearGradient(
                            colors: [Color(.systemGroupedBackground), Color(.secondarySystemGroupedBackground)],
                            startPoint: .top,
                            endPoint: .bottom
                        )
                        .ignoresSafeArea()
                    )
                    .navigationTitle("iPad Canvas")
                    .toolbar {
                        ToolbarItem(placement: .topBarTrailing) {
                            Button("Setup") {
                                showingSetup = true
                            }
                        }
                        ToolbarItem(placement: .topBarTrailing) {
                            Button("Clear") {
                                drawing = PKDrawing()
                            }
                        }
                    }
                }
                .tabItem {
                    Label("Canvas", systemImage: "pencil.and.outline")
                }
                .tag(Tab.canvas)

                EmotionArchiveView(entries: archiveEntries, onSelect: { entry in
                    currentAnalysis = entry.analysis
                    activeTab = .distribution
                })
                .tabItem {
                    Label("Archive", systemImage: "tray.full")
                }
                .tag(Tab.archive)
            }
        }
    }

    private var profileBanner: some View {
        HStack(spacing: 12) {
            Circle()
                .fill(Color(hex: baselineColorHex) ?? .mint)
                .frame(width: 44, height: 44)

            VStack(alignment: .leading, spacing: 4) {
                Text(profileName.isEmpty ? "새 개인 프로필" : profileName)
                    .font(.headline)
                Text("기준 감정 \(baselineEmotion) · 체감 강도 \(Int(perceptionStrength * 100))%")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }

            Spacer()

            Button("Edit") {
                showingSetup = true
            }
            .buttonStyle(.bordered)
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 12)
        .background(.ultraThinMaterial)
    }

    private var controlPanel: some View {
        VStack(alignment: .leading, spacing: 12) {
            toolButtons
            paletteHeader
            colorPalette
            strokeWidthControl
            actionButtons
        }
        .padding(16)
        .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 20, style: .continuous))
    }

    private var actionButtons: some View {
        HStack(spacing: 8) {
            Button("Analyze Artwork") {
                analyzeArtwork()
            }
            .buttonStyle(.borderedProminent)

            Button("Archive") {
                activeTab = .archive
            }
            .buttonStyle(.bordered)

            Spacer(minLength: 0)
        }
    }

    private var toolButtons: some View {
        HStack(spacing: 8) {
            ForEach(ToolMode.allCases, id: \.self) { mode in
                Button(mode.rawValue) {
                    toolMode = mode
                }
                .buttonStyle(.borderedProminent)
                .tint(toolMode == mode ? .accentColor : .secondary)
            }

            Spacer(minLength: 0)
        }
    }

    private var paletteHeader: some View {
        Text(toolMode == .pen ? "Color" : "Eraser mode")
            .font(.headline)
    }

    private var colorPalette: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 10) {
                ForEach(Array(palette.enumerated()), id: \.offset) { index, color in
                    paletteButton(color: color, index: index)
                }
            }
            .padding(.vertical, 2)
        }
    }

    private func paletteButton(color: Color, index: Int) -> some View {
        Button {
            selectedColor = color
            toolMode = .pen
        } label: {
            Circle()
                .fill(color)
                .frame(width: 30, height: 30)
                .overlay(
                    Circle()
                        .strokeBorder(selectedColor == color ? Color.primary : Color.clear, lineWidth: 3)
                )
        }
        .buttonStyle(.plain)
        .accessibilityLabel("Color \(index + 1)")
    }

    private var strokeWidthControl: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text("Thickness")
                Spacer()
                Text("\(Int(strokeWidth)) pt")
                    .foregroundStyle(.secondary)
            }
            Slider(value: $strokeWidth, in: 2...24, step: 1)
        }
    }

    private func analyzeArtwork() {
        guard let analysis = LocalEmotionAnalysisService.shared.analyze(
            drawing: drawing,
            baselineEmotion: baselineEmotion,
            baselineColorHex: baselineColorHex
        ) else {
            analysisErrorMessage = "캔버스에 그려진 내용이 없어 분석할 수 없습니다."
            return
        }

        currentAnalysis = analysis
        activeTab = .distribution
    }

    private func saveCurrentAnalysis() {
        guard let analysis = currentAnalysis else { return }

        let entry = EmotionArchiveEntry(
            id: UUID(),
            createdAt: Date(),
            analysis: analysis,
            note: ""
        )

        archiveEntries.insert(entry, at: 0)
        EmotionArchiveStore.save(archiveEntries)
        activeTab = .archive
    }
}
