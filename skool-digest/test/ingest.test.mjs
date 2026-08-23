#!/usr/bin/env node
// Ingest-layer regression tests. No network, no API keys:
//   node test/ingest.test.mjs
//
// Covers the two things most likely to break when Skool changes its payload:
// escaped URLs inside double-encoded JSON, and containers being mistaken for
// lessons.

import { parseCourse, mergeCourses, scrapeHTML, parseDOM, videoLinks, extractNextData } from "../lib/ingest.mjs";

let pass = 0, fail = 0;
const ok = (name, cond, detail = "") => {
  if (cond) { pass++; console.log(`  ok   ${name}`); }
  else { fail++; console.log(`  FAIL ${name} ${detail}`); }
};
const nextData = (payload) =>
  `<script id="__NEXT_DATA__" type="application/json">${JSON.stringify(payload)}</script>`;
const prose = (n) => "word ".repeat(n);

console.log("\nvideo link extraction");
for (const [name, url] of [
  ["youtube watch", "https://www.youtube.com/watch?v=dQw4w9WgXcQ"],
  ["youtu.be", "https://youtu.be/dQw4w9WgXcQ"],
  ["loom", "https://www.loom.com/share/abcdef0123456789abcdef0123456789"],
  ["vimeo", "https://player.vimeo.com/video/123456789"],
  ["wistia", "https://fast.wistia.net/embed/medias/abc123xyz9"],
  ["mp4", "https://cdn.example.com/a/b.mp4"],
  ["m3u8", "https://cdn.example.com/a/b.m3u8?t=1"],
]) ok(name, videoLinks(url).length === 1, JSON.stringify(videoLinks(url)));

// Skool nests video links in double-encoded JSON, so slashes arrive escaped.
const loom = "https://www.loom.com/share/abcdef0123456789abcdef0123456789";
ok("escaped \\/", videoLinks(loom.replace(/\//g, "\\/"))[0] === loom);
ok("escaped \\u002F", videoLinks(loom.replace(/\//g, "\\u002F"))[0] === loom);

console.log("\n__NEXT_DATA__ parsing");
const course = parseCourse(nextData({ props: { pageProps: {
  currentGroup: { name: "rank-expand-academy", metadata: { displayName: "Rank & Expand Academy" } },
  course: { id: "c1", name: "Rank & Expand", metadata: { title: "Rank & Expand Academy" }, children: [
    { id: "s1", name: "Section One", children: [
      { id: "m1", name: "Lesson A", metadata: { displayOrder: 1, description: prose(20), videoUrl: "https://youtu.be/aaaaaaaaaaa" } },
      // Video on an untitled array — this is the node's own data, not a child lesson.
      { id: "m2", name: "Lesson B", metadata: { displayOrder: 0, description: prose(20), videoLinks: [{ url: "https://youtu.be/bbbbbbbbbbb" }] } },
      { id: "m3", name: "Too Thin", metadata: { description: "short" } },
    ] },
  ] },
} } }));

ok("course title", course.title === "Rank & Expand Academy", course.title);
ok("source", course.source === "next-data");
ok("lessons only", course.modules.length === 2, `got ${course.modules.map((m) => m.title).join(", ")}`);
ok("drops container nodes", !course.modules.some((m) => /Rank & Expand|Section One/.test(m.title)));
ok("drops thin node", !course.modules.some((m) => m.title === "Too Thin"));
ok("sorted by displayOrder", course.modules[0].title === "Lesson B", course.modules[0].title);
ok("video on each lesson", course.modules.every((m) => m.videos.length === 1));
const slots = course.modules.flatMap((m) => m.videos);
ok("no duplicated videos", slots.length === new Set(slots).size);

console.log("\nDOM fallback");
const raw = `<html><head><title>T</title></head><body><h1>Module Four</h1><main><p>${prose(60)}</p>` +
  `<iframe src="https://www.youtube.com/embed/dQw4w9WgXcQ"></iframe></main></body></html>`;
let threw = false;
try { extractNextData(raw); } catch { threw = true; }
ok("no payload throws", threw);
const dom = parseDOM(scrapeHTML(raw), "https://www.skool.com/rank-expand-academy/classroom/abc");
ok("source", dom.source === "dom");
ok("h1 as title", dom.title === "Module Four", dom.title);
ok("one module", dom.modules.length === 1);
ok("iframe video", dom.modules[0]?.videos.length === 1, JSON.stringify(dom.modules[0]?.videos));
ok("allowFallback routes to DOM", parseCourse(raw, { allowFallback: true }).source === "dom");

console.log("\nmerge");
ok("dedupes repeated pages",
  mergeCourses([course, course]).modules.length === course.modules.length);

console.log(`\n${pass} passed, ${fail} failed\n`);
process.exit(fail ? 1 : 0);
