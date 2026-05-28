const fs = require("fs");
const path = require("path");

const LOG_DIR = path.join(process.cwd(), "experiments", "logs");
const LOG_FILE = path.join(LOG_DIR, "ab-events.ndjson");

function ensureLogFile() {
  if (!fs.existsSync(LOG_DIR)) {
    fs.mkdirSync(LOG_DIR, { recursive: true });
  }
  if (!fs.existsSync(LOG_FILE)) {
    fs.writeFileSync(LOG_FILE, "", "utf8");
  }
}

function trackExperimentEvent(payload) {
  ensureLogFile();
  const event = {
    timestamp: new Date().toISOString(),
    ...payload
  };
  fs.appendFileSync(LOG_FILE, `${JSON.stringify(event)}\n`, "utf8");
  return event;
}

module.exports = {
  LOG_FILE,
  trackExperimentEvent
};
