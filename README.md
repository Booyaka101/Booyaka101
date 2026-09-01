### Christo · `Booyaka101`

Hong Kong. I build guardrails for dependency and toolchain risk, plus local AI pipelines and game tooling.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.svg">
  <img alt="Live project figures over a flow field seeded by today's date" src="assets/hero-light.svg">
</picture>

<!-- auto:stamp -->
<sub>Live figures, rebuilt 2026-09-01.</sub>
<!-- /auto:stamp -->

### Tools

**[hass-breakage-radar](https://github.com/Booyaka101/hass-breakage-radar)**. Which of your Home Assistant custom integrations stop working, and in which future release. Crawls every HACS integration daily for deprecated HA APIs, and ships a HACS-installable integration that reports on your own box. [Live dashboard](https://booyaka101.github.io/hass-breakage-radar/).

<!-- auto:radar -->
> Today's crawl checked **3,992** HACS integrations against core 2026.10 and found **2,263** deprecation hits across **875** repos. **2,342** are clean. Next up: **11** break in Home Assistant 2026.10.
<!-- /auto:radar -->

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/breakage-dark.svg">
  <img alt="Column chart: when HACS integrations first break, by Home Assistant release" src="assets/breakage-light.svg">
</picture>

**[ts7-compat-guard](https://github.com/Booyaka101/ts7-compat-guard)**. TypeScript 7.0 / tsgo readiness scanner. Compiler-API dependencies and removed tsconfig options with line numbers. Config-only, so no false positives. CLI, GitHub Action, SARIF.

**[npm-script-lens](https://github.com/Booyaka101/npm-script-lens)**. Audit npm lifecycle scripts for behavioural risk before you approve them under npm v12 `allowScripts`. I run it daily against a download-ranked sample of the registry and publish the result as the [npm install-script census](https://github.com/Booyaka101/npm-install-census).

<!-- auto:census -->
> Today's census audited **3,093** packages from the registry: **25** run an install script, **16** score HIGH. Biggest is `esbuild` at 255.5M installs a week.
<!-- /auto:census -->

**[rust-symbol-audit](https://github.com/Booyaka101/rust-symbol-audit)**. Capability-creep triage for Rust dependency PRs. Diffs demangled symbols, inspects `build.rs` and proc-macros, checks provenance and advisories, with a review ratchet you can block merges on.

**[cargo-witness](https://github.com/Booyaka101/cargo-witness)**. Detects Rust supply-chain attacks by diffing published crate artifacts against their git source. CLI, daemon, GitHub Action.

**[palschema-hub](https://github.com/Booyaka101/palschema-hub)**. Community schema registry for Palworld PalSchema raw-table mods. 31 SDK-verified DataTable schemas and a validator CLI.

**[agentscript-nvim](https://github.com/Booyaka101/agentscript-nvim)**. Neovim support for Salesforce Agent Script: filetype, LSP, tree-sitter, fallback syntax.

### Upstream

<!-- auto:upstream -->
When I depend on something and hit a real bug, I send the fix back. **46 merged PRs across 26 projects**, including koreader (2), nvim-lspconfig, gh-dash (2), sqlfluff (6), lualine.nvim, awesome-nodejs-security, minijinja, this-week-in-rust, aerial.nvim (2), obsidian.nvim (2). 35 more open.
<!-- /auto:upstream -->

[Every PR I've opened](https://github.com/issues?q=author%3ABooyaka101+is%3Apr) · [issues I've filed](https://github.com/issues?q=author%3ABooyaka101+is%3Aissue+-author%3Aapp%2Fgithub-actions)

### Elsewhere

**[The Daily Fable](https://booyaka101.github.io/thedailyfable/)**. One brand-new generative piece every day, made end to end by an AI. So far: typefaces, a fugue under strict counterpoint, a board game, a neural net learning English from one book, and field recordings of a language family that never existed.

<!-- auto:fable -->
> Latest: [Day 36 — Séance for an Extinct Orchestra](https://booyaka101.github.io/thedailyfable/day36/) · 2026-09-01 · 36 pieces so far.
<!-- /auto:fable -->

**[comfyui-vlm-gates](https://github.com/Booyaka101/comfyui-vlm-gates)**. Multi-VLM consensus gates and quality scoring for AI image pipelines. Catches bad renders before they ship.

WoW Ascension (3.3.5) addons: **[Scrap](https://github.com/Booyaka101/Scrap)** (auto-sell greys, AdiBags and Bagnon integration) and **[CCTracker](https://github.com/Booyaka101/CCTracker)** (crowd control, silence and interrupt tracker).
