// Transcription: captions where they exist, speech-to-text where they don't.
//
// Strategy is host-agnostic: yt-dlp already knows YouTube, Loom, Vimeo, Wistia
// and plain media URLs, so we ask it for subtitles first (free, instant) and
// only fall back to downloading audio + paying for transcription.

import { spawn, spawnSync } from "node:child_process";
import { existsSync, mkdtempSync, readdirSync, readFileSync, rmSync, statSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { cached, hash, hhmmss, log } from "./util.mjs";

const CHUNK_SECONDS = 900;              // 15 min per transcription chunk
const MAX_UPLOAD_BYTES = 24 * 1024 * 1024;

/**
 * yt-dlp arguments carrying your Skool session. Course videos are typically
 * unlisted or member-gated, so an anonymous fetch 403s and the module silently
 * transcribes to nothing. Prefers an explicit cookie jar, else the browser
 * profile the crawler already logged in with.
 */
export function cookieArgs({ cookiesFile, cookiesFromBrowser, profileDir } = {}) {
  if (cookiesFile) return ["--cookies", cookiesFile];
  if (cookiesFromBrowser) return ["--cookies-from-browser", cookiesFromBrowser];
  if (profileDir && existsSync(profileDir)) return ["--cookies-from-browser", `chromium:${profileDir}`];
  return [];
}

export function haveBinary(name) {
  try {
    const r = spawnSync(name, ["--version"], { stdio: "ignore" });
    return !r.error;
  } catch { return false; }
}

/**
 * Get a transcript for a video URL.
 * Returns { url, source: "captions"|"speech"|"none", segments: [{start, text}], text }
 */
export async function transcribe(url, { openaiKey, allowPaid = true, cookies = [] } = {}) {
  return cached("transcripts", hash(url), async () => {
    const dir = mkdtempSync(join(tmpdir(), "skool-digest-"));
    try {
      const subs = await fetchCaptions(url, dir, cookies);
      if (subs?.length) {
        log(`    captions: ${subs.length} segments`);
        return pack(url, "captions", subs);
      }

      if (!allowPaid) return pack(url, "none", []);
      if (!openaiKey) {
        log("    no captions and no OPENAI_API_KEY — skipping speech-to-text");
        return pack(url, "none", []);
      }

      const audio = await fetchAudio(url, dir, cookies);
      if (!audio) return pack(url, "none", []);
      const segments = await speechToText(audio, dir, openaiKey);
      log(`    speech-to-text: ${segments.length} segments`);
      return pack(url, "speech", segments);
    } catch (e) {
      log(`    transcription failed: ${e.message}`);
      return pack(url, "none", []);
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });
}

function pack(url, source, segments) {
  return {
    url,
    source,
    segments,
    text: segments.map((s) => `[${hhmmss(s.start)}] ${s.text}`).join("\n"),
  };
}

// ---------- captions ----------

async function fetchCaptions(url, dir, cookies = []) {
  const ok = await run("yt-dlp", [
    ...cookies,
    "--skip-download",
    "--write-subs", "--write-auto-subs",
    "--sub-langs", "en.*,en",
    "--sub-format", "vtt",
    "--no-warnings",
    "-o", join(dir, "sub"),
    url,
  ]);
  if (!ok) return null;

  const vtt = readdirSync(dir).filter((f) => f.endsWith(".vtt")).sort();
  if (!vtt.length) return null;
  // Prefer a manual track over an auto-generated one.
  const pick = vtt.find((f) => !/auto/i.test(f)) ?? vtt[0];
  return parseVTT(readFileSync(join(dir, pick), "utf8"));
}

/** WebVTT -> [{start, text}], de-duplicated (auto-captions repeat rolling lines). */
export function parseVTT(vtt) {
  const segments = [];
  let last = "";
  for (const block of vtt.replace(/\r/g, "").split("\n\n")) {
    const lines = block.split("\n").filter(Boolean);
    const timeIdx = lines.findIndex((l) => l.includes("-->"));
    if (timeIdx === -1) continue;

    const start = vttSeconds(lines[timeIdx].split("-->")[0].trim());
    const text = lines.slice(timeIdx + 1)
      .join(" ")
      .replace(/<[^>]*>/g, "")          // inline karaoke timing tags
      .replace(/&nbsp;/g, " ")
      .replace(/\s+/g, " ")
      .trim();
    if (!text || text === last) continue;

    // Auto-captions scroll: each cue repeats the tail of the previous one.
    const trimmed = last && text.startsWith(last) ? text.slice(last.length).trim() : text;
    if (trimmed) segments.push({ start, text: trimmed });
    last = text;
  }
  return segments;
}

const vttSeconds = (stamp) => {
  const [hms, ms = "0"] = stamp.split(".");
  const parts = hms.split(":").map(Number);
  return parts.reduce((a, n) => a * 60 + n, 0) + Number(ms) / 1000;
};

// ---------- audio + speech-to-text ----------

async function fetchAudio(url, dir, cookies = []) {
  const ok = await run("yt-dlp", [
    ...cookies,
    "-x", "--audio-format", "mp3",
    "--postprocessor-args", "ffmpeg:-ac 1 -ar 16000 -b:a 32k",
    "--no-warnings",
    "-o", join(dir, "audio.%(ext)s"),
    url,
  ]);
  if (!ok) return null;
  const file = readdirSync(dir).find((f) => f.startsWith("audio.") && f.endsWith(".mp3"));
  return file ? join(dir, file) : null;
}

async function speechToText(audioPath, dir, openaiKey) {
  const chunks = statSync(audioPath).size > MAX_UPLOAD_BYTES
    ? await splitAudio(audioPath, dir)
    : [audioPath];

  const segments = [];
  for (const [i, chunk] of chunks.entries()) {
    const offset = chunks.length > 1 ? i * CHUNK_SECONDS : 0;
    log(`      transcribing chunk ${i + 1}/${chunks.length}`);
    for (const s of await whisper(chunk, openaiKey)) {
      segments.push({ start: s.start + offset, text: s.text });
    }
  }
  return segments;
}

async function splitAudio(audioPath, dir) {
  const ok = await run("ffmpeg", [
    "-hide_banner", "-loglevel", "error",
    "-i", audioPath,
    "-f", "segment", "-segment_time", String(CHUNK_SECONDS), "-c", "copy",
    join(dir, "chunk_%03d.mp3"),
  ]);
  if (!ok) return [audioPath];
  return readdirSync(dir).filter((f) => f.startsWith("chunk_")).sort().map((f) => join(dir, f));
}

async function whisper(path, openaiKey) {
  const form = new FormData();
  form.append("file", new File([readFileSync(path)], "audio.mp3", { type: "audio/mpeg" }));
  form.append("model", "whisper-1");
  form.append("response_format", "verbose_json");

  const r = await fetch("https://api.openai.com/v1/audio/transcriptions", {
    method: "POST",
    headers: { authorization: `Bearer ${openaiKey}` },
    body: form,
  });
  if (!r.ok) throw new Error(`Transcription ${r.status}: ${(await r.text()).slice(0, 300)}`);
  const data = await r.json();
  return (data.segments ?? [{ start: 0, text: data.text ?? "" }])
    .map((s) => ({ start: s.start ?? 0, text: (s.text ?? "").trim() }))
    .filter((s) => s.text);
}

// ---------- process helpers ----------

function run(cmd, args) {
  return new Promise((resolve) => {
    const child = spawn(cmd, args, { stdio: ["ignore", "ignore", "pipe"] });
    let err = "";
    child.stderr.on("data", (d) => { err += d.toString(); });
    child.on("error", () => resolve(false));
    child.on("close", (code) => {
      if (code !== 0 && err.trim()) log(`    ${cmd}: ${err.trim().split("\n").slice(-1)[0]}`);
      resolve(code === 0);
    });
  });
}

