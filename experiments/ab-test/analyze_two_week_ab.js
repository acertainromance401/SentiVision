const fs = require("fs");
const path = require("path");

const csvPath = path.join(__dirname, "two_week_ab_metrics.csv");
const outPath = path.join(__dirname, "ab_two_week_report.md");

function parseCsv(text) {
  const [headerLine, ...rows] = text.trim().split("\n");
  const headers = headerLine.split(",");
  return rows.map((line) => {
    const cols = line.split(",");
    const row = {};
    headers.forEach((h, i) => {
      row[h] = cols[i];
    });
    return {
      ...row,
      users: Number(row.users),
      activation_rate: Number(row.activation_rate),
      feedback_submit_rate: Number(row.feedback_submit_rate),
      d7_retention: Number(row.d7_retention),
      avg_session_min: Number(row.avg_session_min)
    };
  });
}

function aggregate(rows, variant) {
  const filtered = rows.filter((r) => r.variant === variant);
  const sum = filtered.reduce(
    (acc, r) => {
      acc.users += r.users;
      acc.activation += r.activation_rate;
      acc.feedback += r.feedback_submit_rate;
      acc.retention += r.d7_retention;
      acc.session += r.avg_session_min;
      return acc;
    },
    { users: 0, activation: 0, feedback: 0, retention: 0, session: 0 }
  );
  const n = filtered.length || 1;
  return {
    users: sum.users,
    activation: sum.activation / n,
    feedback: sum.feedback / n,
    retention: sum.retention / n,
    session: sum.session / n
  };
}

function pctDiff(newValue, oldValue) {
  if (oldValue === 0) return 0;
  return ((newValue - oldValue) / oldValue) * 100;
}

function main() {
  const rows = parseCsv(fs.readFileSync(csvPath, "utf8"));
  const a = aggregate(rows, "A");
  const b = aggregate(rows, "B");

  const uplift = {
    activation: pctDiff(b.activation, a.activation),
    feedback: pctDiff(b.feedback, a.feedback),
    retention: pctDiff(b.retention, a.retention),
    session: pctDiff(b.session, a.session)
  };

  const decision = uplift.retention > 10 && uplift.feedback > 15 ? "Persevere" : "Pivot";

  const report = [
    "# 2-Week Feature Flag A/B Report",
    "",
    `- period: ${rows[0].date} ~ ${rows[rows.length - 1].date}`,
    `- users_A: ${a.users}`,
    `- users_B: ${b.users}`,
    "",
    "## Average Metrics",
    "",
    `- activation_rate_A: ${a.activation.toFixed(3)}`,
    `- activation_rate_B: ${b.activation.toFixed(3)}`,
    `- feedback_submit_rate_A: ${a.feedback.toFixed(3)}`,
    `- feedback_submit_rate_B: ${b.feedback.toFixed(3)}`,
    `- d7_retention_A: ${a.retention.toFixed(3)}`,
    `- d7_retention_B: ${b.retention.toFixed(3)}`,
    `- avg_session_min_A: ${a.session.toFixed(3)}`,
    `- avg_session_min_B: ${b.session.toFixed(3)}`,
    "",
    "## Uplift (B vs A)",
    "",
    `- activation: ${uplift.activation.toFixed(2)}%`,
    `- feedback_submit: ${uplift.feedback.toFixed(2)}%`,
    `- d7_retention: ${uplift.retention.toFixed(2)}%`,
    `- avg_session_min: ${uplift.session.toFixed(2)}%`,
    "",
    `## Decision\n- ${decision}`,
    ""
  ];

  fs.writeFileSync(outPath, report.join("\n"), "utf8");
  console.log(`Wrote ${outPath}`);
}

main();
