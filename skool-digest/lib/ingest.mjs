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
export function parseCourse(html, { title, url = "file://saved-page", allowFallback = false } = {}) {
  let data;
  try {
    data = extractNextData(html);
  } catch (e) {
    // No Next.js payload (Circle, Kajabi, Teachable, …) — read the markup itself.
    if (!allowFallback) throw e;
    return parseDOM(scrapeHTML(html), url);
  }
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
    source: [...new Set(courses.map((c) => c.source))].join("+") || "unknown",
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

    // Anything behind a paywall bounces to a login/sign-in screen first.
    if (!headless && !(await looksLoggedIn(page, url))) {
      log("\nBrowser is open. Log in, navigate to the course, then press Enter here.");
      await waitForEnter();
      await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 });
    }
    await page.waitForTimeout(waitMs);
    await autoScroll(page);

    const targets = await discoverLessons(page, url, maxPages);
    const pages = [url, ...targets.filter((t) => t !== url)];
    log(`Found ${pages.length} page(s) under ${new URL(url).pathname}.`);

    const courses = [];
    for (const [i, target] of pages.entries()) {
      try {
        if (target !== url) {
          await page.goto(target, { waitUntil: "domcontentloaded", timeout: 60000 });
          await page.waitForTimeout(waitMs);
          await autoScroll(page);
        }
        const course = await extractPage(page);
        courses.push(course);
        log(`  [${i + 1}/${pages.length}] ${course.modules.length} module(s) via ${course.source} — ${target}`);
      } catch (e) {
        log(`  [${i + 1}/${pages.length}] failed: ${target} — ${e.message}`);
      }
    }
    const merged = mergeCourses(courses);
    if (!merged.modules.length) {
      throw new Error(
        "No modules found. Either the crawl never got past the login screen, or this platform " +
        "hides lessons behind interactions the crawler didn't perform. Re-run without --headless and watch it.",
      );
    }
    return merged;
  } finally {
    await context.close();
  }
}

/**
 * Extract one page: prefer the Next.js payload (richest), fall back to the
 * rendered DOM. The DOM path is what makes this work on Circle, Kajabi,
 * Teachable and anything else that hydrates client-side.
 */
async function extractPage(page) {
  try {
    const course = parseCourse(await page.content());
    if (course.modules.length) return course;
  } catch { /* no __NEXT_DATA__ — fall through to the DOM */ }
  return parseDOM(await scrapeDOM(page), page.url());
}

/** Pull title, prose and video embeds straight out of the rendered page. */
function scrapeDOM(page) {
  return page.evaluate(() => {
    const text = (el) => (el?.innerText ?? "").trim();
    const main =
      document.querySelector("main") ??
      document.querySelector("[role=main]") ??
      document.querySelector("article") ??
      document.body;

    const embeds = [...document.querySelectorAll("iframe[src], video[src], video source[src]")]
      .map((el) => el.getAttribute("src"))
      .filter(Boolean);

    // Players often keep the real URL on a data-* attribute instead of src.
    const dataAttrs = [...document.querySelectorAll("[data-video-url], [data-src], [data-video-id], [data-wistia-id]")]
      .flatMap((el) => ["data-video-url", "data-src", "data-video-id", "data-wistia-id"].map((a) => el.getAttribute(a)))
      .filter(Boolean);

    return {
      title: text(document.querySelector("h1")) || document.title || "",
      body: text(main).slice(0, 20000),
      embeds: [...embeds, ...dataAttrs],
      html: main.innerHTML.slice(0, 400000),
    };
  });
}

/** Same shape as scrapeDOM(), derived from raw markup with no browser. */
export function scrapeHTML(html) {
  const body = html
    .replace(/<(script|style|noscript|svg)[\s\S]*?<\/\1>/gi, " ")
    .replace(/<br\s*\/?>|<\/(p|div|li|h[1-6]|tr)>/gi, "\n")
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/g, " ").replace(/&amp;/g, "&").replace(/&#39;|&apos;/g, "'")
    .replace(/&quot;/g, '"').replace(/&lt;/g, "<").replace(/&gt;/g, ">")
    .replace(/[ \t]+/g, " ")
    .replace(/\n\s*\n\s*\n+/g, "\n\n")
    .trim();

  const h1 = html.match(/<h1[^>]*>([\s\S]*?)<\/h1>/i)?.[1];
  const title = (h1 ?? html.match(/<title[^>]*>([\s\S]*?)<\/title>/i)?.[1] ?? "")
    .replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();

  const embeds = [...html.matchAll(/<(?:iframe|video|source)[^>]+src=["']([^"']+)["']/gi)].map((m) => m[1]);

  return { title, body: body.slice(0, 20000), embeds, html };
}

export function parseDOM(scraped, pageUrl) {
  const videos = [...new Set([
    ...videoLinks(scraped.embeds.join(" ")),
    ...videoLinks(scraped.html),
    // Bare Wistia/Vimeo IDs sometimes appear only as data attributes.
    ...scraped.embeds
      .filter((s) => /^[a-z0-9]{8,}$/i.test(s))
      .map((id) => `https://fast.wistia.net/embed/medias/${id}`),
  ])];

  const title = (scraped.title || new URL(pageUrl).pathname.split("/").filter(Boolean).pop() || "Untitled").trim();
  const body = scraped.body.replace(/\n{3,}/g, "\n\n").trim();

  return {
    title,
    slug: slug(title),
    source: "dom",
    captured_at: new Date().toISOString(),
    modules: (videos.length || body.length > 200)
      ? [{ id: pageUrl, title, body, videos, order: 0, url: pageUrl }]
      : [],
  };
}

/** Same-origin links sharing the course's path prefix — platform-agnostic. */
function discoverLessons(page, url, maxPages) {
  const { origin, pathname } = new URL(url);
  // /c/1-page-funnel/... -> /c/1-page-funnel ; /<group>/classroom/... -> /<group>/classroom
  const base = "/" + pathname.split("/").filter(Boolean).slice(0, 2).join("/");

  return page.$$eval("a[href]", (as) => as.map((a) => a.getAttribute("href")))
    .then((hrefs) => [...new Set(
      hrefs
        .filter(Boolean)
        .map((h) => { try { return new URL(h, origin).href.split("#")[0]; } catch { return null; } })
        .filter((h) => h && h.startsWith(origin) && new URL(h).pathname.startsWith(base)),
    )].slice(0, maxPages));
}

/** Lazy-loaded lesson lists only render once you scroll them into view. */
async function autoScroll(page, steps = 12) {
  for (let i = 0; i < steps; i++) {
    const atBottom = await page.evaluate(() => {
      const before = window.scrollY;
      window.scrollBy(0, window.innerHeight);
      return window.scrollY === before;
    });
    if (atBottom) break;
    await page.waitForTimeout(350);
  }
  await page.evaluate(() => window.scrollTo(0, 0));
}

async function looksLoggedIn(page, url) {
  if (/\b(login|signin|sign-in|sign_in|auth)\b/i.test(page.url())) return false;
  // Landed somewhere else entirely (redirected home) — treat as not signed in.
  if (new URL(page.url()).pathname === "/" && new URL(url).pathname !== "/") return false;
  return true;
}

function waitForEnter() {
  return new Promise((resolve) => {
    process.stdin.resume();
    process.stdin.once("data", () => { process.stdin.pause(); resolve(); });
  });
}
