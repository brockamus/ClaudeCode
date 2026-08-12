// Thin Claude API wrapper with structured (schema-constrained) JSON output.
//
// Raw fetch, matching copyroom.mjs — keeps this tool zero-install. If you'd
// rather use @anthropic-ai/sdk, this is the only file that needs to change.

const API = "https://api.anthropic.com/v1/messages";
const VERSION = "2023-06-01";
export const MODEL = "claude-opus-5";

// Non-streaming above ~16k max_tokens risks an HTTP timeout, so stream past that.
const STREAM_THRESHOLD = 16000;

/**
 * Ask Claude for JSON matching `schema`. Returns the parsed object.
 *
 * @param {object} o
 * @param {string} o.apiKey
 * @param {string} o.system
 * @param {string} o.user
 * @param {object} o.schema        JSON Schema (objects need additionalProperties:false + required)
 * @param {number} [o.maxTokens]
 * @param {string} [o.effort]      low | medium | high | xhigh | max
 * @param {boolean} [o.cacheSystem] cache the system prompt across calls
 */
export async function askJSON({ apiKey, system, user, schema, maxTokens = 16000, effort = "high", cacheSystem = false }) {
  const body = {
    model: MODEL,
    max_tokens: maxTokens,
    thinking: { type: "adaptive" },
    output_config: {
      effort,
      format: { type: "json_schema", schema },
    },
    system: cacheSystem
      ? [{ type: "text", text: system, cache_control: { type: "ephemeral" } }]
      : system,
    messages: [{ role: "user", content: user }],
  };

  const text = maxTokens > STREAM_THRESHOLD
    ? await streamText(apiKey, body)
    : await createText(apiKey, body);

  try {
    return JSON.parse(text);
  } catch {
    throw new Error(`Model returned unparseable JSON (first 400 chars):\n${text.slice(0, 400)}`);
  }
}

async function post(apiKey, body, stream) {
  const r = await fetch(API, {
    method: "POST",
    headers: {
      "x-api-key": apiKey,
      "anthropic-version": VERSION,
      "content-type": "application/json",
    },
    body: JSON.stringify(stream ? { ...body, stream: true } : body),
  });
  if (!r.ok) throw new Error(`Anthropic ${r.status}: ${(await r.text()).slice(0, 500)}`);
  return r;
}

async function createText(apiKey, body) {
  const data = await (await post(apiKey, body, false)).json();
  if (data.stop_reason === "refusal") {
    throw new Error(`Request refused (${data.stop_details?.category ?? "unknown"}): ${data.stop_details?.explanation ?? ""}`);
  }
  if (data.stop_reason === "max_tokens") {
    throw new Error("Hit max_tokens before finishing — raise maxTokens or split the input.");
  }
  return textOf(data.content);
}

async function streamText(apiKey, body) {
  const r = await post(apiKey, body, true);
  const reader = r.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "", out = "", stopReason = null;

  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop();
    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      let ev;
      try { ev = JSON.parse(line.slice(6)); } catch { continue; }
      if (ev.type === "content_block_delta" && ev.delta?.type === "text_delta") out += ev.delta.text;
      if (ev.type === "message_delta" && ev.delta?.stop_reason) stopReason = ev.delta.stop_reason;
    }
  }
  if (stopReason === "refusal") throw new Error("Request refused by the model.");
  if (stopReason === "max_tokens") throw new Error("Hit max_tokens mid-stream — raise maxTokens or split the input.");
  return out;
}

const textOf = (content) =>
  (content ?? []).filter((b) => b.type === "text").map((b) => b.text).join("");
