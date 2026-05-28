const { evaluateFlags, isFlagEnabledForUser, DEFAULT_FLAGS } = require("./src/featureFlags");
const { EXPERIMENTS, assignUserToExperiment } = require("./src/abTesting");

function getPackageInfo() {
  return {
    name: "@acertainromance401/sentivision-utils",
    purpose: "Utility metadata for SentiVision package workflows"
  };
}

module.exports = {
  getPackageInfo,
  DEFAULT_FLAGS,
  evaluateFlags,
  isFlagEnabledForUser,
  EXPERIMENTS,
  assignUserToExperiment
};