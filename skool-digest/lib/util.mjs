// Shared helpers: env loading, caching, small utilities.

import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { createHash } from "node:crypto";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

export const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
export const CACHE = join(ROOT, "cache");
export const OUT = join(ROOT, "out");

// ---------- env ----------
export function loadEnv() {
  const env = { ...process.env };
  try {
    for (const line of readFileSync(join(ROOT, ".env"), "utf8").split("\n")) {
      const i = line.indexOf("=");
      if (i > 0 && !line.startsWith("#")) {
        env[line.slice(0, i).trim()] = line.slice(i + 1).trim().replace(/^["']|["']$/g, "");
      }
    }
  } catch { /* no .env — fall back to process.env */ }
  return env;
}

export function requireKey(env, name, why) {
  if (!env[name]) {
    console.error(`Missing ${name} (needed for ${why}). Set it in ${join(ROOT, ".env")} or export it.`);
    process.exit(1);
  }
  return env[name];
}

// ---------- fs ----------
export function readJSON(path) { return JSON.parse(readFileSync(path, "utf8")); }

export function writeJSON(path, data) {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, JSON.stringify(data, null, 2));
  return path;
}

export function writeText(path, text) {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, text);
  return path;
}

// ---------- cache ----------
export function hash(...parts) {
  return createHash("sha256").update(parts.join("\u0000")).digest("hex").slice(0, 16);
}

// Cache keyed by an opaque string. Returns cached value or runs fn and stores it.
export async function cached(bucket, key, fn) {
  const path = join(CACHE, bucket, `${key}.json`);
  if (existsSync(path)) {
    try { return readJSON(path); } catch { /* corrupt entry — recompute */ }
  }
  const value = await fn();
  writeJSON(path, value);
  return value;
}

// ---------- misc ----------
export const slug = (s) =>
  String(s).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 60) || "untitled";

export const hhmmss = (seconds) => {
  const s = Math.max(0, Math.floor(seconds));
  const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), sec = s % 60;
  const pad = (n) => String(n).padStart(2, "0");
  return h > 0 ? `${h}:${pad(m)}:${pad(sec)}` : `${m}:${pad(sec)}`;
};

export const toSeconds = (stamp) => {
  const parts = String(stamp).split(":").map(Number);
  if (parts.some(Number.isNaN)) return 0;
  return parts.reduce((acc, n) => acc * 60 + n, 0);
};

export function log(...args) { console.error(...args); }

// Run async work over items with a concurrency cap, preserving order.
export async function mapLimit(items, limit, fn) {
  const results = new Array(items.length);
  let next = 0;
  const workers = Array.from({ length: Math.min(limit, items.length) }, async () => {
    while (next < items.length) {
      const i = next++;
      results[i] = await fn(items[i], i);
    }
  });
  await Promise.all(workers);
  return results;
}
