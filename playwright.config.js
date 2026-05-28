const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./e2e",
  timeout: 30000,
  retries: 0,
  use: {
    headless: true,
    screenshot: "only-on-failure",
    trace: "retain-on-failure"
  },
  reporter: [["list"], ["html", { outputFolder: "playwright-report", open: "never" }]]
});
