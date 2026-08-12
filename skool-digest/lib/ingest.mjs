// Ingest: turn Skool classroom pages into a course.json.
//
// Skool is a Next.js app, so every classroom page ships a __NEXT_DATA__ JSON
// blob containing the module tree, titles, bodies and video links. We parse
// that instead of scraping rendered HTML — it survives cosmetic redesigns.
//
// Two paths in:
//   parseCourse(html)  — one saved page (or a raw __NEXT_DATA__ dump)
//   crawl(url, opts)   — Playwright, using your own logged-in browser profile

import { log, slug } from "./util.mjs";

const VIDEO_PATTERNS = [
  /https?:\/\/(?:www\.)?youtube\.com\/watch\?[^"'\s\\]*v=[\w-]{11}[^"'\s\\]*/gi,
  /https?:\/\/(?:www\.)?youtube\.com\/embed\/[\w-]{11}[^"'\s\\]*/gi,
  /https?:\/\/youtu\.be\/[\w-]{11}[^"'\s\\]*/gi,
  /https?:\/\/(?:www\.)?loom\.com\/(?:share|embed)\/[a-f0-9]{16,}/gi,
  /https?:\/\/(?:player\.)?vimeo\.com\/(?:video\/)?\d+/gi,
  /https?:\/\/(?:fast\.)?wistia\.(?:net|com)\/(?:embed\/)?(?:medias|iframe)\/\w+/gi,
  /https?:\/\/[^"'\s\\]+\.(?:mp4|m3u8)(?:\?[^"'\s\\]*)?/gi,
];

/** Pull the __NEXT_DATA__ payload out of a saved Skool page. */
export function extractNextData(html) {
  const m = html.match(
    /<script[^>]+id=["']__NEXT_DATA__["'][^>]*>([\s\S]*?)<\/script>/i,
  );
  if (m) return JSON.parse(m[1]);
  // Maybe we were handed the JSON directly.
  const trimmed = html.trim();
  if (trimmed.startsWith("{")) return JSON.parse(trimmed);
  throw new Error("No __NEXT_DATA__ found. Save the page with View Source (not DevTools' rendered DOM).");
}

/** Every video URL mentioned anywhere inside a node. */
export function videoLinks(node) {
  const text = typeof node === "string" ? node : JSON.stringify(node ?? "");
  const found = new Set();
  for (const re of VIDEO_PATTERNS) {
    for (const hit of text.match(re) ?? []) found.add(hit.replace(/\\u002F/gi, "/").replace(/\\\//g, "/"));
  }
  return [...found];
}

// Walk the whole payload and collect anything that looks like a lesson: an
// object with a human title that carries at least one video link or a body.
function collectModules(root) {
  const out = [];
  const seen = new Set();

  const visit = (node, depth) => {
    if (!node || typeof node !== "object" || depth > 14) return;
    if (Array.isArray(node)) { node.forEach((n) => visit(n, depth + 1)); return; }

    const meta = node.metadata && typeof node.metadata === "object" ? node.metadata : {};
    const title = firstString(node.title, node.name, meta.title, meta.name);
    const body = firstString(meta.description, meta.content, node.description, node.content);
    const videos = videoLinks(node);

    if (title && (videos.length || (body && body.length > 40))) {
      const id = String(node.id ?? node.uid ?? `${slug(title)}-${out.length}`);
      const key = `${id}::${title}`;
      if (!seen.has(key)) {
        seen.add(key);
        out.push({
          id,
          title: title.trim(),
          body: (body ?? "").trim(),
          videos,
          order: numberOr(meta.displayOrder ?? node.displayOrder ?? node.order, out.length),
        });
      }
    }

    for (const value of Object.values(node)) visit(value, depth + 1);
  };

  visit(root, 0);
  return out;
}

const firstString = (...vals) =>
  vals.find((v) => typeof v === "string" && v.trim().length > 0);

const numberOr = (v, fallback) => (typeof v === "number" && Number.isFinite(v) ? v : fallback);

/** html (or a __NEXT_DATA__ dump) -> course object */
export function parseCourse(html, { title } = {}) {
  const data = extractNextData(html);
  const modules = collectModules(data).sort((a, b) => a.order - b.order);
  const courseTitle =
    title ??
    firstString(
      data?.props?.pageProps?.course?.metadata?.title,
      data?.props?.pageProps?.course?.name,
      data?.props?.pageProps?.currentGroup?.metadata?.displayName,
      data?.props?.pageProps?.currentGroup?.name,
    ) ??
    "Untitled course";

  return {
    title: courseTitle,
    slug: slug(courseTitle),
    source: "next-data",
    captured_at: new Date().toISOString(),
    modules,
  };
}

/** Merge several parsed pages into one course, de-duplicating modules. */
export function mergeCourses(courses, { title } = {}) {
  const modules = [];
  const seen = new Set();
  for (const course of courses) {
    for (const m of course.modules) {
      const key = `${m.title}::${m.videos[0] ?? ""}`;
      if (seen.has(key)) continue;
      seen.add(key);
      modules.push({ ...m, order: modules.length });
    }
  }
  const courseTitle = title ?? courses.find((c) => c.title !== "Untitled course")?.title ?? "Untitled course";
  return {
    title: courseTitle,
    slug: slug(courseTitle),
    source: "next-data",
    captured_at: new Date().toISOString(),
    modules,
  };
}

/**
 * Crawl a Skool classroom with your own logged-in browser profile.
 *
 * Playwright is loaded lazily so the rest of the tool works without it.
 * First run opens a real browser: log into Skool by hand, then press Enter.
 * The session cookie persists in `profileDir` for every run after that.
 */
export async function crawl(url, { profileDir, maxPages = 200, headless = false, waitMs = 1200 } = {}) {
  let chromium;
  try {
    ({ chromium } = await import("playwright"));
  } catch {
    throw new Error("Playwright not installed. Run: npm i -g playwright && playwright install chromium");
  }

  const context = await chromium.launchPersistentContext(profileDir, {
    headless,
    viewport: { width: 1400, height: 950 },
  });
  const page = context.pages()[0] ?? (await context.newPage());

  try {
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 });

    if (!headless && /\/login/i.test(page.url())) {
      log("\nBrowser is open. Log into Skool, navigate to the classroom, then press Enter here.");
      await waitForEnter();
      await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 });
    }
    await page.waitForTimeout(waitMs);

    const origin = new URL(url).origin;
    const base = new URL(url).pathname.split("/").slice(0, 3).join("/"); // /<group>/classroom -> /<group>

    const links = await page.$$eval("a[href]", (as) => as.map((a) => a.getAttribute("href")));
    const targets = [...new Set(
      links
        .filter(Boolean)
        .map((h) => (h.startsWith("http") ? h : `${origin}${h}`))
        .filter((h) => h.startsWith(origin) && h.includes("/classroom"))
        .filter((h) => new URL(h).pathname.startsWith(base)),
    )].slice(0, maxPages);

    const pages = [url, ...targets.filter((t) => t !== url)];
    log(`Found ${pages.length} classroom page(s).`);

    const courses = [];
    for (const [i, target] of pages.entries()) {
      try {
        if (target !== url) {
          await page.goto(target, { waitUntil: "domcontentloaded", timeout: 60000 });
          await page.waitForTimeout(waitMs);
        }
        const html = await page.content();
        courses.push(parseCourse(html));
        log(`  [${i + 1}/${pages.length}] ${target}`);
      } catch (e) {
        log(`  [${i + 1}/${pages.length}] failed: ${target} — ${e.message}`);
      }
    }
    return mergeCourses(courses);
  } finally {
    await context.close();
  }
}

function waitForEnter() {
  return new Promise((resolve) => {
    process.stdin.resume();
    process.stdin.once("data", () => { process.stdin.pause(); resolve(); });
  });
}
