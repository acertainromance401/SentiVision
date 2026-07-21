import SwiftUI

struct EmotionArchiveView: View {
    let entries: [EmotionArchiveEntry]
    let onSelect: (EmotionArchiveEntry) -> Void

    @State private var selectedEntryID: EmotionArchiveEntry.ID?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                header

                if entries.isEmpty {
                    emptyState
                } else {
                    VStack(spacing: 12) {
                        ForEach(entries) { entry in
                            archiveCard(for: entry)
                        }
                    }
                }
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
            Text("Archive")
                .font(.largeTitle.bold())
            Text("분석과 피드백으로 만들어진 전시 카드를 다시 확인합니다.")
                .foregroundStyle(.secondary)
        }
    }

    private var emptyState: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("아직 저장된 전시 카드가 없습니다.")
                .font(.headline)
            Text("캔버스에서 분석하고 전시 저장을 누르면 여기에 기록이 쌓입니다.")
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(16)
        .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 20, style: .continuous))
    }

    private func archiveCard(for entry: EmotionArchiveEntry) -> some View {
        let isSelected = selectedEntryID == entry.id
        let dateText = entry.createdAt.formatted(date: .abbreviated, time: .shortened)
        let backgroundStyle: AnyShapeStyle = isSelected
            ? AnyShapeStyle(Color.accentColor.opacity(0.12))
            : AnyShapeStyle(.thinMaterial)

        return Button {
            selectedEntryID = entry.id
            onSelect(entry)
        } label: {
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    VStack(alignment: .leading, spacing: 4) {
                        Text(dateText)
                            .font(.headline)
                        Text("예측: \(entry.analysis.predictedEmotion)")
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                    }

                    Spacer()

                    Text("\(Int(entry.analysis.confidence * 100))%")
                        .font(.headline)
                        .foregroundStyle(.secondary)
                }

                Text(entry.analysis.summary)
                    .font(.footnote)
                    .foregroundStyle(.secondary)
                    .lineLimit(2)

                HStack(spacing: 8) {
                    ForEach(entry.analysis.dominantColors.prefix(3)) { color in
                        RoundedRectangle(cornerRadius: 10, style: .continuous)
                            .fill(color.color)
                            .frame(width: 42, height: 24)
                            .overlay(
                                RoundedRectangle(cornerRadius: 10, style: .continuous)
                                    .strokeBorder(.secondary.opacity(0.12), lineWidth: 1)
                            )
                    }
                }

                if !entry.note.isEmpty {
                    Text("메모: \(entry.note)")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .lineLimit(2)
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(16)
            .background(backgroundStyle, in: RoundedRectangle(cornerRadius: 20, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: 20, style: .continuous)
                    .strokeBorder(isSelected ? Color.accentColor.opacity(0.34) : .secondary.opacity(0.16), lineWidth: 1)
            )
        }
        .buttonStyle(.plain)
    }
}