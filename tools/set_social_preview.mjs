// Set the social preview image on repos, through an already-signed-in Chrome.
//
// There is no REST endpoint for the social preview, so this drives the real
// upload widget: put the file on the hidden input and let GitHub's own
// file-attachment element fetch its S3 policy and submit the form. Every repo
// is then re-checked against the og:image it serves, because the widget going
// quiet is not evidence that anything was stored.
//
//   node tools/set_social_preview.mjs                 # every png in cards/
//   node tools/set_social_preview.mjs uv-cache-warden
import { readdirSync, statSync } from "node:fs";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { attach, closeTab, endpoint, evaluate, newTab, sleep, waitFor } from "./cdp.mjs";

const USER = "Booyaka101";
const PORT = Number(process.env.CDP_PORT || 9222);
const CARDS = resolve(fileURLToPath(new URL("../cards", import.meta.url)));

const wanted = process.argv.slice(2);
const names = (
  wanted.length
    ? wanted
    : readdirSync(CARDS)
        .filter((f) => f.endsWith(".png"))
        .map((f) => f.slice(0, -4))
).sort();

// The REST API does not expose the social preview at all, so the only honest
// check is the og:image the repo page actually serves. A repo with no custom
// image gets one generated at opengraph.githubassets.com instead.
const preview = async (repo) => {
  const r = await fetch(`https://github.com/${USER}/${repo}`, {
    headers: { "User-Agent": `${USER}-cards` },
  });
  const html = await r.text();
  const url = html.match(
    /<meta property="og:image" content="([^"]+)"/,
  )?.[1];
  return url && url.includes("repository-images.githubusercontent.com")
    ? url
    : "";
};

const base = await endpoint(PORT);
const tab = await newTab(base, "about:blank");
const cdp = await attach(tab);
await cdp.send("Runtime.enable");
await cdp.send("DOM.enable");
await cdp.send("Page.enable");

const results = [];
for (const repo of names) {
  const file = join(CARDS, `${repo}.png`);
  try {
    statSync(file);
  } catch {
    results.push([repo, "no card"]);
    continue;
  }

  const before = await preview(repo);
  await cdp.send("Page.navigate", {
    url: `https://github.com/${USER}/${repo}/settings`,
  });
  const ready = await waitFor(
    cdp,
    "!!document.querySelector('#repo-image-file-input')",
    30000,
  );
  if (!ready) {
    results.push([repo, "no upload widget (not admin, or page changed)"]);
    continue;
  }

  const { root } = await cdp.send("DOM.getDocument", { depth: -1 });
  const { nodeId } = await cdp.send("DOM.querySelector", {
    nodeId: root.nodeId,
    selector: "#repo-image-file-input",
  });
  await cdp.send("DOM.setFileInputFiles", { nodeId, files: [file] });

  // The widget uploads to S3 and submits the form on its own; poll the served
  // og:image rather than guessing how long that takes.
  let after = "";
  for (let i = 0; i < 20 && !after; i++) {
    await sleep(1500);
    const now = await preview(repo);
    if (now && now !== before) after = now;
  }
  results.push([repo, after ? "set" : "NOT SET"]);
  console.log(`${repo.padEnd(38)} ${after ? "set" : "NOT SET"}`);
}

await evaluate(cdp, "0").catch(() => {});
await closeTab(base, tab.id);
cdp.close();

const failed = results.filter(([, s]) => s !== "set");
console.log(`\n${results.length - failed.length}/${results.length} set`);
if (failed.length) {
  console.log("not set:");
  for (const [repo, why] of failed) console.log(`  ${repo}: ${why}`);
  process.exitCode = 1;
}
