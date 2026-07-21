"""Personalized palette emotion model.

This is a standalone Python version of the anchor-based personalization idea.
It keeps a base palette score and then shifts it toward a user profile made of:
- anchor color
- anchor emotion
- personalization strength
- optional emotion bias weights

Usage example:

    python3 test/personalized_palette_model.py \
        --colors '[{"hex": "#A4E3F2", "weight": 0.7}, {"hex": "#B7EDF8", "weight": 0.3}]' \
        --profile '{"anchorColor": "#A4E3F2", "anchorEmotion": "Calm", "personalizationStrength": 0.8, "emotionWeights": {"Calm": 0.6}}'

The script prints the base result and the personalized result side by side.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, MutableMapping, Sequence


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


@dataclass(frozen=True)
class ColorPoint:
    r: int
    g: int
    b: int
    hex: str
    weight: float


@dataclass(frozen=True)
class PersonalizationProfile:
    anchor_color: ColorPoint
    anchor_emotion: str = "Calm"
    personalization_strength: float = 0.6
    distance_weight: float = 0.55
    emotion_bias_weight: float = 0.45
    emotion_weights: Mapping[str, float] = None


def parse_hex_color(hex_value: str) -> ColorPoint:
    normalized = str(hex_value or "").strip().replace("#", "")
    if len(normalized) != 6:
        raise ValueError(f"Invalid hex color: {hex_value}")
    try:
        r = int(normalized[0:2], 16)
        g = int(normalized[2:4], 16)
        b = int(normalized[4:6], 16)
    except ValueError as exc:
        raise ValueError(f"Invalid hex color: {hex_value}") from exc
    return ColorPoint(r=r, g=g, b=b, hex=f"#{normalized.upper()}", weight=1.0)


def normalize_colors(colors: Sequence[Mapping[str, object]]) -> List[ColorPoint]:
    if not isinstance(colors, Sequence) or len(colors) == 0:
        raise ValueError("colors must be a non-empty array")

    parsed: List[ColorPoint] = []
    for entry in colors:
        base = parse_hex_color(str(entry.get("hex", "")))
        raw_weight = entry.get("weight", 1)
        try:
            weight = float(raw_weight)
        except (TypeError, ValueError):
            weight = 1.0
        if not math.isfinite(weight) or weight <= 0:
            weight = 1.0
        parsed.append(ColorPoint(r=base.r, g=base.g, b=base.b, hex=base.hex, weight=weight))

    total = sum(item.weight for item in parsed)
    if total <= 0:
        total = float(len(parsed))

    return [
        ColorPoint(r=item.r, g=item.g, b=item.b, hex=item.hex, weight=item.weight / total)
        for item in parsed
    ]


def _score_to_emotion(score: float) -> str:
    if score >= 0.35:
        return "Excitement"
    if score >= 0.1:
        return "Joy"
    if score > -0.1:
        return "Calm"
    if score > -0.3:
        return "Melancholy"
    return "Anxiety"


def _weighted_palette_features(colors: Sequence[ColorPoint]) -> Dict[str, float]:
    features = {"warmth": 0.0, "saturation": 0.0, "brightness": 0.0}
    for color in colors:
        nr = color.r / 255.0
        ng = color.g / 255.0
        nb = color.b / 255.0
        max_channel = max(nr, ng, nb)
        min_channel = min(nr, ng, nb)
        saturation = max_channel - min_channel
        brightness = (nr + ng + nb) / 3.0
        warmth = (nr - nb + 1.0) / 2.0

        features["warmth"] += warmth * color.weight
        features["saturation"] += saturation * color.weight
        features["brightness"] += brightness * color.weight

    return features


def analyze_palette_emotion(colors: Sequence[Mapping[str, object]]) -> Dict[str, object]:
    normalized = normalize_colors(colors)
    features = _weighted_palette_features(normalized)

    signed_warmth = features["warmth"] * 2.0 - 1.0
    score = (
        signed_warmth * 0.45
        + features["saturation"] * 0.35
        + (features["brightness"] - 0.5) * 0.2
    )

    bounded_score = clamp(score, -1.0, 1.0)
    confidence = clamp(0.55 + abs(bounded_score) * 0.4, 0.55, 0.99)

    return {
        "predictedEmotion": _score_to_emotion(bounded_score),
        "confidence": round(confidence, 2),
        "score": round(bounded_score, 3),
        "features": {
            "warmth": round(features["warmth"], 3),
            "saturation": round(features["saturation"], 3),
            "brightness": round(features["brightness"], 3),
        },
        "colors": [{"hex": item.hex, "weight": round(item.weight, 3)} for item in normalized],
        "explanation": "Base palette model combines weighted warmth, saturation, and brightness to estimate emotional tone.",
    }


def _normalize_emotion_weights(weights: Mapping[str, object] | None) -> Dict[str, float]:
    normalized: Dict[str, float] = {}
    if not weights:
        return normalized
    for emotion, value in weights.items():
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            parsed = 0.0
        normalized[str(emotion)] = clamp(parsed, -1.0, 1.0)
    return normalized


def parse_personalization_profile(profile: Mapping[str, object]) -> PersonalizationProfile:
    if not isinstance(profile, Mapping):
        raise ValueError("profile must be an object")

    anchor_color_input = profile.get("anchorColor") or profile.get("baseColor") or profile.get("referenceColor")
    if not anchor_color_input:
        raise ValueError("profile.anchorColor is required")

    if isinstance(anchor_color_input, Mapping):
        anchor_hex = str(anchor_color_input.get("hex", ""))
    else:
        anchor_hex = str(anchor_color_input)

    anchor_color = parse_hex_color(anchor_hex)
    anchor_emotion = str(profile.get("anchorEmotion") or "Calm").strip() or "Calm"

    def _to_float(value: object, default: float) -> float:
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            parsed = default
        return parsed

    strength = clamp(_to_float(profile.get("personalizationStrength", profile.get("strength", 0.6)), 0.6), 0.0, 1.0)
    distance_weight = clamp(_to_float(profile.get("distanceWeight", 0.55), 0.55), 0.0, 1.0)
    emotion_bias_weight = clamp(_to_float(profile.get("emotionBiasWeight", 0.45), 0.45), 0.0, 1.0)

    return PersonalizationProfile(
        anchor_color=anchor_color,
        anchor_emotion=anchor_emotion,
        personalization_strength=strength,
        distance_weight=distance_weight,
        emotion_bias_weight=emotion_bias_weight,
        emotion_weights=_normalize_emotion_weights(profile.get("emotionWeights") or profile.get("biases")),
    )


def _average_palette_rgb(colors: Sequence[ColorPoint]) -> Dict[str, float]:
    normalized = normalize_colors([{"hex": c.hex, "weight": c.weight} for c in colors])
    return {
        "r": sum(color.r * color.weight for color in normalized),
        "g": sum(color.g * color.weight for color in normalized),
        "b": sum(color.b * color.weight for color in normalized),
    }


def _color_distance(a: Mapping[str, float], b: Mapping[str, float]) -> float:
    dr = float(a["r"]) - float(b["r"])
    dg = float(a["g"]) - float(b["g"])
    db = float(a["b"]) - float(b["b"])
    return math.sqrt((dr * dr) + (dg * dg) + (db * db))


def _infer_emotion_bias(base_emotion: str, profile: PersonalizationProfile) -> float:
    direct_bias = float(profile.emotion_weights.get(base_emotion, 0.0)) if profile.emotion_weights else 0.0
    anchor_bias = float(profile.emotion_weights.get(profile.anchor_emotion, 0.0)) if profile.emotion_weights else 0.0
    return clamp(direct_bias + (anchor_bias * 0.5), -1.0, 1.0)


def analyze_personalized_palette_emotion(payload: Mapping[str, object]) -> Dict[str, object]:
    if not isinstance(payload, Mapping) or not isinstance(payload.get("colors"), Sequence):
        raise ValueError("colors must be a non-empty array")

    base_result = analyze_palette_emotion(payload["colors"])
    profile = parse_personalization_profile(payload.get("profile") or {})
    palette = normalize_colors(payload["colors"])
    palette_average = _average_palette_rgb(palette)
    anchor_color = {"r": profile.anchor_color.r, "g": profile.anchor_color.g, "b": profile.anchor_color.b}

    max_distance = math.sqrt(3 * 255 * 255)
    distance = _color_distance(palette_average, anchor_color)
    similarity = 1.0 - clamp(distance / max_distance, 0.0, 1.0)

    anchor_affinity = (similarity * 2.0) - 1.0
    emotion_bias = _infer_emotion_bias(str(base_result["predictedEmotion"]), profile)
    strength = profile.personalization_strength

    adjusted_score = clamp(
        float(base_result["score"]) * (1.0 - (strength * 0.25))
        + (anchor_affinity * profile.distance_weight * strength)
        + (emotion_bias * profile.emotion_bias_weight * strength),
        -1.0,
        1.0,
    )

    confidence = clamp(float(base_result["confidence"]) + (abs(adjusted_score - float(base_result["score"])) * 0.25), 0.55, 0.99)

    return {
        "model": "personalized-anchor-palette-v1",
        "predictedEmotion": _score_to_emotion(adjusted_score),
        "confidence": round(confidence, 2),
        "score": round(adjusted_score, 3),
        "base": {
            "predictedEmotion": base_result["predictedEmotion"],
            "confidence": base_result["confidence"],
            "score": base_result["score"],
        },
        "profile": {
            "anchorColor": profile.anchor_color.hex,
            "anchorEmotion": profile.anchor_emotion,
            "personalizationStrength": round(profile.personalization_strength, 3),
            "distanceWeight": round(profile.distance_weight, 3),
            "emotionBiasWeight": round(profile.emotion_bias_weight, 3),
        },
        "features": {
            "paletteAverage": {
                "r": round(palette_average["r"], 3),
                "g": round(palette_average["g"], 3),
                "b": round(palette_average["b"], 3),
            },
            "anchorDistance": round(distance, 3),
            "anchorSimilarity": round(similarity, 3),
            "emotionBias": round(emotion_bias, 3),
        },
        "explanation": "Personalization shifts the base palette result toward the user anchor color and anchor emotion.",
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze a color palette and optionally personalize the result.")
    parser.add_argument("--colors", required=True, help="JSON array with color objects, e.g. [{\"hex\": \"#FF6B2C\", \"weight\": 0.6}]")
    parser.add_argument("--profile", default="{}", help="JSON object with personalization profile data")
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    colors = json.loads(args.colors)
    profile = json.loads(args.profile)

    base_result = analyze_palette_emotion(colors)
    personalized_result = analyze_personalized_palette_emotion({"colors": colors, "profile": profile})

    print(json.dumps({"base": base_result, "personalized": personalized_result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()