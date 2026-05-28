const { assignUserToExperiment, EXPERIMENTS } = require("../src/abTesting");

describe("ab testing", () => {
  test("keeps assignment stable for same user", () => {
    const first = assignUserToExperiment("emotion-summary-layout", "user-42");
    const second = assignUserToExperiment("emotion-summary-layout", "user-42");
    expect(first.variant).toBe(second.variant);
    expect(first.bucket).toBe(second.bucket);
  });

  test("only returns declared variants", () => {
    const assigned = assignUserToExperiment("emotion-summary-layout", "user-1002");
    expect(EXPERIMENTS.emotionSummaryLayout.variants).toContain(assigned.variant);
  });

  test("throws for unknown experiment", () => {
    expect(() => assignUserToExperiment("not-exist", "user-1")).toThrow("Unknown experiment");
  });

  test("falls back to last variant when weights are underspecified", () => {
    const original = [...EXPERIMENTS.emotionSummaryLayout.weights];
    EXPERIMENTS.emotionSummaryLayout.weights = [0, 0];
    const assigned = assignUserToExperiment("emotion-summary-layout", "fallback-user");
    expect(assigned.variant).toBe("B");
    EXPERIMENTS.emotionSummaryLayout.weights = original;
  });
});
