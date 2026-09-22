// Downloads the client's original photos from their current B12 site and
// produces responsive AVIF / WebP / JPEG variants for the redesign.
// Originals are cached in .cache/ (git-ignored); outputs go to site/assets/img.
import sharp from 'sharp';
import { existsSync, mkdirSync, writeFileSync } from 'node:fs';

const CDN = 'https://cdn.b12.io/client_media/uhtxIkaf/';
const SRC = {
  sink: '8191f017-5764-11f1-a3c1-0242ac110002-file_000000009ef8722fb81a7f2d5fe63f43.png',
  drawers: '4140b933-5764-11f1-9171-0242ac110002-file_000000007c80720cbc0e8d20dfd353b9.png',
  toilet: '9bb80401-5764-11f1-9537-0242ac110002-463d011531fcce21c059999c18d1ccc49e163c9e50609db611ba15b3890bc4ce.png',
  kitchenDark: 'eea91fcb-510c-11f1-afb5-0242ac110002-FB_IMG_1761601442088.jpg',
  bathroom: '29210490-510c-11f1-888f-0242ac110002-Screenshot_20260508_172722_Google.jpg',
  apartment: '5f2e49f9-510c-11f1-a6a1-0242ac110002-FB_IMG_1761601439123.jpg',
  cabinet: '0231886a-510c-11f1-a1aa-0242ac110002-InCollage_20260508_175105007.jpg',
  livingRoom: 'd60b1602-7f6d-11f1-9922-0242ac110002-InCollage_20260704_061933832.jpg',
  garage: 'd62dc3df-7f6d-11f1-aaf1-0242ac110002-InCollage_20260704_060552892.jpg',
  kitchen: 'd692926b-7f6d-11f1-a1be-0242ac110002-InCollage_20260704_061151354.jpg',
  shop: 'd7f28e17-7f6d-11f1-843e-0242ac110002-InCollage_20260704_060102032.jpg',
};

const OUT = 'site/assets/img';
mkdirSync('.cache', { recursive: true });
mkdirSync(OUT, { recursive: true });

async function src(key) {
  const path = `.cache/${key}`;
  if (!existsSync(path)) {
    const res = await fetch(CDN + SRC[key]);
    if (!res.ok) throw new Error(`download failed ${key}: ${res.status}`);
    writeFileSync(path, Buffer.from(await res.arrayBuffer()));
  }
  return path;
}

const manifest = {};
async function emit(name, pipeline, widths) {
  const buf = await pipeline.clone().toBuffer();
  const base = sharp(buf);
  const { width, height } = await base.metadata();
  manifest[name] = { width, height, widths: [] };
  const sizes = widths.filter((w) => w <= width);
  if (widths.some((w) => w > width) && !sizes.includes(width)) sizes.push(width);
  for (const w of sizes) {
    const r = base.clone().resize({ width: w });
    await r.clone().avif({ quality: 50, effort: 6 }).toFile(`${OUT}/${name}-${w}.avif`);
    await r.clone().webp({ quality: 72 }).toFile(`${OUT}/${name}-${w}.webp`);
    await r.clone().jpeg({ quality: 74, mozjpeg: true }).toFile(`${OUT}/${name}-${w}.jpg`);
    manifest[name].widths.push(w);
  }
}

// Before / after pairs cropped from the side-by-side collages.
// Crops skip the baked-in "BEFORE/AFTER" labels; the slider adds its own.
const pairs = {
  sink: { before: { left: 0, top: 120, width: 1448, height: 410 }, after: { left: 0, top: 676, width: 1448, height: 410 } },
  drawers: { before: { left: 0, top: 120, width: 1448, height: 410 }, after: { left: 0, top: 676, width: 1448, height: 410 } },
  toilet: { before: { left: 0, top: 160, width: 718, height: 926 }, after: { left: 730, top: 160, width: 718, height: 926 } },
};
for (const [key, c] of Object.entries(pairs)) {
  const file = await src(key);
  await emit(`${key}-before`, sharp(file).extract(c.before), [480, 800, 1200]);
  await emit(`${key}-after`, sharp(file).extract(c.after), [480, 800, 1200]);
}

// Gallery collages, kept whole.
for (const key of ['kitchenDark', 'livingRoom', 'apartment', 'bathroom', 'garage', 'kitchen', 'cabinet', 'shop']) {
  await emit(key, sharp(await src(key)).rotate(), [400, 800, 1200]);
}

// Open Graph share image: 1200x630 built from the sink pair.
{
  const b = await sharp(await src('sink')).extract(pairs.sink.before).resize(600, 630, { fit: 'cover' }).toBuffer();
  const a = await sharp(await src('sink')).extract(pairs.sink.after).resize(600, 630, { fit: 'cover' }).toBuffer();
  const label = (t, x, fill) => Buffer.from(
    `<svg width="1200" height="630"><rect x="${x}" y="30" rx="10" width="170" height="54" fill="${fill}"/>` +
    `<text x="${x + 85}" y="67" font-family="Arial, sans-serif" font-weight="700" font-size="26" fill="#fff" text-anchor="middle">${t}</text></svg>`);
  await sharp({ create: { width: 1200, height: 630, channels: 3, background: '#16213a' } })
    .composite([
      { input: b, left: 0, top: 0 }, { input: a, left: 600, top: 0 },
      { input: Buffer.from('<svg width="1200" height="630"><rect x="596" width="8" height="630" fill="#fff"/></svg>'), left: 0, top: 0 },
      { input: label('BEFORE', 30, '#16213a'), left: 0, top: 0 },
      { input: label('AFTER', 1000, '#7b1e3a'), left: 0, top: 0 },
    ])
    .jpeg({ quality: 80, mozjpeg: true })
    .toFile(`${OUT}/og.jpg`);
}

writeFileSync('.cache/manifest.json', JSON.stringify(manifest, null, 2));
console.log(JSON.stringify(manifest));

// Apple touch icon from the SVG favicon.
await sharp('site/favicon.svg', { density: 400 }).resize(180, 180).png().toFile(`${OUT}/apple-touch-icon.png`);
