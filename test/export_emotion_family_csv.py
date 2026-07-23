#!/usr/bin/env python3
import csv
from collections import Counter
from pathlib import Path

INPUT_CSV = Path("app-development/iPadCanvasDemo/iPadCanvasDemo/Data/color_emotion_labeled_augmented.csv")
OUTPUT_CSV = Path("test/emotion_family_classification.csv")

FAMILIES = [
    (
        "고요",
        {"CALMNESS", "TRANQUILITY", "SERENITY", "PEACE", "STILLNESS"},
        {"RELIEF", "HARMONY", "BALANCE", "RESERVED", "GROUNDED", "STABILITY", "SECURITY"},
    ),
    (
        "온기",
        {"TENDERNESS", "LOVE", "ROMANCE", "COMFORT", "WARMTH"},
        {"AFFECTION", "CARE", "TRUST", "COMPASSION", "NOSTALGIA", "FEMININE", "FRIENDSHIP", "PASSION"},
    ),
    (
        "활력",
        {"ENERGY", "EXCITEMENT", "HAPPINESS", "DYNAMIC", "LIVELY"},
        {"JOY", "MOTIVATION", "SPARK", "ENTHUSIASM", "INTENSITY", "PASSION", "OPTIMISM", "FREEDOM", "CREATIVITY"},
    ),
    (
        "집중",
        {"FOCUS", "CLARITY", "PRECISION", "PRACTICAL", "REALITY", "ALERTNESS"},
        {"DISCIPLINE", "ORDER", "CONTROL", "DEPTH", "ELEGANCE", "SOPHISTICATION"},
    ),
    (
        "그늘",
        {"DEPRESSION", "SAD", "LONELINESS", "DESPAIR", "LOSS", "ISOLATION", "DARKNESS", "DEATH"},
        {"SADNESS", "MELANCHOLY", "GRIEF", "EMPTINESS", "FATIGUE", "DULLNESS", "COLDNESS", "ALIENATION", "SIN"},
    ),
    (
        "긴장",
        {"ANXIETY", "FEAR", "TENSION", "URGENCY", "RAGE", "CHAOS"},
        {"STRESS", "COWARDICE", "NERVOUSNESS", "RESTLESSNESS", "CAUTION", "PROTEST", "VULGARITY", "EGOTISM", "IMMATURITY", "MILITARY"},
    ),
    (
        "신비",
        {"MYSTERY", "SPIRITUAL", "BEAUTY", "ROYALTY"},
        {"CURIOSITY", "WONDER", "IMAGINATION", "DREAMY", "CREATIVITY", "IDEALISTIC", "ELEGANCE", "SOPHISTICATION", "DEPTH"},
    ),
    (
        "연결",
        {"CONNECTION", "COOPERATION", "TRUST", "HONESTY", "FRIENDSHIP"},
        {"BELONGING", "UNITY", "UNDERSTANDING", "COMPASSION", "HARMONY", "BALANCE", "NATURE", "GROUNDED", "LOVE"},
    ),
    (
        "회복",
        {"HOPE", "HEALING", "RENEWAL", "GROWTH", "FRESHNESS", "FREEDOM"},
        {"COURAGE", "RECOVERY", "BALANCE", "RESILIENCE", "OPTIMISM", "NATURE", "CONFIDENCE", "ABUNDANCE"},
    ),
    (
        "권위",
        {"AUTHORITY", "STRENGTH", "SECURITY", "STABILITY", "DURABILITY", "MILITARY", "WEALTH"},
        {"CONFIDENCE", "ROYALTY", "ABUNDANCE", "CONTROL", "PRACTICAL", "REALITY", "COURAGE"},
    ),
]


def main() -> None:
    with INPUT_CSV.open(newline="", encoding="utf-8") as f:
        counts = Counter((row["emotion"] or "").strip().upper() for row in csv.DictReader(f))

    rows = []
    for emotion in sorted(counts):
        contributions = []
        for family, primary, secondary in FAMILIES:
            if emotion in primary:
                contributions.append((family, "primary", 1.0))
            elif emotion in secondary:
                contributions.append((family, "secondary", 0.65))

        if not contributions:
            contributions = [("기타", "fallback", 1.0)]

        contributions.sort(key=lambda item: (-item[2], item[0]))
        for family, role, weight in contributions:
            rows.append(
                {
                    "emotion": emotion,
                    "family": family,
                    "role": role,
                    "weight": "{:.2f}".format(weight),
                    "sample_count": counts[emotion],
                }
            )

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["emotion", "family", "role", "weight", "sample_count"])
        writer.writeheader()
        writer.writerows(rows)

    print("wrote", OUTPUT_CSV, "rows", len(rows), "emotions", len(counts))


if __name__ == "__main__":
    main()
