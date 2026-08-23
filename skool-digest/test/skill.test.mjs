#!/usr/bin/env node
// SKILL.md rendering tests. No network, no API keys:
//   node test/skill.test.mjs

import { renderSkill } from "../lib/skill.mjs";

let pass = 0, fail = 0;
const ok = (name, cond, detail = "") => {
  if (cond) { pass++; console.log(`  ok   ${name}`); }
  else { fail++; console.log(`  FAIL ${name} ${detail}`); }
};

const course = { title: "Rank & Expand Academy" };
const playbook = {
  core_thesis: "Ranking a community is a distribution problem. Win search first.",
  playbook: [
    { id: "p1", action: "Publish answer pages", why: "Compounds", trigger: "once you have 10 questions",
      phase: "foundation", effort: "small", repetition_count: 6, prerequisites: ["a live community"], evidence: [] },
    { id: "p2", action: "Raise price", why: "Amplifies retention", trigger: "after flat churn",
      phase: "monetize", effort: "medium", repetition_count: 3, prerequisites: [], evidence: [] },
  ],
  contradictions: [{ topic: "Free trials", resolution: "Use a 7-day trial.",
    positions: [{ claim: "Never", module: "Pricing", timestamp: "3:00" }] }],
  ignore: [{ claim: "Post daily", reason: "Unfalsifiable" }],
};
const distilled = [
  { module: { title: "Search", videos: ["u"] }, transcript: { source: "captions" },
    result: { numbers: [{ metric: "Pages | needed", value: "40", context: "First 90 days" }],
              assets: [{ kind: "dm", name: "Opener", structure: "Accept, then ask." }] } },
  { module: { title: "Churn", videos: ["u2"] }, transcript: { source: "none" },
    result: { numbers: [], assets: [] } },
];

const md = renderSkill(course, playbook, distilled);
const frontmatter = md.split("---")[1] ?? "";

console.log("\nfrontmatter");
ok("opens with fence", md.startsWith("---\n"));
ok("slugged name", /\nname: rank-expand-academy\n/.test(frontmatter), frontmatter);
ok("description on one line", (frontmatter.match(/description: .*/)?.[0] ?? "").length > 40);
ok("description names the course", /Rank & Expand Academy/.test(frontmatter));
ok("description names phases", /foundation/.test(frontmatter) && /monetize/.test(frontmatter));
ok("description under 1024", (frontmatter.match(/description: (.*)/)?.[1] ?? "").length <= 1024);

console.log("\nbody");
ok("thesis present", md.includes("distribution problem"));
ok("phase headings", md.includes("## Foundation") && md.includes("## Monetize"));
ok("actions as headings", md.includes("### Publish answer pages"));
ok("trigger rendered", md.includes("**When:** once you have 10 questions"));
ok("conviction rendered", md.includes("conviction: 6"));
ok("prerequisites rendered", md.includes("needs first: a live community"));
ok("contradiction resolution", md.includes("**Follow:** Use a 7-day trial."));
ok("ignore list", md.includes("Post daily"));

console.log("\nnumbers + assets");
ok("numbers table", md.includes("| Metric | Value | Context |"));
ok("pipe escaped in cell", md.includes("Pages \\| needed"));
ok("dm heading reads correctly", md.includes("### DM openers"), "got Dms?");

console.log("\nprovenance");
ok("counts modules", md.includes("Distilled from 2 module(s)"));
ok("names untranscribed module", /no transcript[\s\S]*- Churn/.test(md));
ok("carries the caveat", md.includes("not established fact"));

console.log("\nedge cases");
const bare = renderSkill({ title: "X" },
  { core_thesis: "T.", playbook: [], contradictions: [], ignore: [] }, []);
ok("empty playbook still valid", bare.startsWith("---\n") && bare.includes("name: x"));
ok("no empty numbers table", !bare.includes("| Metric |"));
ok("no empty judgment section", !bare.includes("## Judgment calls"));

console.log(`\n${pass} passed, ${fail} failed\n`);
process.exit(fail ? 1 : 0);
