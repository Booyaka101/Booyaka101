### Christo · `Booyaka101`

Hong Kong. I build guardrails for dependency and toolchain risk, plus local AI pipelines and game tooling.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.svg">
  <img alt="Live project figures over a flow field seeded by today's date" src="assets/hero-light.svg">
</picture>

<!-- auto:stamp -->
<sub>Live figures, rebuilt 2026-09-11.</sub>
<!-- /auto:stamp -->

<!-- auto:npm -->
> The packages I publish are pulling **1,470** installs a week between **18** of them, most of it `@booyaka/mcp-vet` at 351.
<!-- /auto:npm -->

### Ecosystem watch

Three ecosystems I crawl on a schedule, so the answer is already sitting there when you need it rather than being something you have to go and measure. All three, and everything I publish, are on one page at [booyaka101.github.io](https://booyaka101.github.io/).

**[hass-breakage-radar](https://github.com/Booyaka101/hass-breakage-radar)**. Which of your Home Assistant custom integrations stop working, and in which future release. Crawls every HACS integration daily for deprecated HA APIs, and ships a HACS-installable integration that reports on your own box. [Live dashboard](https://booyaka101.github.io/hass-breakage-radar/).

<!-- auto:radar -->
> Today's crawl checked **4,010** HACS integrations against core 2026.10 and found **2,378** deprecation hits across **907** repos. **2,330** are clean. Next up: **10** break in Home Assistant 2026.10.
<!-- /auto:radar -->

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/breakage-dark.svg">
  <img alt="Column chart: when HACS integrations first break, by Home Assistant release" src="assets/breakage-light.svg">
</picture>

**[eslint10-matrix](https://github.com/Booyaka101/eslint10-matrix)**. Can you upgrade to ESLint 10 yet? A nightly matrix of plugins actually executed against real ESLint 9 and 10 installs, not read off a peer range, plus a CLI that answers it for your own repo. [Live matrix](https://booyaka101.github.io/eslint10-matrix/).

<!-- auto:eslint -->
> Last night's matrix ran **54** plugins, 569M weekly installs between them, against ESLint 10.10.0: **44** clean, **10** not. **6** of those worked on 9.39.5.
<!-- /auto:eslint -->

**[npm-install-census](https://github.com/Booyaka101/npm-install-census)**. What actually runs at `npm install` time, measured daily against a download-ranked sample of the registry with npm-script-lens.

<!-- auto:census -->
> Today's census audited **3,126** packages from the registry: **26** run an install script, **17** score HIGH. Biggest is `esbuild` at 255.5M installs a week.
<!-- /auto:census -->

### Tools

**[wow-secret-lint](https://github.com/Booyaka101/wow-secret-lint)**. Find WoW retail addon Secret Value violations in Lua before they ship, rather than when a player reports a taint error. CLI plus GitHub Action.

**[mcp-vet](https://github.com/Booyaka101/mcp-vet)**. Scan MCP server source for patterns that break under the 2026-07-28 Model Context Protocol spec, before the spec date rather than after it.

**[mcp-app-debug](https://github.com/Booyaka101/mcp-app-debug)**. Local debug host for MCP Apps. Renders your server's app in a real browser with full postMessage protocol visibility and five automated diagnostics.

**[npm-script-lens](https://github.com/Booyaka101/npm-script-lens)**. Audit npm lifecycle scripts for behavioural risk before you approve them under npm v12 `allowScripts`. Behavioural analysis, `binding.gyp` inspection, resolved provenance identity.

**[gemcatch](https://github.com/Booyaka101/gemcatch)**. Fire-and-forget CLI for Gemini's Interactions API background execution. Submit a long research prompt, close the laptop, collect the result later.

**[ts7-compat-guard](https://github.com/Booyaka101/ts7-compat-guard)**. TypeScript 7.0 / tsgo readiness scanner. Compiler-API dependencies and removed tsconfig options with line numbers. Config-only, so no false positives. CLI, GitHub Action, SARIF.

**[rust-symbol-audit](https://github.com/Booyaka101/rust-symbol-audit)**. Capability-creep triage for Rust dependency PRs. Diffs demangled symbols, inspects `build.rs` and proc-macros, checks provenance and advisories, with a review ratchet you can block merges on.

**[cargo-witness](https://github.com/Booyaka101/cargo-witness)**. Detects Rust supply-chain attacks by diffing published crate artifacts against their git source. CLI, daemon, GitHub Action.

**[palschema-hub](https://github.com/Booyaka101/palschema-hub)**. Community schema registry for Palworld PalSchema raw-table mods. 31 SDK-verified DataTable schemas and a validator CLI.

**[agentscript-nvim](https://github.com/Booyaka101/agentscript-nvim)**. Neovim support for Salesforce Agent Script: filetype, LSP, tree-sitter, fallback syntax.

### Upstream

<!-- auto:upstream -->
When I depend on something and hit a real bug, I send the fix back. **47 merged PRs across 27 projects**, including koreader (2), nvim-lspconfig, gh-dash (2), ai-toolkit, sqlfluff (6), lualine.nvim, awesome-nodejs-security, minijinja, this-week-in-rust, aerial.nvim (2). 34 more open.
<!-- /auto:upstream -->

[Every PR I've opened](https://github.com/issues?q=author%3ABooyaka101+is%3Apr) · [issues I've filed](https://github.com/issues?q=author%3ABooyaka101+is%3Aissue+-author%3Aapp%2Fgithub-actions)

### Elsewhere

**[The Daily Fable](https://booyaka101.github.io/thedailyfable/)**. One brand-new generative piece every day, made end to end by an AI. So far: typefaces, a fugue under strict counterpoint, a board game, a neural net learning English from one book, and field recordings of a language family that never existed.

<!-- auto:fable -->
> Latest: [Day 46 — Underhand](https://booyaka101.github.io/thedailyfable/day46/) · 2026-09-11 · 46 pieces so far.
<!-- /auto:fable -->

**[comfyui-vlm-gates](https://github.com/Booyaka101/comfyui-vlm-gates)**. Multi-VLM consensus gates and quality scoring for AI image pipelines. Catches bad renders before they ship.

WoW Ascension (3.3.5) addons: **[Scrap](https://github.com/Booyaka101/Scrap)** (auto-sell greys, AdiBags and Bagnon integration) and **[CCTracker](https://github.com/Booyaka101/CCTracker)** (crowd control, silence and interrupt tracker).
