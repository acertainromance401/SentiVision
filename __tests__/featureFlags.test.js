const { evaluateFlags, isFlagEnabledForUser } = require("../src/featureFlags");

describe("feature flags", () => {
  const baseUser = { id: "user-1001", segment: "general" };

  test("returns false for unknown flag", () => {
    const enabled = isFlagEnabledForUser("unknownFlag", baseUser, { APP_ENV: "production" });
    expect(enabled).toBe(false);
  });

  test("uses target user override in production", () => {
    const user = { id: "beta-designer-01", segment: "beta" };
    const enabled = isFlagEnabledForUser("newOnboardingFlow", user, { APP_ENV: "production" });
    expect(enabled).toBe(true);
  });

  test("supports environment flag override on/off", () => {
    const on = isFlagEnabledForUser("realtimeMoodHints", baseUser, {
      APP_ENV: "production",
      FLAG_REALTIME_MOOD_HINTS: "on"
    });
    const off = isFlagEnabledForUser("realtimeMoodHints", baseUser, {
      APP_ENV: "production",
      FLAG_REALTIME_MOOD_HINTS: "off"
    });
    expect(on).toBe(true);
    expect(off).toBe(false);
  });

  test("supports JSON override payload", () => {
    const enabled = isFlagEnabledForUser("advancedColorInsights", baseUser, {
      APP_ENV: "production",
      FLAG_OVERRIDES: JSON.stringify({ advancedColorInsights: true })
    });
    expect(enabled).toBe(true);
  });

  test("gracefully handles invalid JSON override", () => {
    const enabled = isFlagEnabledForUser("advancedColorInsights", baseUser, {
      APP_ENV: "production",
      FLAG_OVERRIDES: "{invalid-json"
    });
    expect(typeof enabled).toBe("boolean");
  });

  test("enables by target segment", () => {
    const user = { id: "user-segment-test", segment: "pilot-team-01" };
    const enabled = isFlagEnabledForUser("realtimeMoodHints", user, {
      APP_ENV: "production"
    });
    expect(enabled).toBe(true);
  });

  test("returns all three flags from evaluateFlags", () => {
    const result = evaluateFlags(baseUser, { APP_ENV: "staging" });
    expect(Object.keys(result).sort()).toEqual([
      "advancedColorInsights",
      "newOnboardingFlow",
      "realtimeMoodHints"
    ]);
  });
});
