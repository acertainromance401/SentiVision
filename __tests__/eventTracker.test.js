const fs = require("fs");
const os = require("os");
const path = require("path");

describe("event tracker", () => {
  let originalCwd;
  let tempDir;

  beforeEach(() => {
    jest.resetModules();
    originalCwd = process.cwd();
    tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "sentivision-log-test-"));
    process.chdir(tempDir);
  });

  afterEach(() => {
    process.chdir(originalCwd);
    fs.rmSync(tempDir, { recursive: true, force: true });
  });

  test("writes ndjson event log", () => {
    const { LOG_FILE, trackExperimentEvent } = require("../src/eventTracker");
    const event = trackExperimentEvent({
      type: "experiment_exposure",
      userId: "user-1001",
      experiment: "emotion-summary-layout",
      variant: "A"
    });

    const content = fs.readFileSync(LOG_FILE, "utf8").trim().split("\n");
    const parsed = JSON.parse(content[0]);

    expect(event.type).toBe("experiment_exposure");
    expect(parsed.userId).toBe("user-1001");
    expect(parsed.variant).toBe("A");
    expect(parsed.timestamp).toBeTruthy();
  });

  test("appends second event when log file already exists", () => {
    const { LOG_FILE, trackExperimentEvent } = require("../src/eventTracker");
    trackExperimentEvent({ type: "experiment_exposure", userId: "u1", variant: "A" });
    trackExperimentEvent({ type: "experiment_exposure", userId: "u2", variant: "B" });

    const lines = fs.readFileSync(LOG_FILE, "utf8").trim().split("\n");
    expect(lines).toHaveLength(2);
    const second = JSON.parse(lines[1]);
    expect(second.userId).toBe("u2");
  });
});
