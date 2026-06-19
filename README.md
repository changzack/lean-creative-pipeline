# Lean Creative Pipeline

A stripped-down LangGraph-style creative pipeline for AI agents that
generate web prototypes. Built after a $20-per-run, 30-minute creative
pipeline produced output a 30-second one-shot beat consistently.

The lean graph keeps only what produced unique creative value: a designer
fan-out, a human approach gate, a builder fan-out, and a human review.
Everything else (research nodes, asset-gen nodes, QA loops, playability
loops, judge polish loops, pairwise ranking) was dropped — those nodes
burned 80% of the budget on brief-specific heuristics that didn't
generalize.

**Cost:** ~$1-2/run vs $15-20/run on the original pipeline.
**Output:** measurably better per creative-director taste review.

## Topology

```
START → scope_contract → designer (×3 fan-out) → approach_gate (HUMAN)
                                                       ↓
                                                    builder (×3 fan-out)
                                                       ↓
                                                    human_gate (HUMAN)
                                                       ↓
                                                      END
```

## What's in this repo

- **`skills/`** — 5 standalone skill markdown files that carry the creative
  judgment the pipeline used to enforce with regex-based QA loops:
  - `creative-approach-craft` — how to write an approach doc that commits
    on 5 axes (palette, typography, technique, layout, voice) and avoids
    LLM convergence patterns
  - `creative-build-craft` — the move set, performance rules, and build
    checklist that separate award-grade work from generic landing pages
  - `creative-taste-gate` — the two-question human review that replaces
    QA/playability loops
  - `creative-brief-author` — the 8-section brief template and the
    outcome-vs-tool framing
  - `creative-asset-strategy` — when NOT to generate assets, why most
    builds need 0-1, and the critical "vision attachments not text
    descriptions" rule
- **`lean-references/`** — the 5 refero-curated landing pages used as
  vision references. Includes both the JPG previews (the actual signal)
  and a markdown writeup of which axis each ref owns (scaffolding).
- **`pipeline/`** — the lean-graph code excerpt: `build_graph_lean()`,
  `load_skill()`, `load_lean_creative_pack()`, and the designer + builder
  injection sites. Extracted from a larger `pipeline.py` so you can port
  the ideas without taking the legacy graph.

## Two non-obvious lessons

### 1. Skills > QA loops for creative work

The original pipeline had a QA loop that string-matched brief content for
heuristics like "does the page contain the word 'total profit'?" — a
leftover from a finance-quiz brief. On a pizza-cutting game it burned $17
of the $20 budget patching phantom errors. On a landing page it failed the
same way.

Replacing the QA loop with a human-judgment gate guided by the
`creative-taste-gate` skill produced better output for an order of
magnitude less money.

### 2. Visual references must be PIXELS, not text

Text descriptions of design are inert to an LLM. Telling Claude "deep
black canvas with violet accent and oversized pill button" doesn't
transfer the taste of the page, because the model never saw it.

If you want a visual reference to influence output, the model has to SEE
the image:

- For Claude / Hermes-routed agents: provide image file paths + instruct
  the agent to Read/View each one. Hermes can read images.
- For GPT-5 / Gemini / direct-API: attach as proper multimodal vision
  input.
- For reference databases (Refero, Awwwards, etc.): fetch the preview
  JPG to disk, then route it through the same vision channel.

Verified empirically: same brief, same skills, same 3 designers — v3 with
text-only refs produced output indistinguishable from no-reference
baseline. v4 with the same 5 refs as actual JPG vision attachments was
"way better" per CD review.

When in doubt: pixels.

## How to use

You don't need our exact `pipeline.py` (it's 9500 lines of legacy). The
key ideas are stack-agnostic:

1. **Strip your graph** to: scope → designer → human gate → builder →
   human gate. No auto-iteration. Two human decision points.

2. **Load creative skills** directly into your designer + builder
   prompts. The 5 skills in `skills/` are stack-agnostic markdown. They
   carry the creative judgment that QA loops used to enforce
   mechanically.

3. **Pass visual references as vision attachments**, never as text. The
   refero JPGs in `lean-references/images/` are a starter set; swap them
   for refs appropriate to your brief.

4. **Replace QA/polish loops with one human review pass** guided by the
   `creative-taste-gate` skill.

## Provenance

Originally built as part of OpenClaw — a multi-agent creative orchestration
system. The lean graph is the result of stripping back ~6000 lines of
plumbing that was solving problems we didn't actually have.

## License

MIT. Take whatever's useful.
