const pkg = require("../index");

describe("package exports", () => {
  test("exposes package metadata", () => {
    const info = pkg.getPackageInfo();
    expect(info.name).toBe("@acertainromance401/sentivision-utils");
  });

  test("exposes feature and experiment helpers", () => {
    expect(typeof pkg.evaluateFlags).toBe("function");
    expect(typeof pkg.assignUserToExperiment).toBe("function");
  });
});
