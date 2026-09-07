// Grab wall-clock frames of an animated SVG from a throwaway headless Chrome.
// Verification only; nothing in the profile build depends on it.
// usage: node tools/frames.mjs <svg> <outdir> <ms,ms,ms>
import { spawn } from "node:child_process";
import { mkdtempSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";

// Headless Chrome reports prefers-reduced-motion: reduce by default, so the
// motion path only shows up once the media state is emulated. Pass "reduce" to
// capture the other branch.
const [svg, outDir, times = "200,1500,3500,6500,9000", motion = "no-preference",
  scheme = "dark"] = process.argv.slice(2);
const PORT = 9333;
const CHROME =
  process.env.CHROME ||
  "C:/Program Files/Google/Chrome/Application/chrome.exe";

const head = readFileSync(resolve(svg), "utf8").slice(0, 400);
const W = Number(head.match(/width="(\d+)"/)?.[1] ?? 900);
const H = Number(head.match(/height="(\d+)"/)?.[1] ?? 226);

const profile = mkdtempSync(join(tmpdir(), "frames-"));
const page = join(profile, "page.html");
writeFileSync(
  page,
  `<!doctype html><meta charset=utf-8><style>html,body{margin:0;padding:0}` +
    `img{display:block}</style><img src="${pathToFileURL(resolve(svg))}">`,
);

const chrome = spawn(CHROME, [
  "--headless=new",
  "--disable-gpu",
  "--hide-scrollbars",
  "--force-device-scale-factor=1",
  // Headless defaults prefers-reduced-motion to reduce, and Emulation does not
  // reach the separate document an SVG <img> renders in.
  ...(motion === "reduce" ? [] : ["--force-prefers-no-reduced-motion"]),
  `--user-data-dir=${profile}`,
  `--window-size=${W},${H}`,
  `--remote-debugging-port=${PORT}`,
  pathToFileURL(page).href,
]);
chrome.on("error", (e) => {
  throw e;
});
chrome.stderr.on("data", (d) => process.stderr.write(d));

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

let target;
for (let i = 0; i < 60 && !target; i++) {
  await sleep(250);
  // Chrome binds DevTools to ::1 on this box, not 127.0.0.1, so try both.
  for (const host of ["[::1]", "127.0.0.1"]) {
    try {
      const list = await (
        await fetch(`http://${host}:${PORT}/json/list`)
      ).json();
      target = list.find((t) => t.type === "page" && t.url.startsWith("file:"));
      if (target) break;
    } catch {}
  }
}
if (!target) throw new Error("headless chrome never came up");

const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r) => (ws.onopen = r));
let id = 0;
const pending = new Map();
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) pending.get(m.id)(m.result);
};
const send = (method, params = {}) =>
  new Promise((r) => {
    const n = ++id;
    pending.set(n, r);
    ws.send(JSON.stringify({ id: n, method, params }));
  });

await send("Emulation.setEmulatedMedia", {
  features: [
    { name: "prefers-reduced-motion", value: motion },
    { name: "prefers-color-scheme", value: scheme },
  ],
});

mkdirSync(outDir, { recursive: true });
const wanted = times.split(",").map(Number);
const t0 = Date.now();
for (const at of wanted) {
  const wait = at - (Date.now() - t0);
  if (wait > 0) await sleep(wait);
  const { data } = await send("Page.captureScreenshot", {
    format: "png",
    captureBeyondViewport: true,
    clip: { x: 0, y: 0, width: W, height: H, scale: 1 },
  });
  writeFileSync(join(outDir, `t${at}.png`), Buffer.from(data, "base64"));
  console.log("captured", at);
}
ws.close();
chrome.kill();
