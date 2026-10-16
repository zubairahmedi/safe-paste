# Safe Paste

**Hide personal information before it goes into ChatGPT, then put it back in the answer.**

Free tool for nonprofit staff, caseworkers and anyone who handles client information.
Use it here: **https://tools.safeaifornonprofits.ca/safe-paste/**
Watch the 2 minute how-to: https://www.youtube.com/watch?v=acWYuqyHrb4

Built by [Zehaan Khan](https://www.linkedin.com/in/zehaankhan/) at [Safe AI for Nonprofits](https://safeaifornonprofits.ca).

## How it works

1. **Paste** a case note, email or letter.
2. Safe Paste finds names, phone numbers, emails, ID and health numbers, dates and addresses, and swaps them for placeholders like `[NAME_1]`, `[PHONE_1]` and `[HEALTH_CARD_1]`.
3. **Write your prompt** the way you normally would. Safe Paste adds your safe text plus a few rules at the end: keep every placeholder exactly as written, write `[MISSING: ...]` instead of inventing details, and put the answer between `===START===` and `===END===`.
4. **Paste the AI's answer back.** Safe Paste takes the part between the markers and puts the real details back in.

Optional: add your own name, email, job title, organization and phone. The AI signs with `[MY_NAME]` and so on, and step 4 fills in the real values. Your details never go to the AI either.

## Nothing leaves your browser

- The whole tool is **one HTML file**: no server code, no outside files, no fonts from the web, no analytics, no cookies.
- The page **blocks itself from sending anything**: its Content Security Policy sets `connect-src 'none'`, and the only script allowed to run is the page's own, pinned by its sha256 hash.
- **Check it yourself:**
  - Open the page, turn off your wifi, and use it. It works the same.
  - Open your browser's developer tools (F12), go to the Network tab, and use every button. Nothing is sent.
  - The page shows a live counter of requests it has made since you opened it, measured by your own browser. It stays at 0.
- The key that puts details back lives only in the open browser tab. Refresh and it's gone.
- The only things saved (in your own browser) are light or dark mode, and your sign off details if you tick "Remember".

Mozilla's Observatory rates the hosted version A+ (12 of 12 tests): [run the scan](https://developer.mozilla.org/en-US/observatory/analyze?host=tools.safeaifornonprofits.ca).

## Run it yourself

Download [`index.html`](index.html) and open it in any modern browser. That's it. No install, no build step.

## What it detects

| Type | Examples |
|---|---|
| Names | Two or more capitalized words, names after a title (Ms. Okafor), names after words like son, client or tenant, first or last names used alone after the full name appeared |
| Your own list | Any word or name you add to "Always hide", in any language (Arabic, Farsi, Tigrinya...) |
| Contact | Emails, North American and international phone numbers, UK mobiles |
| ID numbers | SIN (Canada, checksum), SSN (US), NHS number (UK), National Insurance number (UK), health card numbers, credit cards (checksum), client and file IDs |
| Dates | 1979-04-12, 12/04/1979, Oct 3, 2026, 3 October 2026 |
| Places | Street addresses with a unit, Canadian and UK postcodes, US ZIP codes |

## What it can't do

It catches common patterns, not everything. It can miss lowercase names, names that are also ordinary words at the start of a sentence (Grace, Hope), nicknames, and details that identify someone without a name, like "the only Tigrinya speaking mother of triplets at our Jane and Finch site". **Always read the safe version before you paste it.** Your organization's privacy rules still come first.

## Tests

```bash
npm install
npx playwright install chromium
npm test
```

The tests run the page in a real browser and check that every detail in the example gets hidden, that putting the details back gives exactly the original text, that UK, US and Arabic examples work, that a plain sentence has no false positives, and that the page makes **zero network requests**.

## Why we built it

Nonprofit staff use ChatGPT to save time, and case notes end up in it. We wrote about it here: [Is it safe to put client information into ChatGPT?](https://safeaifornonprofits.ca/blog/client-information-chatgpt/)

Safe Paste solves one step for free. If your team works with sensitive information every day, [Safe AI for Nonprofits](https://safeaifornonprofits.ca) builds private AI assistants that run on a server you control, so client details never go to an AI company in the first place.

## License

MIT. Use it, share it, change it.

Questions or a pattern it missed? Open an issue, or reach Zehaan on [LinkedIn](https://www.linkedin.com/in/zehaankhan/) or at zehaan@safeaifornonprofits.ca.
