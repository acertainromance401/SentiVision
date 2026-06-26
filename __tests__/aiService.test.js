const { analyzePaletteEmotion, parseHexColor } = require("../src/api/aiService");

describe("aiService", () => {
  test("parses valid hex colors", () => {
    expect(parseHexColor("#ff9900")).toEqual({
      r: 255,
      g: 153,
      b: 0,
      hex: "#FF9900"
    });
  });

  test("predicts warm palettes as positive emotion", () => {
    const result = analyzePaletteEmotion({
      colors: [
        { hex: "#FF6B2C", weight: 0.7 },
        { hex: "#FFC857", weight: 0.3 }
      ]
    });

    expect(["Excitement", "Joy"]).toContain(result.predictedEmotion);
    expect(result.confidence).toBeGreaterThanOrEqual(0.55);
  });

  test("throws for invalid payload", () => {
    expect(() => analyzePaletteEmotion({ colors: [] })).toThrow("non-empty array");
    expect(() => analyzePaletteEmotion({ colors: [{ hex: "red" }] })).toThrow("Invalid hex color");
  });
});
