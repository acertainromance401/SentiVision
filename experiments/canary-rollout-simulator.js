const fs = require("fs");
const path = require("path");

const configPath = path.join(__dirname, "canary-rollout-config.json");
const logPath = path.join(__dirname, "logs", "canary-rollout-log.json");

function readConfig() {
  return JSON.parse(fs.readFileSync(configPath, "utf8"));
}

function randomHealth(stagePercent) {
  // 높은 트래픽 구간에서 실패 확률이 약간 증가하도록 시뮬레이션
  const errorRate = Math.max(0.1, Math.min(12, stagePercent * 0.08 + Math.random() * 4));
  const latencyP95 = Math.max(120, Math.min(1500, 150 + stagePercent * 5 + Math.random() * 400));
  return { errorRate, latencyP95 };
}

function runCanarySimulation() {
  const config = readConfig();
  const logs = [];
  let previousStage = 0;

  for (const stage of config.stages) {
    const health = randomHealth(stage);
    const healthy =
      health.errorRate <= config.healthPolicy.maxErrorRatePercent &&
      health.latencyP95 <= config.healthPolicy.maxLatencyMsP95;

    const entry = {
      timestamp: new Date().toISOString(),
      stage,
      health,
      healthy,
      action: healthy ? "promote" : `rollback_to_${previousStage}`
    };

    logs.push(entry);

    if (!healthy) {
      break;
    }

    previousStage = stage;
  }

  if (!fs.existsSync(path.dirname(logPath))) {
    fs.mkdirSync(path.dirname(logPath), { recursive: true });
  }
  fs.writeFileSync(logPath, JSON.stringify(logs, null, 2), "utf8");
  console.log(JSON.stringify(logs, null, 2));
}

runCanarySimulation();
