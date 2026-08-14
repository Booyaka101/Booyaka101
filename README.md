### Christo · `Booyaka101`

Hong Kong. I build guardrails for dependency and toolchain risk, plus local AI pipelines and game tooling.

### Tools

**[hass-breakage-radar](https://github.com/Booyaka101/hass-breakage-radar)**. Which of your Home Assistant custom integrations stop working, and in which future release. Crawls every HACS integration daily for deprecated HA APIs, and ships a HACS-installable integration that reports on your own box. [Live dashboard](https://booyaka101.github.io/hass-breakage-radar/).

**[ts7-compat-guard](https://github.com/Booyaka101/ts7-compat-guard)**. TypeScript 7.0 / tsgo readiness scanner. Compiler-API dependencies and removed tsconfig options with line numbers. Config-only, so no false positives. CLI, GitHub Action, SARIF.

**[npm-script-lens](https://github.com/Booyaka101/npm-script-lens)**. Audit npm lifecycle scripts for behavioural risk before you approve them under npm v12 `allowScripts`.

**[rust-symbol-audit](https://github.com/Booyaka101/rust-symbol-audit)**. Capability-creep triage for Rust dependency PRs. Diffs demangled symbols, inspects `build.rs` and proc-macros, checks provenance and advisories, with a review ratchet you can block merges on.

**[cargo-witness](https://github.com/Booyaka101/cargo-witness)**. Detects Rust supply-chain attacks by diffing published crate artifacts against their git source. CLI, daemon, GitHub Action.

**[palschema-hub](https://github.com/Booyaka101/palschema-hub)**. Community schema registry for Palworld PalSchema raw-table mods. 31 SDK-verified DataTable schemas and a validator CLI.

**[agentscript-nvim](https://github.com/Booyaka101/agentscript-nvim)**. Neovim support for Salesforce Agent Script: filetype, LSP, tree-sitter, fallback syntax.

### Upstream

When I depend on something and hit a real bug, I send the fix back. 45 merged PRs across 25 projects so far, including sqlfluff (6), KOReader, nvim-lspconfig, minijinja, gh-dash, lualine.nvim, obsidian.nvim, aerial.nvim, Cockatrice and this-week-in-rust. 33 more open.

[Every PR I've opened](https://github.com/issues?q=author%3ABooyaka101+is%3Apr) · [issues I've filed](https://github.com/issues?q=author%3ABooyaka101+is%3Aissue+-author%3Aapp%2Fgithub-actions)

### Elsewhere

**[The Daily Fable](https://booyaka101.github.io/thedailyfable/)**. One brand-new generative piece every day, made end to end by an AI. So far: typefaces, a fugue under strict counterpoint, a board game, a neural net learning English from one book, and field recordings of a language family that never existed.

**[comfyui-vlm-gates](https://github.com/Booyaka101/comfyui-vlm-gates)**. Multi-VLM consensus gates and quality scoring for AI image pipelines. Catches bad renders before they ship.

WoW Ascension (3.3.5) addons: **[Scrap](https://github.com/Booyaka101/Scrap)** (auto-sell greys, AdiBags and Bagnon integration) and **[CCTracker](https://github.com/Booyaka101/CCTracker)** (crowd control, silence and interrupt tracker).

Open to work on dependency-security tooling, ComfyUI pipelines, or anything in the Ascension addon ecosystem. cbosch101@gmail.com
