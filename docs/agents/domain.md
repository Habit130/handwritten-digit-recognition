# Domain Docs

This repository uses a single-context domain documentation layout.

## Before exploring, read these

- **`docs/product/GLOBAL-STRATEGY.md`** — read before product, architecture, implementation-planning, or delivery work.
- **`docs/product/IMPLEMENTATION-SPEC.md`** — read before changing runtime, model, API, Web, challenge, or packaging behavior.
- **`CONTEXT.md`** at the repo root.
- **`docs/adr/`** — read ADRs that touch the area you're about to work in.

If either does not exist, proceed silently. Do not flag its absence or suggest creating it upfront. The `/domain-modeling` skill, reached through `/grill-with-docs` and `/improve-codebase-architecture`, creates these files lazily when terms or decisions are actually resolved.

## File structure

```text
/
├── CONTEXT.md
├── docs/
│   ├── adr/
│   ├── product/
│   │   ├── GLOBAL-STRATEGY.md
│   │   └── IMPLEMENTATION-SPEC.md
│   └── verification/
└── src/
```

## Use the glossary's vocabulary

When output names a domain concept—in an issue title, refactor proposal, hypothesis, or test name—use the term defined in `CONTEXT.md`. Do not drift to synonyms the glossary explicitly avoids.

If a required concept is absent from the glossary, reconsider whether the language belongs to the project or note a real gap for `/domain-modeling`.

## Flag ADR conflicts

If output contradicts an existing ADR, surface the conflict explicitly rather than silently overriding it.
