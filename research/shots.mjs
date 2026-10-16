// Screenshots of the live tool on one hard note from the study (made up): default, then with the client's name added.
import path from 'node:path';
const { chromium } = await import('playwright').catch(() => import('../../safeai-stack/video/node_modules/playwright/index.mjs'));
const out = process.argv[2] || '.';
const note = `spoke w amina rahimi again today, her cell is 416.555.0142 now not the old one. lives at 210 birchmount road. tell amina to bring her id thurs.
Grace from the youth program dropped off the forms.
She is the only Tigrinya speaking mother of triplets at our Jane and Finch site.`;
const b = await chromium.launch({ channel: 'chrome' }).catch(() => chromium.launch());
const p = await b.newPage({ viewport: { width: 1000, height: 900 }, deviceScaleFactor: 1.5, colorScheme: 'light' });
await p.goto('https://tools.safeaifornonprofits.ca/safe-paste/');
await p.fill('#input', note); await p.waitForTimeout(400);
await p.locator('section[aria-labelledby="s2"]').screenshot({ path: path.join(out, 'study-default.png') });
await p.fill('#term', 'Amina Rahimi'); await p.click('#addterm'); await p.waitForTimeout(400);
await p.locator('section[aria-labelledby="s2"]').screenshot({ path: path.join(out, 'study-name-added.png') });
console.log(await p.inputValue('#output'));
await b.close();
