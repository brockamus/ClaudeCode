// Markdown renderers for each artifact. Nothing clever — the JSON is the
// source of truth; these exist so the output is readable on a phone.

const bullet = (s) => `- ${s}`;
const stamp = (e) => `${e.module} @ ${e.timestamp}`;

export function renderPlaybook(course, playbook, distilled) {
  const L = [];
  L.push(`# ${course.title} — playbook`, "");
  L.push(`_${playbook.playbook.length} actions distilled from ${distilled.length} modules._`, "");

  L.push("## The actual argument", "", playbook.core_thesis, "");

  L.push("## Playbook", "");
  let phase = null;
  for (const p of playbook.playbook) {
    if (p.phase !== phase) {
      phase = p.phase;
      L.push(`### ${phase}`, "");
    }
    L.push(`#### ${p.action}`, "");
    L.push(`**When:** ${p.trigger}  `);
    L.push(`**Why:** ${p.why}  `);
    L.push(`**Effort:** ${p.effort} · **Repeated in ${p.repetition_count} module(s)**  `);
    if (p.prerequisites.length) L.push(`**Needs first:** ${p.prerequisites.join("; ")}  `);
    if (p.evidence.length) L.push(`**Source:** ${p.evidence.map(stamp).join(" · ")}`);
    L.push("");
  }

  if (playbook.contradictions.length) {
    L.push("## Where the course contradicts itself", "");
    for (const c of playbook.contradictions) {
      L.push(`### ${c.topic}`, "");
      for (const pos of c.positions) L.push(bullet(`"${pos.claim}" — ${stamp(pos)}`));
      L.push("", `**Read:** ${c.resolution}`, "");
    }
  }

  if (playbook.ignore.length) {
    L.push("## Safe to ignore", "");
    for (const i of playbook.ignore) L.push(bullet(`**${i.claim}** — ${i.reason}`));
    L.push("");
  }

  return L.join("\n");
}

export function renderNumbers(course, distilled) {
  const rows = [];
  for (const { module, result } of distilled) {
    for (const n of result.numbers) {
      rows.push(`| ${esc(n.metric)} | ${esc(n.value)} | ${esc(n.context)} | ${esc(module.title)} @ ${n.timestamp} |`);
    }
  }
  if (!rows.length) return `# ${course.title} — numbers\n\nNo figures were stated in this course.\n`;
  return [
    `# ${course.title} — every number stated`,
    "",
    "| Metric | Value | Context | Source |",
    "| --- | --- | --- | --- |",
    ...rows,
    "",
  ].join("\n");
}

export function renderAssets(course, distilled) {
  const L = [`# ${course.title} — templates and scripts`, ""];
  L.push("_Reusable skeletons, reconstructed from the course. Fill in your own specifics._", "");
  let any = false;
  for (const { module, result } of distilled) {
    if (!result.assets.length) continue;
    any = true;
    L.push(`## ${module.title}`, "");
    for (const a of result.assets) {
      L.push(`### ${a.name} _(${a.kind})_`, "", a.structure, "", `_Source: ${module.title} @ ${a.timestamp}_`, "");
    }
  }
  if (!any) L.push("No templates or scripts were given in this course.", "");
  return L.join("\n");
}

export function renderCoverage(course, distilled) {
  const L = [`# ${course.title} — module coverage`, ""];
  L.push("| Module | Plays | Numbers | Filler | Worth watching |");
  L.push("| --- | --: | --: | --: | --- |");
  for (const { module, result, transcript } of distilled) {
    const filler = `${Math.round((result.filler_ratio ?? 0) * 100)}%`;
    const watch = result.worth_watching ? "**yes**" : "no";
    const src = transcript?.source === "none" ? " _(no transcript)_" : "";
    L.push(`| ${esc(module.title)}${src} | ${result.plays.length} | ${result.numbers.length} | ${filler} | ${watch} |`);
  }
  const watchable = distilled.filter((d) => d.result.worth_watching);
  L.push("", `**${watchable.length} of ${distilled.length} modules are worth actually watching:**`, "");
  for (const d of watchable) L.push(bullet(`${d.module.title} — ${d.result.one_line_summary}`));
  L.push("");
  return L.join("\n");
}

export function renderApplied(course, plan) {
  const L = [`# ${plan.brand} — action plan from "${course.title}"`, ""];
  L.push(plan.read, "");

  L.push("## Ranked actions", "");
  for (const [i, r] of plan.ranked.entries()) {
    L.push(`### ${i + 1}. ${r.adapted_action}`, "");
    L.push(`**Impact:** ${r.impact} · **Effort:** ${r.effort}  `);
    L.push(`**Why here:** ${r.why_this_brand}  `);
    L.push(`**Start with:** ${r.first_step}`, "");
  }

  if (plan.thirty_days.length) {
    L.push("## First 30 days", "");
    for (const w of plan.thirty_days) {
      L.push(`### Week ${w.week} — ${w.focus}`, "");
      for (const a of w.actions) L.push(bullet(a));
      L.push("");
    }
  }

  if (plan.skipped.length) {
    L.push("## Skipped, and why", "");
    for (const s of plan.skipped) L.push(bullet(`\`${s.play_id}\` — ${s.reason}`));
    L.push("");
  }

  return L.join("\n");
}

const esc = (s) => String(s ?? "").replace(/\|/g, "\\|").replace(/\n/g, " ");
