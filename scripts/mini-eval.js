const { analyzePaletteEmotion } = require("../src/api/aiService");

const cases = [
  {
    id: "warm-energy",
    input: {
      colors: [
        { hex: "#FF6B2C", weight: 0.7 },
        { hex: "#FFD166", weight: 0.3 }
      ]
    },
    expected: ["Excitement", "Joy"]
  },
  {
    id: "neutral-mix",
    input: {
      colors: [
        { hex: "#7C8A9A", weight: 0.5 },
        { hex: "#AAB7C4", weight: 0.5 }
      ]
    },
    expected: ["Calm", "Melancholy"]
  }
];

const results = cases.map((testCase) => {
  const output = analyzePaletteEmotion(testCase.input);
  const pass = testCase.expected.includes(output.predictedEmotion);

  return {
    id: testCase.id,
    predictedEmotion: output.predictedEmotion,
    confidence: output.confidence,
    pass
  };
});

const passedCount = results.filter((item) => item.pass).length;
const passRate = passedCount / results.length;

console.log("Mini Eval Results");
for (const result of results) {
  console.log(
    `- ${result.id}: ${result.pass ? "PASS" : "FAIL"} | emotion=${result.predictedEmotion} | confidence=${result.confidence}`
  );
}
console.log(`pass_rate=${passRate.toFixed(2)}`);

if (passRate < 1) {
  process.exitCode = 1;
}
