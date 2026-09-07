// Set the six pinned repos, through an already-signed-in Chrome.
//
// Pinned items have no REST or GraphQL mutation, so this drives the real
// "Customize your pins" dialog and then re-reads the pins over GraphQL,
// because a dialog that closes is not evidence that anything was saved.
//
//   node tools/set_pins.mjs wow-secret-lint npm-script-lens ...
import { execFileSync } from "node:child_process";

import { attach, closeTab, endpoint, evaluate, newTab, sleep, waitFor } from "./cdp.mjs";

const USER = "Booyaka101";
const names = process.argv.slice(2);
if (names.length !== 6) {
  throw new Error(`GitHub pins exactly six; got ${names.length}`);
}

const gh = (args) => execFileSync("gh", args, { encoding: "utf8" }).trim();

const ids = names.map((name) => ({
  name,
  id: gh(["api", `repos/${USER}/${name}`, "--jq", ".id"]),
}));

const pinned = () =>
  gh([
    "api",
    "graphql",
    "-f",
    `query={user(login:"${USER}"){pinnedItems(first:6,types:REPOSITORY){nodes{... on Repository{name}}}}}`,
    "--jq",
    ".data.user.pinnedItems.nodes[].name",
  ])
    .split("\n")
    .filter(Boolean);

console.log("before:", pinned().join(" "));

const base = await endpoint(9222);
const tab = await newTab(base, `https://github.com/${USER}`);
const cdp = await attach(tab);
await cdp.send("Runtime.enable");
await waitFor(cdp, "document.readyState === 'complete'", 30000);
await sleep(2000);

const opened = await evaluate(
  cdp,
  `(() => {
     const b = [...document.querySelectorAll('button')]
       .find(e => /customi[sz]e your pins/i.test(e.textContent));
     if (!b) return false;
     b.click();
     return true;
   })()`,
);
if (!opened) throw new Error("no 'Customize your pins' button on the profile");
await sleep(2500);

const wanted = JSON.stringify(ids.map((r) => `${r.id}-Repository`));

// The dialog paginates, so keep asking for more until every target is on the
// page. Without this a repo further down the list silently never gets ticked.
for (let i = 0; i < 12; i++) {
  const missing = await evaluate(
    cdp,
    `(() => {
       const have = new Set([...document.querySelectorAll('input[name="pinned_items_id_and_type[]"]')].map(c => c.value));
       return ${wanted}.filter(v => !have.has(v));
     })()`,
  );
  if (!missing.length) break;
  const more = await evaluate(
    cdp,
    `(() => {
       const b = [...document.querySelectorAll('button')].find(e => /load more/i.test(e.textContent) && !e.disabled);
       if (!b) return false;
       b.click();
       return true;
     })()`,
  );
  if (!more) throw new Error(`not offered in the dialog: ${missing.join(", ")}`);
  await sleep(1800);
}

// One click at a time, re-querying between: the dialog re-renders its list on
// every change, so a batched pass clicks stale nodes and silently loses ticks.
const clickBox = async (value, want) => {
  for (let i = 0; i < 10; i++) {
    const state = await evaluate(
      cdp,
      `(() => {
         const c = [...document.querySelectorAll('input[name="pinned_items_id_and_type[]"]')]
           .find(x => x.value === ${JSON.stringify(value)});
         if (!c) return 'gone';
         if (c.checked === ${want}) return 'done';
         c.click();
         return 'clicked';
       })()`,
    );
    if (state === "done") return true;
    if (state === "gone") return false;
    await sleep(600);
  }
  return false;
};

const checkedNow = () =>
  evaluate(
    cdp,
    `[...document.querySelectorAll('input[name="pinned_items_id_and_type[]"]')]
       .filter(c => c.checked).map(c => c.value)`,
  );

const want = ids.map((r) => `${r.id}-Repository`);
for (const value of await checkedNow()) {
  if (!want.includes(value)) await clickBox(value, false);
}
for (const value of want) {
  if (!(await clickBox(value, true))) {
    throw new Error(`could not tick ${value}`);
  }
}
const applied = await checkedNow();
console.log("ticked:", applied.length);

const saved = await evaluate(
  cdp,
  `(() => {
     const b = [...document.querySelectorAll('button')].find(e => /save pins/i.test(e.textContent));
     if (!b) return false;
     b.click();
     return true;
   })()`,
);
if (!saved) throw new Error("no 'Save pins' button");
await sleep(4000);

await closeTab(base, tab.id);
cdp.close();

const after = pinned();
console.log("after: ", after.join(" "));
const missed = names.filter((n) => !after.includes(n));
if (missed.length) {
  console.log("NOT PINNED:", missed.join(" "));
  process.exitCode = 1;
}
