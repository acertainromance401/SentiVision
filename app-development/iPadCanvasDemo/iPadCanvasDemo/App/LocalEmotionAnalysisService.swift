import Foundation
import PencilKit
import SwiftUI
import UIKit

struct RGBColor: Codable, Hashable, Identifiable {
    var red: Int
    var green: Int
    var blue: Int

    var id: String {
        hexString
    }

    var hexString: String {
        String(format: "#%02X%02X%02X", red, green, blue)
    }

    var color: Color {
        Color(red: Double(red) / 255.0, green: Double(green) / 255.0, blue: Double(blue) / 255.0)
    }

    func distance(to other: RGBColor) -> Double {
        let redDelta = Double(red - other.red)
        let greenDelta = Double(green - other.green)
        let blueDelta = Double(blue - other.blue)
        return (redDelta * redDelta) + (greenDelta * greenDelta) + (blueDelta * blueDelta)
    }
}

struct EmotionSample: Codable, Hashable {
    let emotion: String
    let color: RGBColor
    let colorName: String?
    let colorLabel: String?
}

struct EmotionScore: Codable, Hashable, Identifiable {
    let emotion: String
    let confidence: Double

    var id: String {
        emotion
    }
}

struct EmotionClusterPrediction: Codable, Hashable, Identifiable {
    let color: RGBColor
    let predictedEmotion: String
    let confidence: Double
    let pixelCount: Int

    var id: String {
        "\(color.hexString)-\(predictedEmotion)"
    }
}

struct EmotionAnalysisResult: Codable, Hashable, Identifiable {
    let id: UUID
    let predictedEmotion: String
    let confidence: Double
    let interpretation: String
    let summary: String
    let baselineEmotion: String
    let dominantColors: [RGBColor]
    let clusterPredictions: [EmotionClusterPrediction]
    let scores: [EmotionScore]
    let createdAt: Date
}

struct EmotionArchiveEntry: Codable, Hashable, Identifiable {
    let id: UUID
    let createdAt: Date
    let analysis: EmotionAnalysisResult
    let note: String
}

enum EmotionArchiveStore {
    private static let storageKey = "sentivision.local.archive.entries"

    static func load() -> [EmotionArchiveEntry] {
        guard let data = UserDefaults.standard.data(forKey: storageKey) else {
            return []
        }

        do {
            return try JSONDecoder().decode([EmotionArchiveEntry].self, from: data)
        } catch {
            return []
        }
    }

    static func save(_ entries: [EmotionArchiveEntry]) {
        guard let data = try? JSONEncoder().encode(entries) else {
            return
        }
        UserDefaults.standard.set(data, forKey: storageKey)
    }
}

final class LocalEmotionAnalysisService {
    static let shared = LocalEmotionAnalysisService()

    private let samples: [EmotionSample]

    private init() {
        samples = LocalEmotionAnalysisService.loadSamples()
    }

    func analyze(drawing: PKDrawing, baselineEmotion: String, baselineColorHex: String) -> EmotionAnalysisResult? {
        guard !drawing.strokes.isEmpty else {
            return nil
        }

        let renderBounds = drawing.bounds.isEmpty
            ? CGRect(x: 0, y: 0, width: 1024, height: 768)
            : drawing.bounds.insetBy(dx: -24, dy: -24)
        let renderedImage = drawing.image(from: renderBounds, scale: 1.0)
        let foregroundPixels = Self.extractForegroundPixels(from: renderedImage)
        guard !foregroundPixels.isEmpty else {
            return nil
        }

        let uniqueCount = Set(foregroundPixels).count
        let clusterCount = max(1, min(3, uniqueCount, foregroundPixels.count))
        let clusters = Self.kMeans(pixels: foregroundPixels, clusterCount: clusterCount)
        let clusterPredictions = clusters.map { cluster -> EmotionClusterPrediction in
            let prediction = self.predictEmotion(for: cluster.center)
            return EmotionClusterPrediction(
                color: cluster.center,
                predictedEmotion: prediction.emotion,
                confidence: prediction.confidence,
                pixelCount: cluster.members.count
            )
        }

        let dominantColors = clusters
            .sorted { $0.members.count > $1.members.count }
            .map { $0.center }

        var aggregateWeights: [String: Double] = [:]
        for prediction in clusterPredictions {
            aggregateWeights[prediction.predictedEmotion, default: 0] += Double(prediction.pixelCount) * prediction.confidence
        }

        let sortedScores = aggregateWeights
            .sorted { first, second in
                if first.value == second.value {
                    return first.key < second.key
                }
                return first.value > second.value
            }

        let totalWeight = max(sortedScores.reduce(0) { $0 + $1.value }, 0.0001)
        let scores = sortedScores.map { EmotionScore(emotion: $0.key, confidence: $0.value / totalWeight) }
        let predictedEmotion = scores.first?.emotion ?? baselineEmotion
        let confidence = scores.first?.confidence ?? 0.0

        let interpretation = Self.interpretation(for: predictedEmotion)
        let summary = "\(interpretation) 기준 감정 \(baselineEmotion)과 비교하면 \(predictedEmotion) 방향이 더 강합니다."

        return EmotionAnalysisResult(
            id: UUID(),
            predictedEmotion: predictedEmotion,
            confidence: confidence,
            interpretation: interpretation,
            summary: summary,
            baselineEmotion: baselineEmotion,
            dominantColors: dominantColors,
            clusterPredictions: clusterPredictions,
            scores: scores,
            createdAt: Date()
        )
    }

    private static func loadSamples() -> [EmotionSample] {
        guard let url = Bundle.main.url(forResource: "color_emotion_labeled_augmented", withExtension: "csv"),
              let content = try? String(contentsOf: url, encoding: .utf8) else {
            return fallbackSamples()
        }

        let lines = content.split(whereSeparator: \.isNewline).map(String.init)
        guard lines.count > 1 else {
            return fallbackSamples()
        }

        let rows = lines.dropFirst().compactMap { line -> EmotionSample? in
            let parts = line.split(separator: ",", omittingEmptySubsequences: false).map(String.init)
            guard parts.count >= 4,
                  let red = Int(parts[1]),
                  let green = Int(parts[2]),
                  let blue = Int(parts[3]) else {
                return nil
            }

            let emotion = normalizeEmotionLabel(parts[0])
            let colorName = parts.count > 4 ? trimOrNil(parts[4]) : nil
            let colorLabel = parts.count > 5 ? trimOrNil(parts[5]) : nil
            return EmotionSample(
                emotion: emotion,
                color: RGBColor(red: red, green: green, blue: blue),
                colorName: colorName,
                colorLabel: colorLabel
            )
        }

        return rows.isEmpty ? fallbackSamples() : rows
    }

    private static func fallbackSamples() -> [EmotionSample] {
        [
            EmotionSample(emotion: "CALMNESS", color: RGBColor(red: 131, green: 211, blue: 229), colorName: "SKY BLUE", colorLabel: "59"),
            EmotionSample(emotion: "TRANQUILITY", color: RGBColor(red: 164, green: 227, blue: 242), colorName: "PALE BLUE", colorLabel: "36"),
            EmotionSample(emotion: "ENERGY", color: RGBColor(red: 227, green: 107, blue: 35), colorName: "ORANGE", colorLabel: "8"),
            EmotionSample(emotion: "HARMONY", color: RGBColor(red: 29, green: 153, blue: 15), colorName: "GREEN", colorLabel: "14"),
            EmotionSample(emotion: "FOCUS", color: RGBColor(red: 69, green: 104, blue: 240), colorName: "BLUE", colorLabel: "22"),
            EmotionSample(emotion: "TRUST", color: RGBColor(red: 94, green: 182, blue: 162), colorName: "TEAL", colorLabel: "17")
        ]
    }

    private static func trimOrNil(_ value: String) -> String? {
        let trimmed = value.trimmingCharacters(in: .whitespacesAndNewlines)
        return trimmed.isEmpty ? nil : trimmed
    }

    private static let typoMap: [String: String] = [
        "CORWARDICE": "COWARDICE",
        "LONLINESS": "LONELINESS"
    ]

    private static func normalizeEmotionLabel(_ label: String) -> String {
        let normalized = label.trimmingCharacters(in: .whitespacesAndNewlines).uppercased()
        return typoMap[normalized] ?? normalized
    }

    private static func extractForegroundPixels(from image: UIImage) -> [RGBColor] {
        guard let cgImage = image.cgImage else {
            return []
        }

        let width = cgImage.width
        let height = cgImage.height
        guard width > 0, height > 0 else {
            return []
        }

        let bytesPerRow = width * 4
        let byteCount = bytesPerRow * height
        let rawData = UnsafeMutablePointer<UInt8>.allocate(capacity: byteCount)
        defer {
            rawData.deallocate()
        }

        guard let context = CGContext(
            data: rawData,
            width: width,
            height: height,
            bitsPerComponent: 8,
            bytesPerRow: bytesPerRow,
            space: CGColorSpaceCreateDeviceRGB(),
            bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue | CGBitmapInfo.byteOrder32Big.rawValue
        ) else {
            return []
        }

        context.draw(cgImage, in: CGRect(x: 0, y: 0, width: width, height: height))

        var pixels: [RGBColor] = []
        pixels.reserveCapacity(width * height / 3)

        for y in stride(from: 0, to: height, by: 2) {
            for x in stride(from: 0, to: width, by: 2) {
                let offset = (y * bytesPerRow) + (x * 4)
                let red = Int(rawData[offset])
                let green = Int(rawData[offset + 1])
                let blue = Int(rawData[offset + 2])
                let alpha = Int(rawData[offset + 3])

                if alpha < 24 {
                    continue
                }

                let maxChannel = max(red, green, blue)
                let minChannel = min(red, green, blue)
                let saturation = maxChannel == 0 ? 0.0 : Double(maxChannel - minChannel) / Double(maxChannel)
                let isForeground = maxChannel < 245 || saturation > 0.08
                if isForeground {
                    pixels.append(RGBColor(red: red, green: green, blue: blue))
                }
            }
        }

        if pixels.isEmpty {
            for y in stride(from: 0, to: height, by: 2) {
                for x in stride(from: 0, to: width, by: 2) {
                    let offset = (y * bytesPerRow) + (x * 4)
                    let red = Int(rawData[offset])
                    let green = Int(rawData[offset + 1])
                    let blue = Int(rawData[offset + 2])
                    let alpha = Int(rawData[offset + 3])

                    if alpha > 0 {
                        pixels.append(RGBColor(red: red, green: green, blue: blue))
                    }
                }
            }
        }

        return pixels
    }

    private struct Cluster {
        var center: RGBColor
        var members: [RGBColor]
    }

    private static func kMeans(pixels: [RGBColor], clusterCount: Int, iterations: Int = 8) -> [Cluster] {
        let uniquePixels = Array(Set(pixels))
        guard !uniquePixels.isEmpty else {
            return []
        }

        let actualCount = max(1, min(clusterCount, uniquePixels.count))
        var centers = stride(from: 0, to: actualCount, by: 1).map { index in
            uniquePixels[(index * uniquePixels.count) / actualCount]
        }

        for _ in 0..<iterations {
            var buckets = Array(repeating: [RGBColor](), count: centers.count)

            for pixel in pixels {
                guard let index = nearestCenterIndex(pixel, centers: centers) else {
                    continue
                }
                buckets[index].append(pixel)
            }

            var hasChanged = false
            for index in centers.indices {
                guard let meanColor = buckets[index].meanColor else {
                    continue
                }
                if meanColor != centers[index] {
                    centers[index] = meanColor
                    hasChanged = true
                }
            }

            if !hasChanged {
                break
            }
        }

        var clusters: [Cluster] = []
        for center in centers {
            clusters.append(Cluster(center: center, members: []))
        }

        for pixel in pixels {
            guard let index = nearestCenterIndex(pixel, centers: centers) else {
                continue
            }
            clusters[index].members.append(pixel)
        }

        return clusters.filter { !$0.members.isEmpty }
    }

    private static func nearestCenterIndex(_ pixel: RGBColor, centers: [RGBColor]) -> Int? {
        guard !centers.isEmpty else {
            return nil
        }

        var bestIndex = 0
        var bestDistance = Double.greatestFiniteMagnitude

        for (index, center) in centers.enumerated() {
            let distance = pixel.distance(to: center)
            if distance < bestDistance {
                bestDistance = distance
                bestIndex = index
            }
        }

        return bestIndex
    }

    private func predictEmotion(for color: RGBColor) -> (emotion: String, confidence: Double) {
        let nearestNeighbors = samples
            .map { sample in
                (sample: sample, distance: color.distance(to: sample.color))
            }
            .sorted { first, second in
                if first.distance == second.distance {
                    return first.sample.emotion < second.sample.emotion
                }
                return first.distance < second.distance
            }
            .prefix(3)

        var emotionCounts: [String: Int] = [:]
        var distanceSums: [String: Double] = [:]

        for neighbor in nearestNeighbors {
            emotionCounts[neighbor.sample.emotion, default: 0] += 1
            distanceSums[neighbor.sample.emotion, default: 0] += neighbor.distance
        }

        let sortedVotes = emotionCounts.sorted { first, second in
            if first.value == second.value {
                let firstDistance = (distanceSums[first.key] ?? .greatestFiniteMagnitude) / Double(first.value)
                let secondDistance = (distanceSums[second.key] ?? .greatestFiniteMagnitude) / Double(second.value)
                if firstDistance == secondDistance {
                    return first.key < second.key
                }
                return firstDistance < secondDistance
            }
            return first.value > second.value
        }

        let winner = sortedVotes.first?.key ?? "UNKNOWN"
        let confidence = Double(sortedVotes.first?.value ?? 0) / Double(max(nearestNeighbors.count, 1))
        return (winner, confidence)
    }

    private static func interpretation(for emotion: String) -> String {
        switch emotion {
        case "TRANQUILITY":
            return "조용하지만 깊게 번지는 안정의 결이 화면 전반에서 느껴집니다."
        case "CALMNESS":
            return "잔잔한 층이 쌓이며 시선이 천천히 머무르는 톤입니다."
        case "ENERGY":
            return "속도감이 강하고 중심을 앞으로 밀어내는 흐름이 보입니다."
        case "HARMONY":
            return "서로 다른 색이 부딪히지 않고 자연스럽게 이어집니다."
        case "FOCUS":
            return "불필요한 요소를 줄이고 중심 축을 또렷하게 세웁니다."
        case "TRUST":
            return "안정감과 개방감이 동시에 유지되는 톤입니다."
        default:
            return "색의 온도와 대비가 현재 감정의 결을 정리합니다."
        }
    }
}

private extension Array where Element == RGBColor {
    var meanColor: RGBColor? {
        guard !isEmpty else { return nil }
        let count = Double(count)
        let red = Int((map(\.red).reduce(0, +).doubleValue / count).rounded())
        let green = Int((map(\.green).reduce(0, +).doubleValue / count).rounded())
        let blue = Int((map(\.blue).reduce(0, +).doubleValue / count).rounded())
        return RGBColor(red: red, green: green, blue: blue)
    }
}

private extension Int {
    var doubleValue: Double { Double(self) }
}