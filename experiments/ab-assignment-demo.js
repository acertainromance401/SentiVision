const { evaluateFlags } = require("../src/featureFlags");
const { assignUserToExperiment } = require("../src/abTesting");
const { trackExperimentEvent } = require("../src/eventTracker");

const users = [
  { id: "user-1001", segment: "general" },
  { id: "user-1002", segment: "general" },
  { id: "beta-designer-01", segment: "beta" },
  { id: "pro-artist-01", segment: "pro" },
  { id: "pilot-team-01", segment: "pilot" }
];

function runDemo() {
  const output = [];

  for (const user of users) {
    const flags = evaluateFlags(user, process.env);
    const assignment1 = assignUserToExperiment("emotion-summary-layout", user.id);
    const assignment2 = assignUserToExperiment("emotion-summary-layout", user.id);

    // 동일 userId는 같은 bucket/variant를 유지해야 한다.
    const consistent =
      assignment1.variant === assignment2.variant && assignment1.bucket === assignment2.bucket;

    trackExperimentEvent({
      type: "experiment_exposure",
      userId: user.id,
      experiment: assignment1.experimentKey,
      variant: assignment1.variant,
      bucket: assignment1.bucket,
      consistent
    });

    output.push({
      userId: user.id,
      flags,
      assignment: assignment1,
      consistent
    });
  }

  console.log(JSON.stringify(output, null, 2));
}

runDemo();
