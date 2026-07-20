import SwiftUI

enum SentiVisionStorageKey {
    static let setupCompleted = "sentivision.setup.completed"
    static let profileName = "sentivision.profile.name"
    static let baselineEmotion = "sentivision.profile.baselineEmotion"
    static let baselineColorHex = "sentivision.profile.baselineColorHex"
    static let perceptionStrength = "sentivision.profile.perceptionStrength"
}

struct InitialSetupView: View {
    private let onComplete: () -> Void
    private let baselineEmotionOptions = [
        "CALMNESS",
        "TRANQUILITY",
        "ENERGY",
        "HAPPINESS",
        "SERENITY",
        "TENDERNESS",
        "NOSTALGIA",
        "FOCUS",
        "RELIEF",
        "CURIOSITY"
    ]

    @AppStorage(SentiVisionStorageKey.setupCompleted) private var setupCompleted = false
    @AppStorage(SentiVisionStorageKey.profileName) private var profileName = ""
    @AppStorage(SentiVisionStorageKey.baselineEmotion) private var baselineEmotion = "CALMNESS"
    @AppStorage(SentiVisionStorageKey.baselineColorHex) private var baselineColorHex = "7FD3E5"
    @AppStorage(SentiVisionStorageKey.perceptionStrength) private var perceptionStrength = 0.65

    @State private var draftProfileName = ""
    @State private var draftBaselineEmotion = "CALMNESS"
    @State private var draftBaselineColor = Color(hex: "7FD3E5") ?? .mint
    @State private var draftPerceptionStrength = 0.65

    init(onComplete: @escaping () -> Void) {
        self.onComplete = onComplete
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                header
                profileCard
                baselineCard
                perceptionCard
                actionCard
            }
            .padding()
        }
        .background(
            LinearGradient(
                colors: [Color(.systemGroupedBackground), Color(.secondarySystemGroupedBackground)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()
        )
        .onAppear(perform: loadDrafts)
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Initial Setup")
                .font(.largeTitle.bold())
            Text("개인 프로필, 기준 감정, 기준 색상, 체감 강도를 먼저 정해두면 이후 분포와 캔버스 해석이 이 기준을 따라갑니다.")
                .foregroundStyle(.secondary)
        }
    }

    private var profileCard: some View {
        setupCard(title: "Personal Profile", systemImage: "person.crop.circle") {
            VStack(alignment: .leading, spacing: 12) {
                TextField("프로필 이름", text: $draftProfileName)
                    .textFieldStyle(.roundedBorder)

                Text("앱 안에서 이 기준이 사용자 고유 분포의 출발점이 됩니다.")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            }
        }
    }

    private var baselineCard: some View {
        setupCard(title: "Baseline", systemImage: "dial.high") {
            VStack(alignment: .leading, spacing: 12) {
                Picker("기준 감정", selection: $draftBaselineEmotion) {
                    ForEach(baselineEmotionOptions, id: \.self) { emotion in
                        Text(emotion).tag(emotion)
                    }
                }
                .pickerStyle(.menu)

                ColorPicker("기준 색상", selection: $draftBaselineColor, supportsOpacity: false)

                HStack(spacing: 12) {
                    Circle()
                        .fill(draftBaselineColor)
                        .frame(width: 34, height: 34)
                    VStack(alignment: .leading, spacing: 3) {
                        Text("선택한 기준이 그래프와 피드백 카드의 출발점이 됩니다.")
                            .font(.footnote)
                            .foregroundStyle(.secondary)
                        Text(hexDescription(for: draftBaselineColor))
                            .font(.caption.monospaced())
                            .foregroundStyle(.secondary)
                    }
                    Spacer()
                }
            }
        }
    }

    private var perceptionCard: some View {
        setupCard(title: "Perception Strength", systemImage: "slider.horizontal.3") {
            VStack(alignment: .leading, spacing: 12) {
                Slider(value: $draftPerceptionStrength, in: 0.35...1.25, step: 0.05)
                HStack {
                    Text("조금 완만")
                    Spacer()
                    Text("표준")
                    Spacer()
                    Text("더 강하게")
                }
                .font(.caption)
                .foregroundStyle(.secondary)

                Text(perceptionSummary(for: draftPerceptionStrength))
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            }
        }
    }

    private var actionCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Button {
                saveDrafts()
                onComplete()
            } label: {
                Text(setupCompleted ? "Update Profile" : "Start")
                    .font(.headline)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 14)
            }
            .buttonStyle(.borderedProminent)

            Button {
                loadDrafts()
            } label: {
                Text("Reset Draft")
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 10)
            }
            .buttonStyle(.bordered)
        }
        .padding(16)
        .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 24, style: .continuous))
    }

    private func setupCard<Content: View>(title: String, systemImage: String, @ViewBuilder content: () -> Content) -> some View {
        VStack(alignment: .leading, spacing: 14) {
            Label(title, systemImage: systemImage)
                .font(.headline)
            content()
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 24, style: .continuous))
    }

    private func loadDrafts() {
        draftProfileName = profileName
        draftBaselineEmotion = baselineEmotion
        draftBaselineColor = Color(hex: baselineColorHex) ?? .mint
        draftPerceptionStrength = perceptionStrength
    }

    private func saveDrafts() {
        profileName = draftProfileName.trimmingCharacters(in: .whitespacesAndNewlines)
        baselineEmotion = draftBaselineEmotion
        baselineColorHex = hexString(for: draftBaselineColor)
        perceptionStrength = draftPerceptionStrength
        setupCompleted = true
    }

    private func perceptionSummary(for value: Double) -> String {
        switch value {
        case ..<0.55:
            return "입력보다 약간 보수적으로 반응하도록 맞춥니다."
        case ..<0.85:
            return "기본 체감에 가까운 균형형 설정입니다."
        default:
            return "색과 감정의 차이를 더 강하게 느끼도록 맞춥니다."
        }
    }

    private func hexDescription(for color: Color) -> String {
        hexString(for: color)
    }

    private func hexString(for color: Color) -> String {
        let uiColor = UIColor(color)
        var red: CGFloat = 0
        var green: CGFloat = 0
        var blue: CGFloat = 0
        uiColor.getRed(&red, green: &green, blue: &blue, alpha: nil)
        return String(format: "%02X%02X%02X", Int(red * 255), Int(green * 255), Int(blue * 255))
    }
}

extension Color {
    init?(hex: String) {
        let cleaned = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        guard cleaned.count == 6, let value = Int(cleaned, radix: 16) else {
            return nil
        }

        let red = Double((value >> 16) & 0xFF) / 255.0
        let green = Double((value >> 8) & 0xFF) / 255.0
        let blue = Double(value & 0xFF) / 255.0
        self.init(red: red, green: green, blue: blue)
    }
}
