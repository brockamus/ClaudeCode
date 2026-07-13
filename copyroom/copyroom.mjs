#!/usr/bin/env node
// Copy Room — 3-AI collaborative copywriting loop.
// Usage: copyroom [--brand <name>] [--rounds N] [--threshold N] "<brief>"

import { readFileSync, mkdirSync, writeFileSync, existsSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ROOT = dirname(fileURLToPath(import.meta.url));

const MODELS = {
  gpt:    { label: "GPT",    model: "gpt-5.6" },
  claude: { label: "Claude", model: "claude-opus-4-8" },
  grok:   { label: "Grok",   model: "grok-4.5" },
};
const MERGE_EDITOR = "claude";
const REVISE_ROTATION = ["gpt", "grok", "claude"];

// ---------- env ----------
const env = {};
try {
  for (const line of readFileSync(join(ROOT, ".env"), "utf8").split("\n")) {
    const i = line.indexOf("=");
    if (i > 0 && !line.startsWith("#")) env[line.slice(0, i).trim()] = line.slice(i + 1).trim().replace(/^["']|["']$/g, "");
  }
} catch { /* fall through to key check */ }
const KEYS = { gpt: env.OPENAI_API_KEY, claude: env.ANTHROPIC_API_KEY, grok: env.XAI_API_KEY };
const KEY_NAMES = { gpt: "OPENAI_API_KEY", claude: "ANTHROPIC_API_KEY", grok: "XAI_API_KEY" };
for (const [id, k] of Object.entries(KEYS)) {
  if (!k) { console.error(`Missing API key for ${MODELS[id].label}. Set ${KEY_NAMES[id]} in ${join(ROOT, ".env")}`); process.exit(1); }
}

// ---------- args ----------
const argv = process.argv.slice(2);
let brand = null, rounds = 3, threshold = 8, brief = null;
for (let i = 0; i < argv.length; i++) {
  if (argv[i] === "--brand") brand = argv[++i];
  else if (argv[i] === "--rounds") rounds = parseInt(argv[++i], 10);
  else if (argv[i] === "--threshold") threshold = parseFloat(argv[++i]);
  else if (!brief) brief = argv[i];
}
if (!brief) { console.error(`Usage: copyroom [--brand <name>] [--rounds N] [--threshold N] "<brief>"`); process.exit(1); }
let brandContext = "";
if (brand) {
  const f = join(ROOT, "brands", `${brand}.md`);
  if (!existsSync(f)) {
    const available = existsSync(join(ROOT, "brands")) ? readdirSync(join(ROOT, "brands")).filter(n => n.endsWith(".md")).map(n => n.replace(/\.md$/, "")).join(", ") : "(none)";
    console.error(`No brand file: ${f}\nAvailable brands: ${available || "(none)"}`);
    process.exit(1);
  }
  brandContext = readFileSync(f, "utf8");
}

// ---------- providers ----------
const alive = new Set(Object.keys(MODELS));
const transcript = [];
function log(section, body) { transcript.push(`## ${section}\n\n${body}\n`); }

async function rawCall(id, system, user, maxTokens) {
  const { model } = MODELS[id];
  if (id === "claude") {
    const r = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: { "x-api-key": KEYS.claude, "anthropic-version": "2023-06-01", "content-type": "application/json" },
      body: JSON.stringify({ model, max_tokens: maxTokens, system, thinking: { type: "adaptive" }, messages: [{ role: "user", content: user }] }),
    });
    if (!r.ok) throw new Error(`Anthropic ${r.status}: ${(await r.text()).slice(0, 300)}`);
    const d = await r.json();
    return d.content.filter(b => b.type === "text").map(b => b.text).join("\n").trim();
  }
  const url = id === "gpt" ? "https://api.openai.com/v1/chat/completions" : "https://api.x.ai/v1/chat/completions";
  const key = id === "gpt" ? KEYS.gpt : KEYS.grok;
  const body = { model, messages: [{ role: "system", content: system }, { role: "user", content: user }] };
  if (id === "gpt") body.max_completion_tokens = maxTokens; else body.max_tokens = maxTokens;
  const r = await fetch(url, {
    method: "POST",
    headers: { authorization: `Bearer ${key}`, "content-type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`${MODELS[id].label} ${r.status}: ${(await r.text()).slice(0, 300)}`);
  return (await r.json()).choices[0].message.content.trim();
}

async function ask(id, system, user, maxTokens = 4000) {
  try { return await rawCall(id, system, user, maxTokens); }
  catch (e) {
    console.error(`  ${MODELS[id].label} error, retrying once: ${e.message}`);
    try { return await rawCall(id, system, user, maxTokens); }
    catch (e2) {
      alive.delete(id);
      console.error(`  ${MODELS[id].label} is down — continuing without it (${e2.message})`);
      log(`${MODELS[id].label} DROPPED`, e2.message);
      if (alive.size < 2) { console.error("Fewer than 2 providers alive — aborting."); finish(null, []); process.exit(1); }
      return null;
    }
  }
}

// ---------- prompts ----------
const baseSystem = `You are an elite direct-response copywriter working in a three-AI "copy room" (GPT, Claude, Grok collaborating). Write copy that sells without sounding like AI. Concrete benefits over vague claims. Match the format the brief asks for (ad, product page, email, etc).${brandContext ? `\n\nBRAND GUIDE — follow this voice strictly:\n${brandContext}` : ""}`;

const critiqueSystem = `${baseSystem}\n\nYou are now reviewing a draft. Respond with ONLY a JSON object, no markdown fences, no prose: {"score": <1-10 number, 10 = ship it as-is>, "strengths": ["..."], "fixes": ["specific actionable fix", "..."]}. Score honestly — an 8+ means you would ship it unchanged.`;

function parseCritique(text) {
  try { return JSON.parse(text.replace(/^```(json)?/m, "").replace(/```\s*$/m, "").trim()); }
  catch { return null; }
}

async function critique(id, draft) {
  const user = `BRIEF:\n${brief}\n\nCURRENT DRAFT:\n${draft}\n\nScore and critique this draft. JSON only.`;
  let text = await ask(id, critiqueSystem, user, 1500);
  if (text === null) return null;
  let c = parseCritique(text);
  if (!c) {
    text = await ask(id, critiqueSystem, user + "\n\nYour previous reply was not valid JSON. Reply with ONLY the JSON object.", 1500);
    if (text === null) return null;
    c = parseCritique(text);
  }
  if (!c) {
    const m = text.match(/(\d+(?:\.\d+)?)/);
    c = { score: m ? parseFloat(m[1]) : 0, strengths: [], fixes: [text] };
  }
  if (!Array.isArray(c.strengths)) c.strengths = [];
  if (!Array.isArray(c.fixes)) c.fixes = [];
  c.score = Math.max(1, Math.min(10, Number(c.score) || 0));
  return c;
}

// ---------- output ----------
const slug = brief.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").split("-").slice(0, 6).join("-");
const runDir = join(ROOT, "runs", `${new Date().toISOString().slice(0, 10)}-${slug}`);
function finish(finalDraft, verdicts) {
  mkdirSync(runDir, { recursive: true });
  writeFileSync(join(runDir, "transcript.md"), `# Copy Room transcript\n\n**Brief:** ${brief}\n**Brand:** ${brand ?? "(none)"}\n\n${transcript.join("\n")}`);
  if (finalDraft) {
    const scoreTable = verdicts.map(v => `| ${v.label} | ${v.score}/10 | ${v.verdict} |`).join("\n");
    writeFileSync(join(runDir, "final.md"), `# Final copy\n\n**Brief:** ${brief}\n**Brand:** ${brand ?? "(none)"}\n\n---\n\n${finalDraft}\n\n---\n\n## Verdicts\n\n| Model | Score | Verdict |\n|---|---|---|\n${scoreTable}\n`);
  }
  console.log(`\nSaved: ${runDir}`);
}

// ---------- the loop ----------
console.log(`Copy Room — ${Object.values(MODELS).map(m => m.label).join(" + ")}`);
console.log(`Brief: ${brief}\nBrand: ${brand ?? "(none)"} | rounds ≤ ${rounds} | threshold ${threshold}\n`);

// Round 0: parallel drafts
console.log("Round 0: drafting (3 in parallel)...");
const draftUser = `BRIEF:\n${brief}\n\nWrite your best version of this copy. Copy only — no commentary, no options, one version.`;
const draftIds = [...alive];
const drafts = await Promise.all(draftIds.map(id => ask(id, baseSystem, draftUser)));
const draftPairs = draftIds.map((id, i) => [id, drafts[i]]).filter(([, d]) => d !== null);
for (const [id, d] of draftPairs) log(`Draft — ${MODELS[id].label}`, d);

// Merge
const mergeEditor = alive.has(MERGE_EDITOR) ? MERGE_EDITOR : [...alive][0];
console.log(`Merge: ${MODELS[mergeEditor].label} combining ${draftPairs.length} drafts...`);
let candidate = await ask(
  mergeEditor,
  baseSystem,
  `BRIEF:\n${brief}\n\n${draftPairs.map(([id, d]) => `DRAFT FROM ${MODELS[id].label.toUpperCase()}:\n${d}`).join("\n\n")}\n\nMerge the strongest elements of these drafts into ONE best version. Keep the sharpest hook, the most persuasive body, the strongest CTA — regardless of whose draft they came from. Output the merged copy only, no commentary.`
);
if (candidate === null) { console.error("Merge failed."); finish(null, []); process.exit(1); }
log(`Merged candidate — ${MODELS[mergeEditor].label}`, candidate);

// Refine rounds
let verdicts = [];
for (let round = 1; round <= rounds; round++) {
  const ids = [...alive];
  const crits = await Promise.all(ids.map(id => critique(id, candidate)));
  const pairs = ids.map((id, i) => [id, crits[i]]).filter(([, c]) => c !== null);
  verdicts = pairs.map(([id, c]) => ({ label: MODELS[id].label, score: c.score, verdict: (c.strengths[0] ?? c.fixes[0] ?? "").slice(0, 140) }));
  const scoreLine = pairs.map(([id, c]) => `${MODELS[id].label} ${c.score}/10`).join(" | ");
  console.log(`Round ${round}: ${scoreLine}`);
  for (const [id, c] of pairs) log(`Round ${round} critique — ${MODELS[id].label}`, "```json\n" + JSON.stringify(c, null, 2) + "\n```");

  if (pairs.every(([, c]) => c.score >= threshold)) { console.log(`Consensus reached — all scores ≥ ${threshold}.`); break; }
  if (round === rounds) { console.log(`Round cap hit (${rounds}) — shipping best current version.`); break; }

  const rotation = REVISE_ROTATION.filter(id => alive.has(id));
  const editor = rotation[(round - 1) % rotation.length];
  console.log(`  ${MODELS[editor].label} revising...`);
  const fixes = pairs.flatMap(([id, c]) => c.fixes.map(f => `- [${MODELS[id].label}] ${f}`)).join("\n");
  const revised = await ask(
    editor,
    baseSystem,
    `BRIEF:\n${brief}\n\nCURRENT DRAFT:\n${candidate}\n\nFIXES REQUESTED BY THE ROOM:\n${fixes}\n\nRevise the draft applying these fixes. Preserve what the room scored well; change only what needs changing. Output the revised copy only.`
  );
  if (revised !== null) { candidate = revised; log(`Round ${round} revision — ${MODELS[editor].label}`, candidate); }
}

console.log(`\n${"=".repeat(60)}\n${candidate}\n${"=".repeat(60)}`);
finish(candidate, verdicts);
