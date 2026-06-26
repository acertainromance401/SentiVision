const fs = require("fs");
const path = require("path");

const personasPath = path.join(__dirname, "personas.json");
const scenariosPath = path.join(__dirname, "scenarios.json");
const outJsonPath = path.join(__dirname, "persona_feedback.json");
const outMdPath = path.join(__dirname, "persona_feedback_report.md");

const phraseByStyle = {
  encouraging: "시작 장벽이 낮아져서 계속 쓰고 싶어요.",
  direct: "핵심은 속도와 즉시성입니다.",
  curious: "왜 그런 결과인지 더 배우고 싶어요.",
  precise: "명확한 대비와 접근성 옵션이 필요해요.",
  empathetic: "감정 표현이 더 따뜻하면 좋겠어요.",
  analytical: "수치 비교와 추세선이 중요합니다.",
  brief: "한 화면에서 끝나면 좋겠어요.",
  exploratory: "실험 옵션을 더 쉽게 찾고 싶어요.",
  cautious: "개인정보 보관 기준을 먼저 보여주세요.",
  collaborative: "팀 공유 흐름이 자연스러워야 해요."
};

function scoreFromSeed(seed) {
  let hash = 0;
  for (let i = 0; i < seed.length; i += 1) hash = (hash * 31 + seed.charCodeAt(i)) >>> 0;
  return {
    usability: 3 + (hash % 3),
    clarity: 2 + (hash % 4),
    trust: 2 + (hash % 4)
  };
}

function main() {
  const personas = JSON.parse(fs.readFileSync(personasPath, "utf8"));
  const scenarios = JSON.parse(fs.readFileSync(scenariosPath, "utf8"));

  const feedback = personas.map((persona, idx) => {
    const scenario = scenarios[idx % scenarios.length];
    const scores = scoreFromSeed(`${persona.id}:${scenario.id}`);
    const recommendation =
      scores.clarity < 4 ? "결과 근거 UI 강화" : scores.trust < 4 ? "데이터 처리 투명성 강화" : "현재 방향 유지";

    return {
      personaId: persona.id,
      personaName: persona.name,
      segment: persona.segment,
      llmPersonaPattern: persona.style,
      scenarioId: scenario.id,
      scenarioTitle: scenario.title,
      feedbackText: `${phraseByStyle[persona.style]} (${scenario.title})`,
      scores,
      recommendation
    };
  });

  fs.writeFileSync(outJsonPath, JSON.stringify(feedback, null, 2), "utf8");

  const avg = feedback.reduce(
    (acc, item) => {
      acc.usability += item.scores.usability;
      acc.clarity += item.scores.clarity;
      acc.trust += item.scores.trust;
      return acc;
    },
    { usability: 0, clarity: 0, trust: 0 }
  );

  const total = feedback.length;
  const md = [
    "# Persona Feedback Report (LLM-pattern synthetic)",
    "",
    `- participants: ${total}`,
    `- avg_usability: ${(avg.usability / total).toFixed(2)}`,
    `- avg_clarity: ${(avg.clarity / total).toFixed(2)}`,
    `- avg_trust: ${(avg.trust / total).toFixed(2)}`,
    "",
    "## Raw Entries",
    ""
  ];

  for (const item of feedback) {
    md.push(`- ${item.personaId}(${item.segment}) -> ${item.feedbackText} / rec: ${item.recommendation}`);
  }

  fs.writeFileSync(outMdPath, md.join("\n"), "utf8");
  console.log(`Generated ${total} persona feedback records.`);
}

main();
