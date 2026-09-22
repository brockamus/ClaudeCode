// Copies the self-hosted display font into the deployable site folder.
import { copyFileSync, mkdirSync } from 'node:fs';
mkdirSync('site/assets/fonts', { recursive: true });
copyFileSync(
  'node_modules/@fontsource-variable/bricolage-grotesque/files/bricolage-grotesque-latin-wght-normal.woff2',
  'site/assets/fonts/bricolage-grotesque-latin-wght.woff2'
);
console.log('fonts copied');
