module.exports = {
  testEnvironment: "node",
  testPathIgnorePatterns: ["/e2e/"],
  collectCoverageFrom: ["src/**/*.js", "index.js"],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};
