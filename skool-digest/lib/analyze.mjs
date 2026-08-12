// Analysis: transcript -> structured plays -> deduped playbook -> per-brand plan.
//
// Every stage asks Claude for schema-constrained JSON, so downstream code never
// parses prose. Timestamps ride along with each item, which is what makes the
// output checkable — you can jump to the 90 seconds behind any bullet.

import { askJSON } from "./claude.mjs";
import { cached, hash, log } from "./util.mjs";

const EFFORT = ["trivial", "small", "medium", "large"];
const IMPACT = ["low", "medium", "high"];

// ---------- stage 1: per-video extraction ----------

const DISTILL_SCHEMA = {
  type: "object",
  additionalProperties: false,
  required: ["one_line_summary", "plays", "numbers", "assets", "prerequisites", "filler_ratio", "worth_watching"],
  properties: {
    one_line_summary: { type: "string" },
    worth_watching: { type: "boolean" },
    filler_ratio: { type: "number" },
    plays: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        required: ["action", "trigger", "detail", "timestamp"],
        properties: {
          action: { type: "string" },
          trigger: { type: "string" },
          detail: { type: "string" },
          timestamp: { type: "string" },
        },
      },
    },
    numbers: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        required: ["metric", "value", "context", "timestamp"],
        properties: {
          metric: { type: "string" },
          value: { type: "string" },
          context: { type: "string" },
          timestamp: { type: "string" },
        },
      },
    },
    assets: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        required: ["kind", "name", "structure", "timestamp"],
        properties: {
          kind: { type: "string", enum: ["script", "template", "post", "dm", "email", "offer", "checklist", "other"] },
          name: { type: "string" },
          structure: { type: "string" },
          timestamp: { type: "string" },
        },
      },
    },
    prerequisites: { type: "array", items: { type: "string" } },
  },
};

const DISTILL_SYSTEM = `You extract the operational substance from long, slow-paced business course videos.

The person reading your output has paid for this course and wants to implement it without watching every hour of video. Your job is signal extraction, not summary.

Rules:
- A "play" is a concrete action someone could put on a to-do list. "Post consistently" is not a play. "Post one win from a member every Tuesday, tagging the member" is. Include the trigger — the condition under which the play applies ("once you pass 30 members", "before you raise your price").
- Capture every number stated: prices, conversion rates, member counts, timeframes, thresholds, benchmarks. These are the most valuable and most easily lost details.
- For assets (scripts, templates, post formats, DM openers, offer structures): describe the STRUCTURE and the reasoning — the beats it moves through, what each beat is doing, and the specific angle that makes it work. Write it as a reusable skeleton the reader can fill in for their own business, in your own words. Do not transcribe the speaker's wording at length.
- prerequisites: what must already be true for this video's advice to apply.
- filler_ratio: your honest estimate (0 to 1) of how much of this video was padding — story, repetition, self-promotion, throat-clearing.
- worth_watching: true only if there is material here that your extraction genuinely cannot carry (a demo, a walkthrough, a nuance that needs seeing).
- Every item carries a timestamp in m:ss or h:mm:ss form, taken from the nearest transcript marker.
- Return empty arrays rather than padding. A video that says nothing should extract to nothing.`;

export async function distill({ apiKey, module, transcript }) {
  const key = hash(module.title, transcript.text.slice(0, 20000), transcript.text.length, DISTILL_SYSTEM);
  return cached("distill", key, async () => {
    const user = [
      `MODULE: ${module.title}`,
      module.body ? `\nMODULE NOTES:\n${module.body.slice(0, 4000)}` : "",
      transcript.text
        ? `\nTRANSCRIPT (timestamps in brackets):\n${transcript.text}`
        : "\n(No transcript available — extract from the module notes alone.)",
    ].join("\n");

    return askJSON({
      apiKey,
      system: DISTILL_SYSTEM,
      user,
      schema: DISTILL_SCHEMA,
      maxTokens: 16000,
      effort: "high",
      cacheSystem: true,
    });
  });
}

// ---------- stage 2: course-wide roll-up ----------

const ROLLUP_SCHEMA = {
  type: "object",
  additionalProperties: false,
  required: ["core_thesis", "playbook", "contradictions", "ignore"],
  properties: {
    core_thesis: { type: "string" },
    playbook: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        required: ["id", "action", "why", "trigger", "phase", "effort", "prerequisites", "repetition_count", "evidence"],
        properties: {
          id: { type: "string" },
          action: { type: "string" },
          why: { type: "string" },
          trigger: { type: "string" },
          phase: { type: "string" },
          effort: { type: "string", enum: EFFORT },
          repetition_count: { type: "integer" },
          prerequisites: { type: "array", items: { type: "string" } },
          evidence: {
            type: "array",
            items: {
              type: "object",
              additionalProperties: false,
              required: ["module", "timestamp"],
              properties: { module: { type: "string" }, timestamp: { type: "string" } },
            },
          },
        },
      },
    },
    contradictions: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        required: ["topic", "positions", "resolution"],
        properties: {
          topic: { type: "string" },
          resolution: { type: "string" },
          positions: {
            type: "array",
            items: {
              type: "object",
              additionalProperties: false,
              required: ["claim", "module", "timestamp"],
              properties: { claim: { type: "string" }, module: { type: "string" }, timestamp: { type: "string" } },
            },
          },
        },
      },
    },
    ignore: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        required: ["claim", "reason"],
        properties: { claim: { type: "string" }, reason: { type: "string" } },
      },
    },
  },
};

const ROLLUP_SYSTEM = `You consolidate extracted notes from every video in one course into a single operational playbook.

Course creators repeat themselves constantly, so your main job is compression and ordering.

- Collapse the same play stated many ways into ONE entry. Set repetition_count to how many videos pushed it — a high count is the strongest signal of what the creator actually believes, versus what they mentioned once.
- Order the playbook by dependency: what must happen before what. Use "phase" for the stage it belongs to (e.g. "foundation", "first 30 members", "monetize", "scale"). List entries in the order they should be executed.
- prerequisites: what must be true before this play works. Be concrete.
- contradictions: places where the course disagrees with itself, usually because the creator changed their mind between recordings. Give the competing claims with their sources, and your read on which to follow and why.
- ignore: advice you judge to be filler, self-promotion, unfalsifiable motivation, or a claim contradicted by the rest of the course. Say why in one line.
- core_thesis: in two or three sentences, the actual argument of this course, stripped of the sales language.
- Keep evidence entries so every play traces back to specific videos and timestamps.
- Aim for the smallest playbook that loses nothing. If forty hours of video reduce to twenty five real actions, that is the correct answer.`;

export async function rollup({ apiKey, course, distilled }) {
  const payload = distilled.map(({ module, result }) => ({
    module: module.title,
    summary: result.one_line_summary,
    filler_ratio: result.filler_ratio,
    plays: result.plays,
    numbers: result.numbers,
    assets: result.assets.map((a) => ({ kind: a.kind, name: a.name, timestamp: a.timestamp })),
    prerequisites: result.prerequisites,
  }));

  return askJSON({
    apiKey,
    system: ROLLUP_SYSTEM,
    user: `COURSE: ${course.title}\nMODULES: ${payload.length}\n\nEXTRACTED NOTES (JSON):\n${JSON.stringify(payload)}`,
    schema: ROLLUP_SCHEMA,
    maxTokens: 32000,
    effort: "xhigh",
  });
}

// ---------- stage 3: apply to one business ----------

const APPLY_SCHEMA = {
  type: "object",
  additionalProperties: false,
  required: ["brand", "read", "ranked", "skipped", "thirty_days"],
  properties: {
    brand: { type: "string" },
    read: { type: "string" },
    ranked: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        required: ["play_id", "adapted_action", "impact", "effort", "first_step", "why_this_brand"],
        properties: {
          play_id: { type: "string" },
          adapted_action: { type: "string" },
          impact: { type: "string", enum: IMPACT },
          effort: { type: "string", enum: EFFORT },
          first_step: { type: "string" },
          why_this_brand: { type: "string" },
        },
      },
    },
    skipped: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        required: ["play_id", "reason"],
        properties: { play_id: { type: "string" }, reason: { type: "string" } },
      },
    },
    thirty_days: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        required: ["week", "focus", "actions"],
        properties: {
          week: { type: "integer" },
          focus: { type: "string" },
          actions: { type: "array", items: { type: "string" } },
        },
      },
    },
  },
};

const APPLY_SYSTEM = `You adapt a generic course playbook to one specific business.

- Rewrite each surviving play as a concrete action for THIS business, using its real audience, offer, and channels. Generic restatements are useless; if you cannot make it specific, skip it.
- Rank by impact against effort. Put the highest-impact, lowest-effort actions first.
- Skip plays whose prerequisites this business does not meet, or that do not fit its model. Say plainly why — the skips are as useful as the picks.
- first_step: the single next physical action, small enough to do in one sitting.
- thirty_days: four weeks, each with a focus and two to four actions drawn from your ranked list. Sequence it so each week's work is possible given the previous week's.
- read: two or three sentences on how well this course actually fits this business, including where it does not.`;

export async function apply({ apiKey, playbook, brandName, brandContext }) {
  return askJSON({
    apiKey,
    system: APPLY_SYSTEM,
    user: [
      `BUSINESS: ${brandName}`,
      `\nBUSINESS CONTEXT:\n${brandContext}`,
      `\nPLAYBOOK (JSON):\n${JSON.stringify({ core_thesis: playbook.core_thesis, playbook: playbook.playbook })}`,
    ].join("\n"),
    schema: APPLY_SCHEMA,
    maxTokens: 24000,
    effort: "xhigh",
  });
}

export { EFFORT, IMPACT };
