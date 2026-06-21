---
name: creative-asset-strategy
description: How to decide whether a build needs generated images at all, how to integrate visual references into prompts so they actually transfer taste (vision attachments, not text), and how to ship builds that aren't 42MB. Replaces the pipeline's asset-gen-then-bloat pattern.
---

# Creative Asset Strategy

The default move of generating 8 raster assets and inlining them as base64 produces 42MB HTML files where 7 of 8 assets are unused. Stop doing that.

## The most important lesson: visual references must be PIXELS, not text

## Host the asset, don't inline it (lean-graph rule, 2026-06-19, multi-asset update 2026-06-19)

The full-graph pattern was: generate image → base64-encode → glue into HTML as a `data:image/jpeg;base64,...` URI. That made HTML files 30-40MB, killed first paint, and prevented browser caching. The reason was historical — the full graph's QA walker opened builds via `file://` where remote `<img src="https://...">` tags fail CORS.

The lean graph doesn't open builds from `file://`. We deploy to GitHub Pages. So the inline workaround is gone:

1. Generate up to 5 assets via fal.ai (mix of images + 1 video loop max).
2. Push each one to `changzack/prototypes/_assets/<run-name>/concept-N/` (same repo as deploys).
3. Builder writes `<img src="https://changzack.github.io/prototypes/_assets/<run>/concept-N/<slug>.jpg">` or `<video src=".../<slug>.mp4" autoplay muted loop playsinline>` directly.
4. HTML stays under 100KB. Assets cache forever in the browser.

The `lean_asset_gen_node` in `pipeline.py` does this automatically when `--graph lean` is used and `FAL_KEY` is set. Per-concept caps: 5 assets max, $2.00 budget hard cap, soft warn at $1.00.

## Multi-asset playbook for landing pages (lean graph)

A strong landing page typically uses 3-5 assets across 2-3 categories, not 1 hero and not 8 raster blobs. Pick the combo that matches the concept:

**Editorial / magazine direction**
- 1 hero photo (large, photoreal, restrained framing)
- 1 paper-or-grain texture as section overlay (mix-blend-mode: multiply)
- 1-2 graphic marks (issue number, stamp, hairline divider, foil seal)
- Optional: 1 illustration if the concept is editorial-illustrated

**Luxury / atmospheric direction**
- 1 render-3d of the central object (membership card, product, package)
- 1 video-loop for hero atmosphere (slow camera, moody lighting, NO speech / NO text)
- 1 gold/foil graphic seal
- 1 atmospheric texture overlay (light leak, bokeh, smoke)

**Street / hype / drop direction**
- 2-3 product/photo shots (hero + 2 secondary, different angles)
- 1 distress texture / grain / sticker-collage atmosphere
- 1 graphic mark (numbered badge, "DROP" stamp, ticker glyph)
- Optional: 1 video-loop for ticker / marquee background

**Pure-CSS direction (legitimately empty manifest)**
- Typography-led concepts where the wow moment is type contrast, kinetic letterforms, or pure geometric composition.
- Generative concepts where canvas/WebGL is the art.
- Leave the ASSET MANIFEST empty. The lean graph respects this and skips the node. The builder gets nothing to embed and uses CSS/SVG/canvas for everything.

## Asset type → fal model routing (lean)

| Type | fal model | Cost | Use for |
|---|---|---|---|
| `texture` | flux/schnell | $0.003 | grain, paper, foil, distress overlays |
| `atmosphere` | flux-2-pro | $0.03 | light leaks, bokeh, smoke, moody backgrounds |
| `product` / `photo` | flux-2-pro | $0.03 | hero shots, secondary product photos |
| `render-3d` | flux-2-pro + 3D prompt suffix | $0.03 | photoreal 3D-look renders of cards/objects |
| `graphic` | recraft-v3 | $0.06 | badges, stamps, numbered marks, text-bearing graphics |
| `illustration` | nano-banana-2 | $0.08 | painted/illustrated editorial art |
| `video-loop` | kling-video v1.6 standard | $0.35 | 5s ambient mp4 loop, autoplay/muted/loop |

`render-3d` is the same model as `product` — the difference is the prompt suffix the pipeline appends: "photoreal 3D render, octane render, cinematic studio lighting, soft shadows, depth of field, premium product visualization." That suffix reliably shifts flux-2-pro toward a 3D-look output without a separate model.

Video-loops have a HARD per-concept cap of 1 (designer enforced) because they burn the budget — at $0.35 each, two videos already eats 35% of the $2.00 cap.

**Gotcha when wiring this in: the file:// QA walker also pushed a "no external image URLs" CORS ban into the builder's HARD ASSET CONSTRAINT block.** That ban is obsolete too — strip it (or branch on `graph_mode == "lean"`) or the builder will refuse to use the hosted URL you just generated. See `references/orphaned-workarounds-checklist.md` for the general pattern of auditing what gets orphaned when you delete a pipeline node.

**Verified end-to-end 2026-06-19** on the Complex Allegiance brief, lean graph + hosted assets: 3 concepts, builds 28KB / 46KB / 33KB (vs. full graph's 4MB / 36MB / 42MB on a similar brief), total run cost $1.17 including $0.06 in fal.ai calls. One designer (street/hype direction) correctly opted out of any commissioned asset and drew everything in CSS/SVG — the gating-on-empty-ASSET-MANIFEST rule worked. The two designers who commissioned a hero card got it hosted at a stable URL and embedded with a plain `<img src>` tag. See `references/lean-asset-hosting-on-github-pages.md` for the concrete integration recipe, helper functions to reuse, and the verification ritual (curl-for-200 after push).

Text descriptions of design are inert to an LLM. Telling Claude "deep black canvas with violet accent and oversized pill button" doesn't transfer the taste of the page, because the model never saw it. It's like describing a song with adjectives.

**If you want a visual reference to actually influence output, the model has to SEE the image.** This means:

- For Claude/Hermes-routed designers and builders: provide image file paths in the prompt + instruct the agent to use Read/View tools on each before designing. Hermes can read images.
- For GPT-5 / Gemini / direct-API calls: attach the images as proper multimodal vision input via the existing `moodboard_images` channel.
- For Refero-style reference databases: fetch the preview JPG to disk, then route it through the same vision attachment pipe as user-supplied moodboards. The `description` field is scaffolding context only — never the primary signal.

Verified 2026-06-19 on the Complex Allegiance brief: v3 had text descriptions of 5 refero references → output indistinguishable from no-reference baseline. v4 had the same 5 refs as actual JPG vision attachments → "way better" per CD. Same brief, same skills, only difference was pixels vs words.

When in doubt: pixels.

## The decision tree (whether to generate assets at all)

Before generating ANY raster asset, ask:

```
Does the build need a photographic / illustrative visual element?
├── NO → Use canvas / SVG / CSS gradients / inline shapes. STOP. No asset gen.
└── YES → Continue.

Can it be drawn procedurally (sneaker silhouette as clip-path, pizza as canvas, etc.)?
├── YES → Procedural. Lower file size, infinite variation, the build owns its look.
└── NO → Continue.

Is it a hero showpiece (1 image carrying the build's whole visual identity)?
├── YES → Generate ONE image, max 1.5MB after compression. Inline as base64 OR reference via asset://.
└── NO → It's chrome. Use SVG / CSS / emoji. Don't generate.
```

**95% of creative builds need 0-1 generated assets.** The pipeline's "commission 8 assets" default is wrong for almost every brief.

## What canvas/SVG/CSS can actually do

Most "needs an image" instincts are wrong. The following are all native-renderable, no asset needed:

- **Sneaker silhouette** → `clip-path: polygon(...)` on a colored div
- **Pizza** → canvas with arc + radial gradients + procedural pepperoni placement
- **Member card** → CSS gradient + conic-gradient holography + 3D transform
- **Sticker / badge / stamp** → SVG circle + text + rotation + drop-shadow
- **Newspaper / zine texture** → SVG turbulence filter at 0.55 opacity, mix-blend-mode overlay
- **Abstract product silhouettes** → clip-path polygons on gradient backgrounds
- **Pattern / repeat textures** → repeating-linear-gradient
- **Atmospheric bloom** → radial-gradient + filter: blur(60px)
- **Animated grain** → SVG filter feTurbulence + animation: translate steps
- **Sketchy / hand-drawn lines** → SVG path with stroke-dasharray animation
- **Charts / data viz** → SVG / canvas, never raster
- **Icons** → SVG or unicode glyphs, never raster

If your instinct is "this needs a generated image," check this list first.

## When generated assets actually help

Some things genuinely benefit from raster:

- **Hero product photography** (sneaker, perfume bottle, food) where the brand value is the visual fidelity
- **Editorial photography mood** (faces, scenes, atmospheres) that you can't fake
- **Texture maps** for 3D scenes (rare in single-file prototypes)
- **Pattern/background art** that's too organic for SVG (chaotic painterly textures)

In all of these cases: ONE asset. Maybe two. Not eight.

## The asset budget rule

Set an asset budget BEFORE generating anything:

| Build type | Budget |
|---|---|
| Landing page (typography-led) | 0 assets |
| Landing page (product-led) | 1 hero image, max |
| Multi-step experience | 0-2 assets, total |
| Game / interactive toy | 0 assets — draw it |
| Editorial feature with photo essay | 3-5 assets, intentional |
| Pure showpiece (single hero scene) | 1-3 assets |

When the budget is 0-1, don't even commission assets. Skip the node entirely.

## Asset integration — the hard part

The pipeline's failure mode: builder gets `asset://hero-pizza-toppings` as a string, has never seen the image, doesn't know its composition or color, glues it in as `<img>` without composing around it. Result: a sticker on a layout that doesn't know it's there.

Fix:

1. **Generate assets BEFORE the builder runs**, not in parallel.
2. **Feed the actual rendered image into the builder's context** as a vision attachment, not just a slug name. The builder must SEE the asset to compose around it.
3. **The builder writes the build with the image already loaded**, so it can mirror the asset's palette, scale to its dimensions, and place it where the composition wants it.

In Hermes / Claude builds: attach the image as a vision input in the user message. In direct API: same. In the pipeline: route through the moodboard_images plumbing that already exists for inspiration refs — generated assets are just another moodboard image.

## Asset pruning — never inline what you don't use

After the build is written:

1. Scan the final HTML for `asset://` references that survived.
2. Drop unused asset slugs from the base64 inline list.
3. A build that referenced 1 of 8 assets ships with 1 inlined asset, not 8.

This single step takes a 42MB build to ~6MB. It's a 50-line post-processor.

## File-size targets

| Build size | What's reasonable | What's broken |
|---|---|---|
| Pure typographic landing (no raster) | 20-80KB | >200KB = bloat |
| Landing with 1 hero image | 500KB - 2MB | >5MB = uncompressed |
| Showpiece with 2-3 hero images | 2-6MB | >10MB = asset-bloat |
| Multi-step game with 4-6 assets | 4-8MB | >15MB = pipeline default failure mode |

If a single-page build is >10MB, something is wrong. Almost always it's unused inlined assets.

## Compression hygiene

- PNG → WebP (`cwebp` or fal can return WebP directly)
- Cap dimensions: hero images at 1600px wide, not 4096px
- Quality 80-85 is indistinguishable from 95 visually but ~40% smaller
- Inline as base64 only when needed for offline/file:// portability — otherwise use asset:// + post-processor

## The "describe the asset, don't generate" pattern

When the brief says "needs a hero image," sometimes the right move is:

> Generate the image conceptually in the build itself, using procedural primitives. A "sneaker drop" hero doesn't need a photorealistic sneaker — it can be a clip-path silhouette on a gradient with kinetic typography over it. The IDEA of a sneaker hits harder than the photo of one in many cases.

This is especially true for street/editorial briefs where the visual language values graphic restraint over photorealism.

## When to load this skill

- BEFORE deciding to commission generated assets for a build
- Whenever a build's output is >5MB and you don't know why
- Whenever the brief says "needs an image" and you're about to default to fal.ai
- Whenever the build feels like assets were glued on instead of composed in
