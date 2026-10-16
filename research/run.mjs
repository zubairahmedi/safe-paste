// Runs every test note through Safe Paste's real detection code in a browser and saves what it hid.
//   node research/run.mjs            -> research/detections.json
// Scenario A: default settings. Scenario B: the client's name added to "Always hide" (what we tell staff to do).
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const { chromium } = await import('playwright')
  .catch(() => import('../../safeai-stack/video/node_modules/playwright/index.mjs'));
const here = path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Z]:)/, '$1'));
const notes = fs.readFileSync(path.join(here, 'notes.jsonl'), 'utf8').trim().split('\n').map(JSON.parse);

const browser = await chromium.launch({ channel: 'chrome' }).catch(() => chromium.launch());
const page = await browser.newPage();
await page.goto(pathToFileURL(path.join(here, '..', 'index.html')).href);

const out = await page.evaluate((notes) => notes.map(n => {
  const client = n.entities.find(e => ['Full names', 'Lowercase names', 'ALL CAPS names'].includes(e.group));
  const run = custom => window.SafePaste.detect(n.text, custom).map(c => [c.s, c.e, c.type, c.sure]);
  return { id: n.id, A: run([]), B: run(client ? [client.value] : []) };
}), notes);

fs.writeFileSync(path.join(here, process.argv[2] ? 'detections_' + process.argv[2] + '.json' : 'detections.json'), JSON.stringify(out));
console.log('ran', out.length, 'notes');
await browser.close();
