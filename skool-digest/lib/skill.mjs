// Render the playbook as a Claude Code skill.
//
// playbook.md is for a person to read once. SKILL.md is for Claude to load
// when you are doing the work — so it leads with the decision rules and the
// numbers, and drops the narrative.

import { slug } from "./util.mjs";

const MAX_DESC = 1024;

/** playbook + distilled -> SKILL.md */
export function renderSkill(course, playbook, distilled, { name } = {}) {
  const skillName = slug(name ?? course.title);
  const L = [];

  L.push("---");
  L.push(`name: ${skillName}`);
  L.push(`description: ${describe(course, playbook)}`);
  L.push("---", "");

  L.push(`# ${course.title}`, "");
  L.push(playbook.core_thesis, "");

  L.push("## How to use this");
  L.push("");
  L.push("Work the phases in order — each one assumes the previous is done. Before");
  L.push("proposing an action, check its trigger actually holds; these plays are");
  L.push("conditional, not universal. Where the source contradicts itself the call is");
  L.push("recorded under Judgment calls — follow that, not one side of the argument.");
  L.push("");
  L.push("Conviction is how many modules pushed a play. High conviction means the");
  L.push("creator built their business on it; conviction 1 was said once in passing.");
  L.push("");

  // ---------- the plays ----------
  let phase = null;
  for (const p of playbook.playbook) {
    if (p.phase !== phase) {
      phase = p.phase;
      L.push(`## ${titleCase(phase)}`, "");
    }
    L.push(`### ${p.action}`, "");
    L.push(`**When:** ${p.trigger}`, "");
    L.push(`**Why:** ${p.why}`, "");
    const facts = [`effort: ${p.effort}`, `conviction: ${p.repetition_count}`];
    if (p.prerequisites?.length) facts.push(`needs first: ${p.prerequisites.join("; ")}`);
    L.push(`_${facts.join(" · ")}_`, "");
  }

  // ---------- numbers ----------
  const numbers = distilled.flatMap(({ module, result }) =>
    result.numbers.map((n) => ({ ...n, module: module.title })));
  if (numbers.length) {
    L.push("## Numbers stated in the source", "");
    L.push("Benchmarks and thresholds as given. Treat them as the creator's claims, not");
    L.push("as validated figures — check them against your own data before relying on one.", "");
    L.push("| Metric | Value | Context |");
    L.push("| --- | --- | --- |");
    for (const n of numbers) L.push(`| ${cell(n.metric)} | ${cell(n.value)} | ${cell(n.context)} |`);
    L.push("");
  }

  // ---------- assets ----------
  const assets = distilled.flatMap(({ result }) => result.assets);
  if (assets.length) {
    L.push("## Templates and structures", "");
    for (const kind of [...new Set(assets.map((a) => a.kind))]) {
      L.push(`### ${kindLabel(kind)}`, "");
      for (const a of assets.filter((x) => x.kind === kind)) {
        L.push(`**${a.name}**`, "", a.structure, "");
      }
    }
  }

  // ---------- judgment ----------
  if (playbook.contradictions?.length) {
    L.push("## Judgment calls", "");
    L.push("The source argues with itself here. The resolution is what to follow.", "");
    for (const c of playbook.contradictions) {
      L.push(`### ${c.topic}`, "");
      for (const pos of c.positions) L.push(`- "${pos.claim}" — ${pos.module}`);
      L.push("", `**Follow:** ${c.resolution}`, "");
    }
  }

  if (playbook.ignore?.length) {
    L.push("## Do not act on", "");
    for (const i of playbook.ignore) L.push(`- **${i.claim}** — ${i.reason}`);
    L.push("");
  }

  // ---------- provenance ----------
  L.push("## Provenance", "");
  L.push(`Distilled from ${distilled.length} module(s) of "${course.title}".`);
  L.push(`${playbook.playbook.length} actions retained.`, "");
  const thin = distilled.filter(({ transcript }) => transcript?.source === "none");
  if (thin.length) {
    L.push(`${thin.length} module(s) had no transcript and were read from their text`);
    L.push("notes alone, so their coverage is weaker:", "");
    for (const t of thin) L.push(`- ${t.module.title}`);
    L.push("");
  }
  L.push("This is one creator's method, not established fact. It reflects what worked");
  L.push("in their market at the time of recording.", "");

  return L.join("\n");
}

/** The description is what makes a skill trigger, so it names the work, not the course. */
function describe(course, playbook) {
  const thesis = (playbook.core_thesis ?? "").split(/(?<=\.)\s/)[0].trim();
  const phases = [...new Set(playbook.playbook.map((p) => p.phase))].slice(0, 5);
  const text =
    `Apply the ${course.title} method. ${thesis} ` +
    `Use when working on ${phases.map(lower).join(", ")}, or when asked to act on ` +
    `what ${course.title} teaches.`;
  return one(text).slice(0, MAX_DESC);
}

// Plural headings for asset kinds — "dm" title-cases to the wrong thing.
const KIND_LABELS = {
  script: "Scripts", template: "Templates", post: "Post formats", dm: "DM openers",
  email: "Emails", offer: "Offer structures", checklist: "Checklists", other: "Other",
};
const kindLabel = (k) => KIND_LABELS[k] ?? `${titleCase(k)}s`;

const one = (s) => s.replace(/\s+/g, " ").trim();
const cell = (s) => one(String(s ?? "")).replace(/\|/g, "\\|");
const lower = (s) => String(s ?? "").toLowerCase();
const titleCase = (s) =>
  String(s ?? "").replace(/[-_]/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
