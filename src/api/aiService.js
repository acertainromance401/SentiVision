function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function parseHexColor(hex) {
  const normalized = String(hex || "").trim().replace(/^#/, "");
  if (!/^[0-9a-fA-F]{6}$/.test(normalized)) {
    throw new Error(`Invalid hex color: ${hex}`);
  }

  return {
    r: parseInt(normalized.slice(0, 2), 16),
    g: parseInt(normalized.slice(2, 4), 16),
    b: parseInt(normalized.slice(4, 6), 16),
    hex: `#${normalized.toUpperCase()}`
  };
}

function normalizeColors(colors) {
  if (!Array.isArray(colors) || colors.length === 0) {
    throw new Error("colors must be a non-empty array");
  }

  const weighted = colors.map((entry) => {
    const parsed = parseHexColor(entry.hex);
    const rawWeight = Number(entry.weight);
    const weight = Number.isFinite(rawWeight) && rawWeight > 0 ? rawWeight : 1;
    return { ...parsed, weight };
  });

  const total = weighted.reduce((sum, item) => sum + item.weight, 0);
  return weighted.map((item) => ({
    ...item,
    weight: item.weight / total
  }));
}

function scoreToEmotion(score) {
  if (score >= 0.35) {
    return "Excitement";
  }
  if (score >= 0.1) {
    return "Joy";
  }
  if (score > -0.1) {
    return "Calm";
  }
  if (score > -0.3) {
    return "Melancholy";
  }
  return "Anxiety";
}

function analyzePaletteEmotion(payload) {
  const colors = normalizeColors(payload.colors);

  const features = colors.reduce(
    (acc, color) => {
      const normalizedR = color.r / 255;
      const normalizedG = color.g / 255;
      const normalizedB = color.b / 255;
      const maxChannel = Math.max(normalizedR, normalizedG, normalizedB);
      const minChannel = Math.min(normalizedR, normalizedG, normalizedB);
      const saturation = maxChannel - minChannel;
      const brightness = (normalizedR + normalizedG + normalizedB) / 3;
      const warmth = (normalizedR - normalizedB + 1) / 2;

      return {
        warmth: acc.warmth + warmth * color.weight,
        saturation: acc.saturation + saturation * color.weight,
        brightness: acc.brightness + brightness * color.weight
      };
    },
    { warmth: 0, saturation: 0, brightness: 0 }
  );

  const signedWarmth = features.warmth * 2 - 1;
  const score =
    signedWarmth * 0.45 +
    features.saturation * 0.35 +
    (features.brightness - 0.5) * 0.2;

  const boundedScore = clamp(score, -1, 1);
  const confidence = clamp(0.55 + Math.abs(boundedScore) * 0.4, 0.55, 0.99);
  const predictedEmotion = scoreToEmotion(boundedScore);

  return {
    predictedEmotion,
    confidence: Number(confidence.toFixed(2)),
    score: Number(boundedScore.toFixed(3)),
    features: {
      warmth: Number(features.warmth.toFixed(3)),
      saturation: Number(features.saturation.toFixed(3)),
      brightness: Number(features.brightness.toFixed(3))
    },
    colors: colors.map((color) => ({
      hex: color.hex,
      weight: Number(color.weight.toFixed(3))
    })),
    explanation:
      "Heuristic palette model combines weighted warmth, saturation, and brightness to estimate emotional tone."
  };
}

module.exports = {
  analyzePaletteEmotion,
  parseHexColor,
  normalizeColors
};
