const path = require("path");
const { test, expect } = require("@playwright/test");

test("frontend landing renders headline and actions", async ({ page }) => {
  const filePath = path.resolve(__dirname, "..", "frontend", "index.html");
  await page.goto(`file://${filePath}`);

  await expect(page.getByText("Color to Emotion", { exact: false })).toBeVisible();
  await expect(page.getByRole("link", { name: "Actions 확인" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Repository" })).toBeVisible();
});
