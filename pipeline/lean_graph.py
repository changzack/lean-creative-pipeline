# Lean Creative Pipeline — code excerpt from pipeline.py
#
# These are the additions that turn a heavyweight LangGraph creative pipeline
# into the lean graph. Drop these into your own pipeline.py and wire them into
# your CLI + initial_state, or use them as reference when porting to a
# different orchestration framework.
#
# The full original pipeline.py is ~9500 lines (legacy from the OpenClaw
# project). This file shows only what the lean graph itself adds.

from pathlib import Path
from typing import Optional
from langgraph.graph import StateGraph, START, END

# These are assumed to exist from the rest of pipeline.py — they're the
# original node functions for the legacy graph, reused by the lean graph.
# - scope_contract_node, designer_node, approach_gate_node, builder_node,
#   human_gate_node, iterate_node, deploy_node
# - fan_out_designers, fan_out_builders
# - PipelineState (TypedDict)
# - WORKSPACE = Path("~/.openclaw/workspace").expanduser()


# ─────────────────────────────────────────────────────────────
# Skill + Reference loaders
# ─────────────────────────────────────────────────────────────
# The lean graph injects creative skills + a refero-sourced visual references
# pack into designer + builder prompts. This replaces the expensive
# research_node + asset_gen_node + QA loop with grounded creative judgment
# baked into the prompts themselves.

WORKSPACE_SKILLS = WORKSPACE / "skills"
LEAN_REFS_DIR = Path(__file__).parent / "lean-references"


def load_skill(name: str, max_chars: Optional[int] = None) -> str:
    """Load a SKILL.md from the workspace skills directory. Returns empty
    string if the skill doesn't exist (graceful degradation)."""
    path = WORKSPACE_SKILLS / name / "SKILL.md"
    if not path.exists():
        print(f"  ⚠️  Skill missing: {name}")
        return ""
    content = path.read_text()
    if max_chars:
        content = content[:max_chars]
    return content


def load_lean_creative_pack(role: str) -> str:
    """Build the creative knowledge pack injected into lean-graph designer
    or builder prompts.

    role: "designer" or "builder"

    Returns a single composed markdown string with:
      - Role-appropriate skills (approach-craft for designer,
        build-craft + asset-strategy for builder)
      - The shared creative-taste-gate skill (so both know the rubric)
      - The visual references pack (5 refero-curated real landing pages)
      - The creative-technologist persona (anti-slop ground rules)
    """
    parts = []

    # Persona / anti-slop ground rules — both roles get this
    ct = load_skill("creative-technologist", max_chars=8000)
    if ct:
        parts.append(
            "## CREATIVE GROUND RULES (read first — this is the bar)\n\n" + ct
        )

    # Role-specific skill
    if role == "designer":
        approach = load_skill("creative-approach-craft")
        if approach:
            parts.append(
                "## APPROACH CRAFT (how to write the approach doc)\n\n" + approach
            )
    elif role == "builder":
        build = load_skill("creative-build-craft")
        if build:
            parts.append("## BUILD CRAFT (the move set + checklist)\n\n" + build)
        assets = load_skill("creative-asset-strategy")
        if assets:
            parts.append(
                "## ASSET STRATEGY (most builds need 0-1 generated assets)\n\n"
                + assets
            )

    # Shared taste gate — both roles know how their output will be judged
    taste = load_skill("creative-taste-gate")
    if taste:
        parts.append("## TASTE GATE (how your output will be judged)\n\n" + taste)

    # Visual references — real landing pages from refero
    refs_path = LEAN_REFS_DIR / "visual-references.md"
    if refs_path.exists():
        parts.append(
            "## VISUAL REFERENCES (real landing pages, refero-curated)\n\n"
            + refs_path.read_text()
        )

    if not parts:
        return ""
    return "\n\n---\n\n".join(parts)


# ─────────────────────────────────────────────────────────────
# The lean graph itself
# ─────────────────────────────────────────────────────────────

def build_graph_lean():
    """Build the lean creative graph (5 nodes, no QA/judge loops).

    Topology:
      START → scope_contract → designer (×3 fan-out) → approach_gate (HUMAN)
                                                         ↓
                                                      builder (×3 fan-out)
                                                         ↓
                                                      human_gate (HUMAN)
                                                         ↓
                                                        END

    What was dropped from the full graph:
      - research (replaced by creative-approach-craft skill + refero refs)
      - asset_gen (replaced by `lean_asset_gen` — up to 5 HOSTED assets per
        concept, mixed images + 1 video loop max, public CDN URLs, no inlining)
      - qa_loop + playability_loop (replaced by creative-taste-gate skill +
        the human gate)
      - judge_polish + pairwise_rank (replaced by human judgment at the gate)

    Cost target: ~$1-2 per run vs ~$15-20 for the full graph.
    """
    graph = StateGraph(PipelineState)

    graph.add_node("scope_contract", scope_contract_node)
    graph.add_node("designer", designer_node)
    graph.add_node("approach_gate", approach_gate_node)
    graph.add_node("lean_asset_gen", lean_asset_gen_node)
    graph.add_node("builder", builder_node)
    graph.add_node("human_gate", human_gate_node)
    graph.add_node("iterate", iterate_node)
    graph.add_node("deploy", deploy_node)

    graph.add_edge(START, "scope_contract")
    # Skip research: designers read brief + load creative-approach-craft skill
    graph.add_conditional_edges("scope_contract", fan_out_designers, ["designer"])
    graph.add_edge("designer", "approach_gate")
    # Lean asset gen: at most ONE hosted image per concept, gated by the
    # designer's ASSET MANIFEST. If the manifest is empty, the node skips.
    # The hero image is pushed to changzack/prototypes/_assets/<run>/concept-N/
    # and served at https://changzack.github.io/prototypes/_assets/...
    # The builder writes `<img src="https://...">` directly. NO base64 inlining.
    graph.add_edge("approach_gate", "lean_asset_gen")
    graph.add_conditional_edges("lean_asset_gen", fan_out_builders, ["builder"])
    # Skip qa_loop / judge_loop / pairwise_rank entirely
    graph.add_edge("builder", "human_gate")
    # human_gate uses Command() to route to deploy/iterate/END
    graph.add_conditional_edges("iterate", fan_out_designers, ["designer"])
    graph.add_edge("deploy", END)

    return graph


# ─────────────────────────────────────────────────────────────
# Lean asset generation — host on a public CDN, do NOT inline
# ─────────────────────────────────────────────────────────────
# The full-graph asset_gen_node commissions up to 8 assets per concept and
# bakes them as base64 data URIs into the HTML. That produces 30-40MB single-
# page builds. The reason was historical: the full graph's QA walker opened
# builds via `file://` where remote `<img src="https://...">` tags fail CORS.
#
# The lean graph doesn't open builds from file:// — we deploy to GitHub Pages.
# So we generate UP TO 5 assets per concept (mixed images + 1 video loop max),
# push each to a public repo, and the builder writes plain `<img>` / `<video>`
# tags. HTML stays under 100KB. Per-concept caps: 5 assets, $2.00 budget.

# Replace these with your own public asset host. The default points at the
# repo this pipeline ships into.
PROTOTYPES_REPO_DIR = Path.home() / ".openclaw" / "workspace" / "prototypes-repo"
PROTOTYPES_PAGES_BASE = "https://changzack.github.io/prototypes"

# Per-concept caps for the lean asset gen node.
LEAN_ASSET_MAX_COUNT = 5
LEAN_ASSET_MAX_COST = 2.00
LEAN_ASSET_WARN_COST = 1.00


def host_assets_on_github_pages(run_name: str, concept_id: int, local_files: list) -> list:
    """Copy generated asset files into a public GitHub Pages repo, commit, and
    push. Returns the list of public URLs (one per file, in order). Skips and
    returns empty if the repo isn't cloned locally or the push fails — the
    builder will fall back to CSS/SVG in that case.
    """
    import shutil
    import subprocess as _sp

    if not PROTOTYPES_REPO_DIR.exists() or not (PROTOTYPES_REPO_DIR / ".git").exists():
        print(f"  [lean-asset-host] ⚠️  {PROTOTYPES_REPO_DIR} not a git checkout — skipping")
        return []

    rel_dir = Path("_assets") / run_name / f"concept-{concept_id}"
    dest_dir = PROTOTYPES_REPO_DIR / rel_dir
    dest_dir.mkdir(parents=True, exist_ok=True)

    urls = []
    for src in local_files:
        src = Path(src)
        if not src.exists():
            continue
        dst = dest_dir / src.name
        shutil.copyfile(src, dst)
        urls.append(f"{PROTOTYPES_PAGES_BASE}/{rel_dir.as_posix()}/{src.name}")

    if not urls:
        return []

    try:
        _sp.run(["git", "-C", str(PROTOTYPES_REPO_DIR), "pull", "--rebase", "--quiet"], check=False, timeout=30)
        _sp.run(["git", "-C", str(PROTOTYPES_REPO_DIR), "add", str(rel_dir)], check=True, timeout=15)
        _sp.run(
            ["git", "-C", str(PROTOTYPES_REPO_DIR), "commit", "-m",
             f"lean asset gen: {run_name} concept-{concept_id} ({len(urls)} file(s))"],
            check=True, timeout=15,
        )
        _sp.run(["git", "-C", str(PROTOTYPES_REPO_DIR), "push", "--quiet"], check=True, timeout=60)
        print(f"  [lean-asset-host] ✅ pushed {len(urls)} asset(s) for concept-{concept_id}")
    except Exception as e:
        print(f"  [lean-asset-host] ⚠️  push failed: {e}")
        return []

    return urls


def lean_asset_gen_node(state):
    """Lean asset gen: up to LEAN_ASSET_MAX_COUNT assets per concept (mixed
    images + at most 1 video loop), hosted at public URLs. Skips concepts
    whose approach doc has no ASSET MANIFEST. Stops a concept early when
    cumulative cost hits LEAN_ASSET_MAX_COST.

    Assumes these helpers exist in your codebase (from the full graph):
      - extract_asset_manifest(approach_content) → list of asset dicts
      - generate_asset(asset, fal_key) → {url, kind, ext, cost, model, ...}
      - route_asset_model(asset) → fal model id
      - RUNS_DIR (Path)
    """
    import os, json, urllib.request

    print(f"[LEAN ASSET GEN] Reviewing {len(state['approaches'])} approaches")
    fal_key = os.environ.get("FAL_KEY", "")
    if not fal_key:
        print("  [lean-asset-gen] ⚠️  FAL_KEY not set — skipping")
        return {"asset_manifest": {}, "asset_base_url": PROTOTYPES_PAGES_BASE}

    run_dir = RUNS_DIR / state["name"]
    assets_dir = run_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    all_assets = {}
    for approach in state["approaches"]:
        if approach.get("status") not in ("done", "approved", None):
            continue
        designer_id = approach["designer_id"]
        manifest = extract_asset_manifest(approach["content"])
        if not manifest:
            print(f"  [lean-asset-gen] Designer {designer_id}: no ASSET MANIFEST — skipping")
            all_assets[designer_id] = []
            continue

        manifest = manifest[:LEAN_ASSET_MAX_COUNT]
        concept_dir = assets_dir / f"concept-{designer_id}"
        concept_dir.mkdir(parents=True, exist_ok=True)
        print(f"  [lean-asset-gen] Designer {designer_id}: {len(manifest)} asset(s) to generate")

        generated = []
        concept_cost = 0.0
        for idx, asset in enumerate(manifest, start=1):
            if concept_cost >= LEAN_ASSET_MAX_COST:
                print(f"    [lean-asset-gen] ⚠️  hit ${LEAN_ASSET_MAX_COST:.2f} cap; dropping remaining")
                break
            result = generate_asset(asset, fal_key)
            if not result:
                continue
            ext = result.get("ext") or ("mp4" if result.get("kind") == "video" else "jpg")
            local_path = concept_dir / f"{asset['name']}.{ext}"
            try:
                urllib.request.urlretrieve(result["url"], str(local_path))
                result["local_path"] = str(local_path)
                result["size_kb"] = local_path.stat().st_size // 1024
            except Exception as e:
                print(f"    [lean-asset-gen] download failed: {e}")
                continue
            concept_cost += result.get("cost", 0.0)
            hosted = host_assets_on_github_pages(state["name"], designer_id, [local_path])
            result["hosted_url"] = hosted[0] if hosted else result.get("url", "")
            generated.append(result)

        if not generated:
            all_assets[designer_id] = []
            continue

        # ASSETS.md: list every asset with type-specific embed snippets
        # (img for images, autoplay-muted-loop video tag for video-loops).
        lines = [
            f"# Hero Assets — concept-{designer_id} (HOSTED, do NOT inline)",
            "",
            f"{len(generated)} asset(s) generated and uploaded to a public CDN.",
            "Use `<img src=\"...\">` for images, `<video src=\"...\" autoplay muted loop playsinline>` for video-loops.",
            "",
        ]
        for a in generated:
            url = a["hosted_url"]
            kind = a.get("kind", "image")
            name = a["name"]
            desc = a.get("prompt", "")[:160]
            lines.append(f"## {name}  *(type: {a.get('type','image')} · {a.get('size_kb','?')}KB)*")
            lines.append(f"- Public URL: `{url}`")
            lines.append(f"- Description: {desc}")
            if kind == "video":
                lines.append("```html")
                lines.append(f'<video src="{url}" autoplay muted loop playsinline></video>')
                lines.append("```")
            else:
                lines.append("```html")
                lines.append(f'<img src="{url}" alt="{desc[:80]}" loading="eager" />')
                lines.append("```")
            lines.append("")

        (concept_dir / "ASSETS.md").write_text("\n".join(lines))
        with open(concept_dir / "manifest.json", "w") as f:
            json.dump(generated, f, indent=2)
        all_assets[designer_id] = generated

    return {"asset_manifest": all_assets, "asset_base_url": PROTOTYPES_PAGES_BASE}

# ─────────────────────────────────────────────────────────────
# Designer-node injection (inside the existing designer_node body)
# ─────────────────────────────────────────────────────────────
# Add this block to designer_node BEFORE composing the task string:

"""
# Lean graph: inject the creative pack (skills + refero visual refs)
lean_pack = ""
lean_vision_block = ""
if state.get("graph_mode") == "lean":
    lean_pack = load_lean_creative_pack(role="designer")
    if lean_pack:
        print(f"  📚 lean creative pack loaded: {len(lean_pack)//1000}KB (designer)")

    # Vision attachments: tell the designer to OPEN the 5 refero ref images
    # via the Read/View tool. Hermes can read images directly. Text
    # descriptions don't transfer taste — pixels do.
    refs_img_dir = LEAN_REFS_DIR / "images"
    if refs_img_dir.exists():
        ref_imgs = sorted(refs_img_dir.glob("*.jpg"))
        if ref_imgs:
            img_lines = "\n".join(
                f"- `{p}` — {p.stem} reference" for p in ref_imgs
            )
            lean_vision_block = (
                "\n## VISUAL REFERENCES — OPEN THESE IMAGES BEFORE WRITING\n\n"
                "Before writing your approach doc, you MUST use your Read/View "
                "tool to look at each of the 5 reference images below. The text "
                "descriptions in the VISUAL REFERENCES section above are "
                "scaffolding — the actual taste comes from seeing the pages. "
                "Pixels transfer taste; words don't.\n\n"
                f"{img_lines}\n\n"
                "After looking at each image, your approach doc should "
                "explicitly cite WHICH reference's specific moves you're "
                "borrowing (palette discipline, layout rhythm, typography "
                "treatment, etc.) and which you're rejecting. Vague synthesis "
                "is the failure mode — name the visual move and where you saw it.\n"
            )

# Then inject `lean_pack` + `lean_vision_block` at the top of the task f-string.
"""


# ─────────────────────────────────────────────────────────────
# Builder-node injection (inside the existing builder_node body)
# ─────────────────────────────────────────────────────────────
# Add this block to builder_node:

"""
# Lean graph: builder pack (build-craft + asset-strategy + visual refs + taste gate)
lean_pack = ""
if state.get("graph_mode") == "lean":
    lean_pack = load_lean_creative_pack(role="builder")
    if lean_pack:
        print(f"  📚 lean creative pack loaded: {len(lean_pack)//1000}KB (builder)")

# And in the moodboard-loading section:
moodboard_dir = run_dir / "moodboard"
all_moodboard = []
if moodboard_dir.exists():
    for ext in ["*.png", "*.jpg", "*.jpeg"]:
        all_moodboard.extend(moodboard_dir.glob(ext))

# Lean graph: if no per-run moodboard exists, seed with the 5 refero refs
# so the builder actually SEES the design language via the moodboard_images
# vision channel (GPT-5 / Gemini direct API path).
if not all_moodboard and state.get("graph_mode") == "lean":
    refs_img_dir = LEAN_REFS_DIR / "images"
    if refs_img_dir.exists():
        for ext in ["*.png", "*.jpg", "*.jpeg"]:
            all_moodboard.extend(refs_img_dir.glob(ext))
        if all_moodboard:
            print(f"  🖼️  lean: seeded moodboard with {len(all_moodboard)} refero refs")

all_moodboard = sorted(all_moodboard)[:5]
"""


# ─────────────────────────────────────────────────────────────
# CLI flag
# ─────────────────────────────────────────────────────────────
# Add to the argparser:

"""
run_parser.add_argument(
    "--graph", choices=["full", "lean"], default="full",
    help="Which graph to run. 'full' is the existing 10-node graph with "
         "research, asset-gen, QA loop, playability loop, judge polish, and "
         "pairwise rank. 'lean' is the stripped 5-node graph "
         "(scope_contract → designer → approach_gate → builder → human_gate) "
         "that drops QA/playability/judge/pairwise and routes creative "
         "judgment to the loaded skills + the human gate. "
         "Cost: ~$1-2 vs ~$15-20."
)
"""

# And in the main() build_graph dispatch:

"""
graph_mode = getattr(args, "graph", "full")
if graph_mode == "lean":
    print("📐 Using LEAN graph (5 nodes, no QA/playability/judge loops)")
    graph = build_graph_lean()
else:
    graph = build_graph()
"""

# And in initial_state, add:

"""
initial_state = {
    ...
    "graph_mode": graph_mode,
    ...
}
"""
