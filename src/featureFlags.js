const DEFAULT_FLAGS = {
  newOnboardingFlow: {
    enabledEnvs: ["staging", "production"],
    defaultPercentage: 50,
    targetUsers: ["beta-designer-01", "qa-owner-01"]
  },
  advancedColorInsights: {
    enabledEnvs: ["staging", "production"],
    defaultPercentage: 30,
    targetUsers: ["pro-artist-01"]
  },
  realtimeMoodHints: {
    enabledEnvs: ["staging", "production"],
    defaultPercentage: 10,
    targetUsers: ["pilot-team-01"]
  }
};

function hashString(value) {
  let hash = 2166136261;
  for (let i = 0; i < value.length; i += 1) {
    hash ^= value.charCodeAt(i);
    hash += (hash << 1) + (hash << 4) + (hash << 7) + (hash << 8) + (hash << 24);
  }
  return Math.abs(hash >>> 0);
}

function parseFlagOverrides(env) {
  try {
    return env.FLAG_OVERRIDES ? JSON.parse(env.FLAG_OVERRIDES) : {};
  } catch {
    return {};
  }
}

function toEnvToggleKey(flagKey) {
  const snakeUpper = flagKey.replace(/([a-z])([A-Z])/g, "$1_$2").toUpperCase();
  return `FLAG_${snakeUpper}`;
}

function isFlagEnabledForUser(flagKey, user, env = process.env) {
  const config = DEFAULT_FLAGS[flagKey];
  if (!config) {
    return false;
  }

  const environment = env.APP_ENV || "development";
  if (!config.enabledEnvs.includes(environment)) {
    return false;
  }

  const overrides = parseFlagOverrides(env);
  if (Object.prototype.hasOwnProperty.call(overrides, flagKey)) {
    return Boolean(overrides[flagKey]);
  }

  const envToggle = env[toEnvToggleKey(flagKey)];
  if (envToggle === "on") {
    return true;
  }
  if (envToggle === "off") {
    return false;
  }

  if (config.targetUsers.includes(user.id) || config.targetUsers.includes(user.segment)) {
    return true;
  }

  const rolloutSeed = `${flagKey}:${user.id}`;
  const bucket = hashString(rolloutSeed) % 100;
  return bucket < config.defaultPercentage;
}

function evaluateFlags(user, env = process.env) {
  return Object.keys(DEFAULT_FLAGS).reduce((acc, key) => {
    acc[key] = isFlagEnabledForUser(key, user, env);
    return acc;
  }, {});
}

module.exports = {
  DEFAULT_FLAGS,
  evaluateFlags,
  isFlagEnabledForUser
};
