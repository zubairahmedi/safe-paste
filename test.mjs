// Checks Safe Paste in a real browser: detection, placeholders, restore, and zero network requests.
//   npm install && npm test              (tests the local index.html)
//   node test.mjs https://.../safe-paste/ (tests a live copy)
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const { chromium } = await import('playwright')
  .catch(() => import('../safeai-stack/video/node_modules/playwright/index.mjs'));
const url = process.argv[2] || pathToFileURL(path.resolve('index.html')).href;
const browser = await chromium.launch({ channel: 'chrome' }).catch(() => chromium.launch());
const page = await browser.newPage();
const requests = [];
page.on('request', r => { if (!r.url().startsWith('file:') && !r.url().startsWith('data:') && r.url() !== url) requests.push(r.url()); });
const errors = [];
page.on('pageerror', e => errors.push(e.message));
await page.goto(url);

let fails = 0;
const check = (ok, msg) => { console.log((ok ? 'PASS ' : 'FAIL ') + msg); if (!ok) fails++; };

// 1. the built in example
await page.click('#example');
await page.waitForTimeout(300);
const out = await page.inputValue('#output');
console.log('\n--- safe version ---\n' + out + '\n--------------------');
for (const secret of ['Amina', 'Rahimi', 'Yusuf', '1979-04-12', 'C-1042', '416-555-0143', 'amina.rahimi@example.com',
  '1234-567-890-AB', '45 Birchmount Road', 'M1N 3J5', 'Okafor', 'Patel'])
  check(!out.includes(secret), 'hides ' + secret);
check(out.includes('[NAME_1]') && out.includes('[NAME_1_FIRST]'), 'full name and first name share number 1');

// 2. restore
const answer = 'Dear Dr. [NAME_5],\nI am writing about [NAME_1] (born [DATE_1]). [NAME_1_FIRST] can be reached at [PHONE_1] or EMAIL_1. Unknown [NAME_99].';
await page.fill('#answer', answer);
await page.click('#restore');
const back = await page.inputValue('#restored');
console.log('\n--- restored ---\n' + back + '\n----------------');
check(back.includes('Amina Rahimi') && back.includes('1979-04-12') && back.includes('416-555-0143') && back.includes('amina.rahimi@example.com'), 'restores names, date, phone, unbracketed EMAIL_1');
check(back.includes('[NAME_99]'), 'leaves unknown placeholder alone');
console.log('info: ' + await page.textContent('#restoreinfo'));

const rt = await page.evaluate(() => { const t = document.getElementById('input').value; return t; });
await page.fill('#answer', out); await page.click('#restore');
check((await page.inputValue('#restored')) === rt, 'round trip: putting back the safe version gives the original text exactly');

// 3. UK + US + Arabic custom term
const r = await page.evaluate(() => {
  const t = 'Spoke to Mrs Siobhan O\'Neill, NHS number 943 476 5919, NI number AB 12 34 56 C, postcode SW1A 1AA, mobile 07700 900123. ' +
            'US file: SSN 123-45-6789, Austin TX 78701. Also called وليد المطيري about the referral. Card 4111 1111 1111 1111.';
  const m = window.SafePaste.detect(t, ['وليد المطيري']);
  return m.map(c => c.type + ':' + c.val);
});
console.log('\nUK/US/Arabic matches:', r);
for (const want of ["NAME:Siobhan O'Neill", 'NHS:943 476 5919', 'NI:AB 12 34 56 C', 'POSTCODE:SW1A 1AA', 'PHONE:07700 900123',
  'SSN:123-45-6789', 'POSTCODE:78701', 'NAME:وليد المطيري', 'CARD:4111 1111 1111 1111'])
  check(r.includes(want), 'finds ' + want);

// 3b. fixes found by the 200 case note study
const fx = await page.evaluate(() => [
  ['Best number is +44 7700 900123.', []], ['She lives at 1203-55 Harbour Square, Toronto', []],
  ['lives at 45 birchmount road. tell amina to come', ['amina rahimi']], ['Interpreter confirmed the spelling: أمينة رحيمي.', []],
  ['She has 2 kids and will drive them to court on the way home.', []],
].map(([t, c]) => window.SafePaste.detect(t, c).map(x => x.type + ':' + x.val)));
check(fx[0].includes('PHONE:+44 7700 900123'), 'UK international phone hidden whole: ' + fx[0]);
check(fx[1].includes('ADDRESS:1203-55 Harbour Square'), 'unit-dash address hidden whole: ' + fx[1]);
check(fx[2].includes('ADDRESS:45 birchmount road.') && fx[2].includes('NAME:amina'), 'lowercase address + lowercase first name from Always hide: ' + fx[2]);
check(fx[3].includes('NAME:أمينة رحيمي'), 'non-Latin name flagged: ' + fx[3]);
check(fx[4].length === 0, 'no false alarm on "drive / court / way": ' + fx[4]);

// 4. false positive sanity: ordinary sentence
const fp = await page.evaluate(() => window.SafePaste.detect('The board met on Monday to review the Q3 budget and the food bank program in Toronto.', []).map(c => c.type + ':' + c.val));
check(fp.length === 0, 'no false positives in a plain sentence (' + JSON.stringify(fp) + ')');

// 5. toggle off a highlight keeps it visible
await page.click('#example'); await page.waitForTimeout(200);
await page.click('mark:has-text("Okafor")'); await page.waitForTimeout(250);
check((await page.inputValue('#output')).includes('Okafor'), 'clicking a highlight keeps it visible');

// 6. UK flat address is one address, cities are not names, "Name 1" gets put back
await page.fill('#input', "Spoke with Mrs Siobhan O'Neill today. She lives at Flat 2, 14 Albert Road, Leeds LS6 2AB.");
await page.waitForTimeout(300);
const uk = await page.inputValue('#output');
check(uk === 'Spoke with Mrs [NAME_1] today. She lives at [ADDRESS_1], Leeds [POSTCODE_1].', 'flat address + city handled: ' + uk);
await page.fill('#answer', 'Dear Name 1, we will visit [Name 1] at ADDRESS_1.'); await page.click('#restore');
const nm = await page.inputValue('#restored');
check(nm === "Dear Siobhan O'Neill, we will visit Siobhan O'Neill at Flat 2, 14 Albert Road.", 'puts back Name 1 variants: ' + nm);

// 7. ready to paste prompt + an AI reply with chatter around the markers
await page.click('#example'); await page.waitForTimeout(250);
await page.fill('#task', 'Summarize this for my supervisor in a friendly tone'); await page.waitForTimeout(100);
const prompt = await page.inputValue('#prompt');
check(prompt.startsWith('Summarize this for my supervisor') && prompt.trim().endsWith('===START=== and ===END===.') && prompt.includes('[NAME_1]') && !prompt.includes('Amina'),
  'prompt = their own prompt + safe text + format rules at the end, no real names');
const reply = "Sure! Here's a draft:\n\n===START===\nDear Dr. [NAME_4],\n\nI'm referring [NAME_1] (born [DATE_1]) for housing support. [NAME_1_FIRST] can be reached at [PHONE_1]. Her health card expiry: [MISSING: health card expiry date].\n\nThank you,\n===END===\n\nLet me know if you want changes!";
await page.fill('#answer', reply); await page.click('#restore');
const letter = await page.inputValue('#restored');
check(letter.startsWith('Dear Dr. Patel,') && letter.includes('Amina Rahimi (born 1979-04-12)') && letter.includes('416-555-0143') && !letter.includes('Sure!') && !letter.includes('Let me know'), 'keeps only the marked answer and puts names back');
check((await page.textContent('#restoreinfo')).includes('[MISSING]'), 'tells the user about [MISSING] details');

// 8. sender details: placeholders in the prompt, filled back in step 4, remembered only when ticked
await page.fill('[data-me="MY_NAME"]', 'Zehaan Khan');
await page.fill('[data-me="MY_ORG"]', 'Harbourview Co-op');
await page.fill('[data-me="MY_EMAIL"]', 'zehaan@example.org');
const p2 = await page.inputValue('#prompt');
check(p2.includes('[MY_NAME] for my name') && p2.includes('[MY_ORG] for my organization') && !p2.includes('Zehaan Khan') && !p2.includes('[MY_PHONE]'),
  'prompt lists only filled sender placeholders, never the real values');
await page.fill('#answer', '===START===\nDear Dr. [NAME_4],\nRe: [NAME_1].\nBest,\n[MY_NAME]\n[MY_ORG] | [MY_EMAIL]\n===END===');
await page.click('#restore');
const signed = await page.inputValue('#restored');
check(signed.endsWith('Zehaan Khan\nHarbourview Co-op | zehaan@example.org') && signed.startsWith('Dear Dr. Patel,'), 'fills in sender details: ' + JSON.stringify(signed));
check(await page.evaluate(() => localStorage.getItem('sp-me')) === null, 'nothing saved unless Remember is ticked');
await page.check('#remember');
await page.reload(); await page.waitForTimeout(300);
check(await page.inputValue('[data-me="MY_ORG"]') === 'Harbourview Co-op', 'Remember keeps sender details after a reload');
await page.uncheck('#remember');
check(await page.evaluate(() => localStorage.getItem('sp-me')) === null, 'unticking Remember deletes them');

check(requests.length === 0, 'zero network requests (' + requests.join(', ') + ')');
check(errors.length === 0, 'no page errors ' + errors.join('; '));
await browser.close();
console.log(fails ? `\n${fails} FAILED` : '\nALL PASSED');
process.exit(fails ? 1 : 0);
