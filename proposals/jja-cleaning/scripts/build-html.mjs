// Expands {{pic ...}} placeholders in src/index.html into responsive
// <picture> elements (AVIF, WebP, JPEG) using the image manifest,
// then writes the deployable site/index.html.
//
// Placeholder syntax (attributes are key="value"):
//   {{pic name="sink-before" alt="..." sizes="100vw" loading="lazy" class="x"}}
import { readFileSync, writeFileSync } from 'node:fs';

const manifest = JSON.parse(readFileSync('.cache/manifest.json', 'utf8'));
const tpl = readFileSync('src/index.html', 'utf8');

const attrs = (s) => Object.fromEntries([...s.matchAll(/(\w+)="([^"]*)"/g)].map((m) => [m[1], m[2]]));

const out = tpl.replace(/\{\{pic ([^}]+)\}\}/g, (_, raw) => {
  const a = attrs(raw);
  const m = manifest[a.name];
  if (!m) throw new Error(`unknown image ${a.name}`);
  const set = (ext) => m.widths.map((w) => `assets/img/${a.name}-${w}.${ext} ${w}w`).join(', ');
  const fallbackW = m.widths.includes(800) ? 800 : m.widths[m.widths.length - 1];
  const h = Math.round((m.height / m.width) * fallbackW);
  const sizes = a.sizes || '100vw';
  const loading = a.loading || 'lazy';
  const extra = [
    a.class ? ` class="${a.class}"` : '',
    loading === 'eager' ? ' fetchpriority="high"' : '',
  ].join('');
  return [
    '<picture>',
    `<source type="image/avif" srcset="${set('avif')}" sizes="${sizes}">`,
    `<source type="image/webp" srcset="${set('webp')}" sizes="${sizes}">`,
    `<img src="assets/img/${a.name}-${fallbackW}.jpg" srcset="${set('jpg')}" sizes="${sizes}" width="${fallbackW}" height="${h}" alt="${a.alt ?? ''}" loading="${loading}" decoding="async"${extra}>`,
    '</picture>',
  ].join('');
});

const final = out.replace(/\{\{full name="([^"]+)"\}\}/g, (_, name) => {
  const m = manifest[name];
  if (!m) throw new Error(`unknown image ${name}`);
  return `assets/img/${name}-${m.widths[m.widths.length - 1]}.webp`;
});

writeFileSync('site/index.html', final);
console.log('site/index.html written');
