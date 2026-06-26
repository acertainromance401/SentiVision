const crypto = require("crypto");

const EXPERIMENTS = {
  emotionSummaryLayout: {
    key: "emotion-summary-layout",
    variants: ["A", "B"],
    weights: [50, 50]
  }
};

function bucketOf(seed) {
  const digest = crypto.createHash("sha256").update(seed).digest("hex");
  const firstEightHex = digest.slice(0, 8);
  return parseInt(firstEightHex, 16) % 100;
}

function resolveVariant(experiment, bucket) {
  let cumulative = 0;
  for (let i = 0; i < experiment.variants.length; i += 1) {
    cumulative += experiment.weights[i];
    if (bucket < cumulative) {
      return experiment.variants[i];
    }
  }
  return experiment.variants[experiment.variants.length - 1];
}

function assignUserToExperiment(experimentKey, userId) {
  const experiment = Object.values(EXPERIMENTS).find((item) => item.key === experimentKey);
  if (!experiment) {
    throw new Error(`Unknown experiment: ${experimentKey}`);
  }

  const seed = `${experiment.key}:${userId}`;
  const bucket = bucketOf(seed);
  const variant = resolveVariant(experiment, bucket);

  return {
    experimentKey,
    userId,
    variant,
    bucket
  };
}

module.exports = {
  EXPERIMENTS,
  assignUserToExperiment
};
