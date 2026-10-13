// Browser driver for the FLYNC frontend (React/Vite SPA at :8443), backed
// by the FastAPI backend (:8000). Uses the system-installed Edge browser
// via playwright-core's `channel: 'msedge'` -- this machine has no network
// budget to let Playwright download its own Chromium, and no chromium-cli
// binary is installed, so this script IS the driver.
//
// Usage: node driver.mjs <script.txt>
// Each line of the script file is one command (same vocabulary as
// chromium-cli): nav, wait-for, click, fill, press, screenshot, eval,
// console, text. Blank lines and lines starting with # are ignored.
//
// Screenshots land in .claude/skills/run-ai-powered-state-machine/screenshots/.

import { chromium } from 'playwright-core';
import * as fs from 'node:fs';
import * as path from 'node:path';

const SKILL_DIR = path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1'));
const SHOT_DIR = process.env.SCREENSHOT_DIR || path.join(SKILL_DIR, 'screenshots');
fs.mkdirSync(SHOT_DIR, { recursive: true });

const scriptPath = process.argv[2];
if (!scriptPath) {
  console.error('usage: node driver.mjs <script.txt>');
  process.exit(1);
}
const lines = fs.readFileSync(scriptPath, 'utf-8')
  .split('\n')
  .map(l => l.trim())
  .filter(l => l && !l.startsWith('#'));

const consoleErrors = [];

function splitArgs(rest) {
  // very small arg splitter: "sel text..." -> [sel, "text..."]
  const m = rest.match(/^(\S+)\s*(.*)$/);
  return m ? [m[1], m[2]] : [rest, ''];
}

async function main() {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  // Backend now serves HTTPS with a locally-generated self-signed cert
  // (backend/certs/) -- trust it here the same way a real browser needs a
  // one-time manual "proceed anyway" click for it.
  const page = await browser.newPage({ ignoreHTTPSErrors: true });
  page.on('console', msg => {
    if (msg.type() === 'error') consoleErrors.push(msg.text());
  });
  page.on('pageerror', err => consoleErrors.push(String(err)));

  for (const line of lines) {
    const [cmd, rest] = splitArgs(line);
    try {
      switch (cmd) {
        case 'nav': {
          await page.goto(rest, { waitUntil: 'domcontentloaded', timeout: 30_000 });
          console.log('nav ->', rest);
          break;
        }
        case 'wait-for': {
          // rest is like: text=Dashboard  OR  a CSS selector
          let selector = rest;
          if (rest.startsWith('text=')) {
            const needle = rest.slice(5);
            selector = `:text("${needle}")`;
          }
          await page.waitForSelector(selector, { timeout: 15_000 });
          console.log('wait-for OK:', rest);
          break;
        }
        case 'click': {
          await page.click(rest, { timeout: 10_000 });
          console.log('click OK:', rest);
          break;
        }
        case 'click-text': {
          await page.getByText(rest, { exact: false }).first().click({ timeout: 10_000 });
          console.log('click-text OK:', rest);
          break;
        }
        case 'fill': {
          const [sel, value] = splitArgs(rest);
          await page.fill(sel, value, { timeout: 10_000 });
          console.log('fill OK:', sel, '=', value);
          break;
        }
        case 'press': {
          await page.keyboard.press(rest);
          console.log('press OK:', rest);
          break;
        }
        case 'screenshot': {
          const name = rest || `ss-${Date.now()}`;
          const file = path.join(SHOT_DIR, `${name}.png`);
          await page.screenshot({ path: file, fullPage: true });
          console.log('screenshot ->', file);
          break;
        }
        case 'eval': {
          const result = await page.evaluate(rest);
          console.log('eval ->', JSON.stringify(result));
          break;
        }
        case 'text': {
          const sel = rest || 'body';
          const t = await page.locator(sel).first().innerText();
          console.log('text ->', t.slice(0, 500));
          break;
        }
        case 'console': {
          console.log('console --errors ->', consoleErrors.length === 0 ? '(none)' : consoleErrors.join(' | '));
          break;
        }
        case 'sleep': {
          await new Promise(r => setTimeout(r, Number(rest) || 1000));
          break;
        }
        default:
          console.log('unknown command:', cmd);
      }
    } catch (err) {
      console.log(`ERROR on "${line}":`, err.message.split('\n')[0]);
    }
  }

  await browser.close();
}

main();
