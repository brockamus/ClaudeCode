#!/usr/bin/env node
// Skool Digest — turn a Skool course into an action plan you can execute.
//
//   skool-digest ingest <page.html...>        saved classroom pages -> course.json
//   skool-digest crawl  <classroom-url>       Playwright + your logged-in profile
//   skool-digest run    <course.json>         transcribe -> distill -> playbook
//   skool-digest apply  <playbook.json>       playbook -> per-business action plan
//
// See README.md for setup.

import { existsSync, readFileSync, readdirSync } from "node:fs";
import { join, basename } from "node:path";

import { ROOT, OUT, loadEnv, requireKey, readJSON, writeJSON, writeText, log, slug, mapLimit } from "./lib/util.mjs";
import { parseCourse, mergeCourses, crawl } from "./lib/ingest.mjs";
import { transcribe, haveBinary } from "./lib/transcribe.mjs";
import { distill, rollup, apply } from "./lib/analyze.mjs";
import { renderPlaybook, renderNumbers, renderAssets, renderCoverage, renderApplied } from "./lib/render.mjs";

const USAGE = `Usage:
  skool-digest ingest <page.html...> [--title "Course name"]
  skool-digest crawl  <classroom-url> [--headless] [--max-pages N]
  skool-digest run    <course.json> [--brand <name>] [--limit N] [--no-paid] [--concurrency N]
  skool-digest apply  <playbook.json> --brand <name>

Flags:
  --brand <name>    business to adapt the playbook for (see --list-brands)
  --limit N         only process the first N modules (useful for a trial run)
  --no-paid         captions only; never pay for speech-to-text
  --concurrency N   parallel module analyses (default 3)
  --list-brands     show available business context files`;

// ---------- args ----------
const argv = process.argv.slice(2);
// A leading flag (e.g. `--list-brands`) is not a command — leave it for the parser.
const cmd = argv[0]?.startsWith("--") ? null : argv.shift();
const flags = {};
const positional = [];
for (let i = 0; i < argv.length; i++) {
  const a = argv[i];
  if (a === "--headless" || a === "--no-paid" || a === "--list-brands") flags[a.slice(2)] = true;
  else if (a.startsWith("--")) flags[a.slice(2)] = argv[++i];
  else positional.push(a);
}

const env = loadEnv();

if (flags["list-brands"]) { listBrands(); process.exit(0); }

try {
  switch (cmd) {
    case "ingest": await cmdIngest(); break;
    case "crawl": await cmdCrawl(); break;
    case "run": await cmdRun(); break;
    case "apply": await cmdApply(); break;
    default:
      console.error(USAGE);
      process.exit(cmd ? 1 : 0);
  }
} catch (e) {
  console.error(`\nError: ${e.message}`);
  process.exit(1);
}

// ---------- commands ----------

async function cmdIngest() {
  if (!positional.length) throw new Error("Give me one or more saved .html pages.\n\n" + USAGE);
  const courses = positional.map((path) => {
    // allowFallback: saved pages from Circle/Kajabi/Teachable have no __NEXT_DATA__,
    // so fall back to reading the markup itself.
    const course = parseCourse(readFileSync(path, "utf8"), {
      title: flags.title,
      url: `file://${path}`,
      allowFallback: true,
    });
    log(`${basename(path)}: ${course.modules.length} module(s) via ${course.source}`);
    return course;
  });
  const course = courses.length === 1 ? courses[0] : mergeCourses(courses, { title: flags.title });
  finishIngest(course);
}

async function cmdCrawl() {
  const url = positional[0];
  if (!url) throw new Error("Give me a Skool classroom URL.\n\n" + USAGE);
  const course = await crawl(url, {
    profileDir: join(ROOT, ".browser-profile"),
    headless: Boolean(flags.headless),
    maxPages: Number(flags["max-pages"] ?? 200),
  });
  finishIngest(course);
}

function finishIngest(course) {
  const withVideo = course.modules.filter((m) => m.videos.length).length;
  const path = writeJSON(join(OUT, course.slug, "course.json"), course);
  log(`\n${course.title}`);
  log(`  ${course.modules.length} modules, ${withVideo} with video`);
  log(`  -> ${path}`);
  log(`\nNext: skool-digest run ${path}`);
}

async function cmdRun() {
  const coursePath = positional[0];
  if (!coursePath) throw new Error("Give me a course.json (from `ingest` or `crawl`).\n\n" + USAGE);

  const apiKey = requireKey(env, "ANTHROPIC_API_KEY", "analysis");
  const openaiKey = env.OPENAI_API_KEY;
  const allowPaid = !flags["no-paid"];
  const concurrency = Number(flags.concurrency ?? 3);

  const course = readJSON(coursePath);
  let modules = course.modules;
  if (flags.limit) modules = modules.slice(0, Number(flags.limit));

  if (!haveBinary("yt-dlp")) {
    log("Warning: yt-dlp not found — no captions or audio can be fetched.");
    log("         Install it (brew install yt-dlp) or run against modules with text bodies only.\n");
  }
  if (allowPaid && !openaiKey) {
    log("Note: OPENAI_API_KEY not set — videos without captions will be skipped.\n");
  }

  log(`${course.title}: analysing ${modules.length} module(s)\n`);

  // Stage 1+2 per module: transcribe, then extract. Runs concurrently.
  const distilled = (await mapLimit(modules, concurrency, async (module, i) => {
    // Workers run concurrently, so every line has to name its own module.
    const label = `[${String(i + 1).padStart(String(modules.length).length)}/${modules.length}] ${module.title}`;
    try {
      const transcript = module.videos.length
        ? await transcribe(module.videos[0], { openaiKey, allowPaid })
        : { url: null, source: "none", segments: [], text: "" };

      if (!transcript.text && !module.body) {
        log(`${label} — nothing to analyse, skipped`);
        return null;
      }
      const result = await distill({ apiKey, module, transcript });
      const src = { captions: "captions", speech: "speech-to-text", none: "text only" }[transcript.source];
      log(`${label} — ${result.plays.length} plays, ${result.numbers.length} numbers, ${result.assets.length} assets (${src})`);
      return { module, transcript, result };
    } catch (e) {
      log(`${label} — failed: ${e.message}`);
      return null;
    }
  })).filter(Boolean);

  if (!distilled.length) throw new Error("Nothing could be analysed. Check yt-dlp is installed and the course has videos or text bodies.");

  const dir = join(OUT, course.slug);
  writeJSON(join(dir, "distilled.json"), distilled);

  // Stage 3: consolidate across the whole course.
  log(`\nConsolidating ${distilled.length} modules into one playbook…`);
  const playbook = await rollup({ apiKey, course, distilled });
  writeJSON(join(dir, "playbook.json"), playbook);

  writeText(join(dir, "playbook.md"), renderPlaybook(course, playbook, distilled));
  writeText(join(dir, "numbers.md"), renderNumbers(course, distilled));
  writeText(join(dir, "templates.md"), renderAssets(course, distilled));
  writeText(join(dir, "coverage.md"), renderCoverage(course, distilled));

  log(`\n${playbook.playbook.length} actions · ${playbook.contradictions.length} contradictions · ${playbook.ignore.length} ignorable claims`);
  log(`  -> ${join(dir, "playbook.md")}`);
  log(`  -> ${join(dir, "numbers.md")}`);
  log(`  -> ${join(dir, "templates.md")}`);
  log(`  -> ${join(dir, "coverage.md")}`);

  if (flags.brand) await runApply({ apiKey, course, playbook, brandName: flags.brand, dir });
  else log(`\nNext: skool-digest apply ${join(dir, "playbook.json")} --brand <name>`);
}

async function cmdApply() {
  const playbookPath = positional[0];
  if (!playbookPath) throw new Error("Give me a playbook.json.\n\n" + USAGE);
  if (!flags.brand) throw new Error("--brand is required. See --list-brands.");

  const apiKey = requireKey(env, "ANTHROPIC_API_KEY", "analysis");
  const playbook = readJSON(playbookPath);
  const dir = playbookPath.replace(/\/[^/]+$/, "");
  const course = existsSync(join(dir, "course.json"))
    ? readJSON(join(dir, "course.json"))
    : { title: "course" };

  await runApply({ apiKey, course, playbook, brandName: flags.brand, dir });
}

async function runApply({ apiKey, course, playbook, brandName, dir }) {
  const brandContext = loadBrand(brandName);
  log(`\nAdapting ${playbook.playbook.length} actions for ${brandName}…`);
  const plan = await apply({ apiKey, playbook, brandName, brandContext });

  writeJSON(join(dir, `plan-${slug(brandName)}.json`), plan);
  const md = writeText(join(dir, `plan-${slug(brandName)}.md`), renderApplied(course, plan));
  log(`  ${plan.ranked.length} actions kept, ${plan.skipped.length} skipped`);
  log(`  -> ${md}`);
}

// ---------- brand context ----------

function brandDirs() {
  return [join(ROOT, "brands"), join(ROOT, "..", "copyroom", "brands")].filter(existsSync);
}

function loadBrand(name) {
  for (const dir of brandDirs()) {
    const path = join(dir, `${name}.md`);
    if (existsSync(path)) return readFileSync(path, "utf8");
  }
  throw new Error(`No context file for "${name}". Available: ${availableBrands().join(", ") || "(none)"}`);
}

function availableBrands() {
  const names = new Set();
  for (const dir of brandDirs()) {
    for (const f of readdirSync(dir)) if (f.endsWith(".md")) names.add(f.replace(/\.md$/, ""));
  }
  return [...names].sort();
}

function listBrands() {
  const names = availableBrands();
  if (!names.length) {
    console.log(`No brand files found. Add markdown files describing each business to ${join(ROOT, "brands")}/`);
    return;
  }
  console.log("Available businesses:");
  for (const n of names) console.log(`  ${n}`);
}
