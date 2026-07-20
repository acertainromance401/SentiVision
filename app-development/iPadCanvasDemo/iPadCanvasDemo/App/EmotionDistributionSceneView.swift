import SceneKit
import SwiftUI
import UIKit

struct EmotionDistributionPoint: Identifiable {
    let id = UUID()
    let emotion: String
    let red: Int
    let green: Int
    let blue: Int
    let colorName: String?
    let colorLabel: String?

    var normalizedPosition: SCNVector3 {
        SCNVector3(
            ((Float(red) / 255.0) - 0.5) * 2.4,
            ((Float(green) / 255.0) - 0.5) * 2.4,
            ((Float(blue) / 255.0) - 0.5) * 2.4
        )
    }

    var uiColor: UIColor {
        UIColor(
            red: CGFloat(red) / 255.0,
            green: CGFloat(green) / 255.0,
            blue: CGFloat(blue) / 255.0,
            alpha: 1.0
        )
    }
}

enum EmotionDistributionDataStore {
    static func loadBundledPoints() -> [EmotionDistributionPoint] {
        guard let url = Bundle.main.url(forResource: "color_emotion_labeled_augmented", withExtension: "csv") else {
            return fallbackPoints()
        }

        do {
            let content = try String(contentsOf: url, encoding: .utf8)
            return parseCSV(content)
        } catch {
            return fallbackPoints()
        }
    }

    private static func parseCSV(_ csv: String) -> [EmotionDistributionPoint] {
        let lines = csv.split(whereSeparator: \.isNewline).map(String.init)
        guard lines.count > 1 else {
            return fallbackPoints()
        }

        return lines.dropFirst().compactMap { line in
            let parts = line.split(separator: ",", omittingEmptySubsequences: false).map(String.init)
            guard parts.count >= 6 else { return nil }
            guard let red = Int(parts[1]), let green = Int(parts[2]), let blue = Int(parts[3]) else { return nil }

            let emotion = parts[0].trimmingCharacters(in: .whitespacesAndNewlines)
            let colorName = parts[4].trimmingCharacters(in: .whitespacesAndNewlines)
            let colorLabel = parts[5].trimmingCharacters(in: .whitespacesAndNewlines)

            return EmotionDistributionPoint(
                emotion: emotion,
                red: red,
                green: green,
                blue: blue,
                colorName: colorName.isEmpty ? nil : colorName,
                colorLabel: colorLabel.isEmpty ? nil : colorLabel
            )
        }
    }

    private static func fallbackPoints() -> [EmotionDistributionPoint] {
        [
            EmotionDistributionPoint(emotion: "CALMNESS", red: 131, green: 211, blue: 229, colorName: "SKY BLUE", colorLabel: "59"),
            EmotionDistributionPoint(emotion: "TRANQUILITY", red: 164, green: 227, blue: 242, colorName: "PALE BLUE", colorLabel: "36"),
            EmotionDistributionPoint(emotion: "ENERGY", red: 227, green: 107, blue: 35, colorName: "ORANGE", colorLabel: "8"),
            EmotionDistributionPoint(emotion: "MYSTERY", red: 126, green: 26, blue: 160, colorName: "PURPLE", colorLabel: "7"),
            EmotionDistributionPoint(emotion: "HAPPINESS", red: 7, green: 255, blue: 10, colorName: "LIME", colorLabel: "58"),
            EmotionDistributionPoint(emotion: "DEPRESSION", red: 84, green: 82, blue: 75, colorName: nil, colorLabel: nil)
        ]
    }
}

struct EmotionDistributionView: View {
    private let points = EmotionDistributionDataStore.loadBundledPoints()
    private let displayLimit = 120
    @State private var selectedPoint: EmotionDistributionPoint?
    @State private var resetViewToken = UUID()

    private var displayedPoints: [EmotionDistributionPoint] {
        Array(points.prefix(displayLimit))
    }

    private var uniqueEmotionCount: Int {
        Set(points.map { $0.emotion }).count
    }

    private var topEmotionSummary: String {
        let counts = Dictionary(grouping: points, by: { $0.emotion })
            .mapValues { $0.count }
            .sorted { $0.value > $1.value }
            .prefix(3)
            .map { "\($0.key) \($0.value)" }
        return counts.joined(separator: " • ")
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                header
                ZStack(alignment: .topTrailing) {
                    EmotionDistributionSceneView(points: displayedPoints, selectedPoint: $selectedPoint, resetTrigger: resetViewToken)
                        .frame(height: 560)
                        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
                        .overlay(
                            RoundedRectangle(cornerRadius: 24, style: .continuous)
                                .strokeBorder(.secondary.opacity(0.16), lineWidth: 1)
                        )

                    Button {
                        resetViewToken = UUID()
                    } label: {
                        Label("Reset View", systemImage: "arrow.counterclockwise")
                            .font(.caption.weight(.semibold))
                            .padding(.horizontal, 12)
                            .padding(.vertical, 8)
                            .background(.thinMaterial, in: Capsule())
                    }
                    .padding(12)
                }

                if let selectedPoint {
                    selectedPointCard(selectedPoint)
                } else {
                    hintCard
                }

                infoRow
                Text("RGB 축 위에서 개인 분포를 먼저 보고, 탭한 점의 감정-색 정보를 바로 확인할 수 있습니다.")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            }
            .padding()
        }
        .background(
            LinearGradient(
                colors: [Color(.systemGroupedBackground), Color(.secondarySystemGroupedBackground)],
                startPoint: .top,
                endPoint: .bottom
            )
            .ignoresSafeArea()
        )
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Personal RGB 3D Distribution")
                .font(.largeTitle.bold())
            Text("개인 보정 데이터가 쌓일수록 이 분포가 사용자 기준으로 바뀝니다.")
                .foregroundStyle(.secondary)
        }
    }

    private var hintCard: some View {
        Text("점 하나를 탭하면 감정명, RGB 값, 색상명이 표시됩니다.")
            .font(.subheadline)
            .foregroundStyle(.secondary)
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(12)
            .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 16, style: .continuous))
    }

    private func selectedPointCard(_ point: EmotionDistributionPoint) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(point.emotion)
                    .font(.headline)
                Spacer()
                Circle()
                    .fill(Color(red: Double(point.red) / 255.0, green: Double(point.green) / 255.0, blue: Double(point.blue) / 255.0))
                    .frame(width: 18, height: 18)
            }

            Text("RGB(\(point.red), \(point.green), \(point.blue))")
                .font(.subheadline)
            if let colorName = point.colorName, !colorName.isEmpty {
                Text("Color: \(colorName)")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }
            if let colorLabel = point.colorLabel, !colorLabel.isEmpty {
                Text("Label: \(colorLabel)")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(12)
        .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 16, style: .continuous))
    }

    private var infoRow: some View {
        HStack(spacing: 12) {
            summaryChip(title: "Points", value: "\(points.count)")
            summaryChip(title: "Emotions", value: "\(uniqueEmotionCount)")
            summaryChip(title: "Top", value: topEmotionSummary)
        }
    }

    private func summaryChip(title: String, value: String) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title)
                .font(.caption)
                .foregroundStyle(.secondary)
            Text(value)
                .font(.subheadline.weight(.semibold))
                .lineLimit(1)
                .minimumScaleFactor(0.75)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(12)
        .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 16, style: .continuous))
    }
}

struct EmotionDistributionSceneView: UIViewRepresentable {
    let points: [EmotionDistributionPoint]
    @Binding var selectedPoint: EmotionDistributionPoint?
    let resetTrigger: UUID

    func makeUIView(context: Context) -> SCNView {
        let view = SCNView(frame: .zero)
        view.backgroundColor = UIColor.systemBackground
        view.autoenablesDefaultLighting = false
        view.allowsCameraControl = true
        view.antialiasingMode = .multisampling4X
        view.isPlaying = true
        view.preferredFramesPerSecond = 60
        let scene = EmotionDistributionSceneBuilder(points: points).makeScene()
        view.scene = scene
        context.coordinator.attach(to: view, points: points, selectedPoint: $selectedPoint)
        context.coordinator.lastResetTrigger = resetTrigger
        return view
    }

    func makeCoordinator() -> Coordinator {
        Coordinator()
    }

    func updateUIView(_ uiView: SCNView, context: Context) {
        context.coordinator.points = points
        context.coordinator.selectedPoint = $selectedPoint
        if context.coordinator.lastResetTrigger != resetTrigger {
            context.coordinator.lastResetTrigger = resetTrigger
            context.coordinator.resetCamera(on: uiView)
        }
        if uiView.scene == nil {
            uiView.scene = EmotionDistributionSceneBuilder(points: points).makeScene()
        }
    }

    final class Coordinator: NSObject {
        var points: [EmotionDistributionPoint] = []
        var selectedPoint: Binding<EmotionDistributionPoint?>?
        var lastResetTrigger: UUID?
        private weak var view: SCNView?

        func attach(to view: SCNView, points: [EmotionDistributionPoint], selectedPoint: Binding<EmotionDistributionPoint?>) {
            self.view = view
            self.points = points
            self.selectedPoint = selectedPoint

            if view.gestureRecognizers?.contains(where: { $0 is UITapGestureRecognizer }) != true {
                let tap = UITapGestureRecognizer(target: self, action: #selector(handleTap(_:)))
                view.addGestureRecognizer(tap)
            }
        }

        func resetCamera(on view: SCNView) {
            guard let cameraNode = view.scene?.rootNode.childNode(withName: "mainCamera", recursively: true) else { return }
            cameraNode.position = SCNVector3(0.0, 0.0, 5.4)
            cameraNode.eulerAngles = SCNVector3(0.0, 0.0, 0.0)
            view.pointOfView = cameraNode
            view.defaultCameraController.target = SCNVector3Zero
        }

        @objc private func handleTap(_ gesture: UITapGestureRecognizer) {
            guard let view = view else { return }
            let location = gesture.location(in: view)
            let hits = view.hitTest(location, options: [SCNHitTestOption.searchMode: SCNHitTestSearchMode.all.rawValue])
            guard let hitNode = hits.first?.node else { return }

            let tappedEmotion = hitNode.name ?? hitNode.parent?.name
            guard let tappedEmotion else { return }

            let selected = points.first(where: { $0.emotion == tappedEmotion })
            if let selected {
                selectedPoint?.wrappedValue = selected
            }
        }

        func resetSelection() {
            selectedPoint?.wrappedValue = nil
        }
    }
}

final class EmotionDistributionSceneBuilder {
    private let points: [EmotionDistributionPoint]

    init(points: [EmotionDistributionPoint]) {
        self.points = points
    }

    func makeScene() -> SCNScene {
        let scene = SCNScene()
        scene.background.contents = UIColor.systemBackground

        let rootNode = SCNNode()
        scene.rootNode.addChildNode(rootNode)

        addLights(to: rootNode)
        addAxes(to: rootNode)
        addGrid(to: rootNode)
        addPoints(to: rootNode)
        addCamera(to: scene)

        return scene
    }

    private func addCamera(to scene: SCNScene) {
        let cameraNode = SCNNode()
        cameraNode.camera = SCNCamera()
        cameraNode.position = SCNVector3(0.0, 0.0, 5.4)
        cameraNode.name = "mainCamera"
        scene.rootNode.addChildNode(cameraNode)
    }

    private func addLights(to root: SCNNode) {
        let ambient = SCNLight()
        ambient.type = .ambient
        ambient.intensity = 850
        ambient.color = UIColor(white: 0.95, alpha: 1)

        let ambientNode = SCNNode()
        ambientNode.light = ambient
        root.addChildNode(ambientNode)

        let omni = SCNLight()
        omni.type = .omni
        omni.intensity = 1200

        let omniNode = SCNNode()
        omniNode.light = omni
        omniNode.position = SCNVector3(2.0, 4.0, 6.0)
        root.addChildNode(omniNode)
    }

    private func addAxes(to root: SCNNode) {
        addLine(from: SCNVector3(-1.3, -1.3, -1.3), to: SCNVector3(1.3, -1.3, -1.3), color: .systemRed, root: root)
        addLine(from: SCNVector3(-1.3, -1.3, -1.3), to: SCNVector3(-1.3, 1.3, -1.3), color: .systemGreen, root: root)
        addLine(from: SCNVector3(-1.3, -1.3, -1.3), to: SCNVector3(-1.3, -1.3, 1.3), color: .systemBlue, root: root)

        addAxisLabel(text: "R", position: SCNVector3(1.45, -1.28, -1.28), color: .systemRed, root: root)
        addAxisLabel(text: "G", position: SCNVector3(-1.28, 1.45, -1.28), color: .systemGreen, root: root)
        addAxisLabel(text: "B", position: SCNVector3(-1.28, -1.28, 1.45), color: .systemBlue, root: root)
    }

    private func addGrid(to root: SCNNode) {
        for offset in stride(from: -1.2, through: 1.2, by: 0.4) {
            addGridLine(from: SCNVector3(offset, -1.3, -1.3), to: SCNVector3(offset, 1.3, -1.3), root: root)
            addGridLine(from: SCNVector3(-1.3, offset, -1.3), to: SCNVector3(1.3, offset, -1.3), root: root)
            addGridLine(from: SCNVector3(-1.3, -1.3, offset), to: SCNVector3(1.3, -1.3, offset), root: root)
            addGridLine(from: SCNVector3(-1.3, offset, -1.3), to: SCNVector3(-1.3, offset, 1.3), root: root)
            addGridLine(from: SCNVector3(-1.3, -1.3, offset), to: SCNVector3(-1.3, 1.3, offset), root: root)
            addGridLine(from: SCNVector3(offset, -1.3, -1.3), to: SCNVector3(offset, -1.3, 1.3), root: root)
        }
    }

    private func addPoints(to root: SCNNode) {
        let grouped = Dictionary(grouping: points, by: { $0.emotion })
        let sortedEmotionNames = grouped.keys.sorted()

        for emotion in sortedEmotionNames {
            guard let emotionPoints = grouped[emotion] else { continue }
            for (index, point) in emotionPoints.enumerated() {
                let sphere = SCNSphere(radius: 0.04)
                sphere.segmentCount = 14
                sphere.firstMaterial?.diffuse.contents = point.uiColor
                sphere.firstMaterial?.lightingModel = .physicallyBased
                sphere.firstMaterial?.roughness.contents = 0.25
                sphere.firstMaterial?.metalness.contents = 0.05

                let node = SCNNode(geometry: sphere)
                node.position = point.normalizedPosition
                node.name = point.emotion
                root.addChildNode(node)

                if index < 2 {
                    addEmotionLabel(point, at: point.normalizedPosition, root: root)
                }
            }
        }
    }

    private func addEmotionLabel(_ point: EmotionDistributionPoint, at position: SCNVector3, root: SCNNode) {
        let text = SCNText(string: point.emotion, extrusionDepth: 0.01)
        text.flatness = 0.25
        text.font = UIFont.systemFont(ofSize: 5.5, weight: .semibold)
        text.firstMaterial?.diffuse.contents = UIColor(white: 0.1, alpha: 0.88)
        text.firstMaterial?.emission.contents = UIColor(white: 0.95, alpha: 0.2)

        let textNode = SCNNode(geometry: text)
        textNode.scale = SCNVector3(0.03, 0.03, 0.03)
        textNode.position = SCNVector3(position.x + 0.03, position.y + 0.06, position.z + 0.03)
        textNode.constraints = [SCNBillboardConstraint()]
        root.addChildNode(textNode)
    }

    private func addAxisLabel(text: String, position: SCNVector3, color: UIColor, root: SCNNode) {
        let textGeometry = SCNText(string: text, extrusionDepth: 0.01)
        textGeometry.flatness = 0.2
        textGeometry.font = UIFont.systemFont(ofSize: 7, weight: .bold)
        textGeometry.firstMaterial?.diffuse.contents = color

        let node = SCNNode(geometry: textGeometry)
        node.scale = SCNVector3(0.05, 0.05, 0.05)
        node.position = position
        node.constraints = [SCNBillboardConstraint()]
        root.addChildNode(node)
    }

    private func addLine(from start: SCNVector3, to end: SCNVector3, color: UIColor, root: SCNNode) {
        let line = lineNode(from: start, to: end, color: color, radius: 0.008)
        root.addChildNode(line)
    }

    private func addGridLine(from start: SCNVector3, to end: SCNVector3, root: SCNNode) {
        let line = lineNode(from: start, to: end, color: UIColor.secondaryLabel.withAlphaComponent(0.12), radius: 0.003)
        root.addChildNode(line)
    }

    private func lineNode(from start: SCNVector3, to end: SCNVector3, color: UIColor, radius: CGFloat) -> SCNNode {
        let vector = SCNVector3(end.x - start.x, end.y - start.y, end.z - start.z)
        let height = CGFloat(sqrt((vector.x * vector.x) + (vector.y * vector.y) + (vector.z * vector.z)))

        let cylinder = SCNCylinder(radius: radius, height: height)
        cylinder.firstMaterial?.diffuse.contents = color
        cylinder.firstMaterial?.lightingModel = .physicallyBased

        let node = SCNNode(geometry: cylinder)
        node.position = SCNVector3((start.x + end.x) / 2, (start.y + end.y) / 2, (start.z + end.z) / 2)
        node.eulerAngles = lineEulerAngles(from: vector)
        return node
    }

    private func lineEulerAngles(from vector: SCNVector3) -> SCNVector3 {
        let length = sqrt((vector.x * vector.x) + (vector.y * vector.y) + (vector.z * vector.z))
        guard length > 0 else {
            return SCNVector3(0, 0, 0)
        }

        let dx = vector.x / length
        let dy = vector.y / length
        let dz = vector.z / length
        let axis = SCNVector3(-dz, 0, dx)
        let angle = acos(dy)
        return SCNVector3(axis.x * angle, axis.y * angle, axis.z * angle)
    }
}
