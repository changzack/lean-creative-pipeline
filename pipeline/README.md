# Lean Creative Pipeline — code excerpt

This directory shows how the lean graph is wired into pipeline.py. The full
pipeline.py (9500+ lines, the inherited legacy from the OpenClaw project) is
not included here — only the surgical additions that produce the lean graph.

## Files

- `lean_graph.py` — the additions to pipeline.py: `build_graph_lean()`,
  `load_skill()`, `load_lean_creative_pack()`, and the designer/builder
  injection sites. These are extracted verbatim from pipeline.py so you can
  port them into your own LangGraph orchestrator without bringing the whole
  legacy graph with you.
- `cli_changes.diff` — the unified diff of every change made to the CLI
  argparser and the initial_state dict (additions only; nothing legacy was
  removed).

## How the lean graph runs

```bash
./run-pipeline.sh run --graph lean \
  --brief path/to/brief.md \
  --name my-run
```

Topology:

```
START → scope_contract → designer (×3 fan-out) → approach_gate (HUMAN GATE)
                                                       ↓
                                                    builder (×3 fan-out)
                                                       ↓
                                                    human_gate (HUMAN GATE)
                                                       ↓
                                                      END
```

What was dropped from the full graph: `research`, `asset_gen`, `qa_loop`,
`playability_loop`, `judge_polish`, `pairwise_rank`. These nodes burned ~80%
of the budget on brief-specific heuristics ("does the page contain the text
'total profit'?") that didn't generalize to new briefs.

## What replaces those nodes

1. **Skills loaded into prompts** — `creative-approach-craft`,
   `creative-build-craft`, `creative-taste-gate`, `creative-asset-strategy`,
   `creative-brief-author` are injected directly into the designer + builder
   task strings. They carry the creative judgment that the QA/judge nodes
   used to enforce mechanically.

2. **Visual references as vision attachments** — the 5 refero JPG previews
   are passed to the designer (via Hermes Read tool) and the builder (via
   the existing `moodboard_images` channel for GPT-5 / Gemini). Text
   descriptions of design don't transfer taste; pixels do.

3. **Human judgment at the gates** — the approach gate and the post-build
   human gate replace the auto-scoring loops. A creative director with taste
   making 2 decisions is more valuable than 20 polish iterations against a
   regex-based rubric.

## Cost

- Full graph: $15-20 per run (cost-cap-bound on most briefs)
- Lean graph: $1-2 per run (designer + approach gate + builder, no auto-iter)

## How to port this to your own pipeline

You don't need our exact pipeline.py. The key ideas:

1. Strip your graph to: scope → designer → human gate → builder → human gate.
2. Load creative skills directly into your designer + builder prompts. The 5
   skills in `../skills/` are stack-agnostic markdown.
3. Pass visual references as vision attachments, NOT as text descriptions.
   For Anthropic / Claude: route through a tool-use agent (like Hermes) so
   the model can read images. For OpenAI / Google: use multimodal vision
   input directly.
4. Replace QA/polish loops with one human review pass guided by the
   `creative-taste-gate` skill.
