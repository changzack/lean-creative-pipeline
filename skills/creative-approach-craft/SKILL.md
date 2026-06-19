---
name: creative-approach-craft
description: How to write an approach doc that doesn't read like AI slop. Use when designing a concept BEFORE writing any code — captures 5-axis creative commitments (palette / typography / technique / layout / voice), avoids known convergence patterns, and forces a single specific "hero moment" you can close your eyes and see.
---

# Creative Approach Craft

The approach doc is where 90% of the creative outcome is decided. Code is downstream of the doc. A weak doc cannot be saved by a strong builder.

## The whole point

An approach doc is a contract you make with yourself BEFORE you write code, so you can't drift to the safe middle while building. It is short, specific, and committed. It is not a list of options. It is not a research summary. It is not a moodboard.

## The 5 axes — commit to all of them

Every approach doc commits to a single answer on each axis. "It depends on context" is not an answer.

1. **Palette** — exact hex values. ONE dominant color owns 60%+ of the surface. ONE sharp accent. Optional third for type. No 5-color "safe" palettes. No "earth tones." No "warm + cool." Pick three hexes and write them down.

2. **Typography** — specific typefaces, not categories. "A modern sans" is not a commitment. "Inter at weight 900 for display, weight 400 mono for labels, weight 700 italic for emphasis, extreme scale jump from 11px caps to 148px display" is a commitment. Mix sans + mono OR sans + serif. Never sans + sans.

3. **Primary visual technique** — what is the dominant rendering move? Examples: WebGL fluid sim background, scroll-driven SVG morph, 3D card tilt with conic-gradient holography, kinetic typography with character-level reveals, animated grain + blend-mode atmosphere. Name ONE technique. This is the hero of the build.

4. **Layout pattern** — specific spatial composition. "Split hero with offset card stage on right, full-bleed ticker, four-column stat strip with hairline dividers, single-column manifesto, three-column tier grid with middle pulled forward, marquee, accordion FAQ, hot-color final CTA, hairline footer." Not "modern sectioned layout."

5. **Voice** — how does the copy SOUND? Editorial / street / luxury / brutalist / playful / academic / corporate. Pick one. Write a sample headline in that voice as proof.

## The hero moment test

Add one sentence that describes the single most important visual moment of the build. Specific enough that someone reading it can close their eyes and see it.

✅ "A numbered holographic member card with a conic-gradient sweep that tilts in 3D toward the cursor, sitting offset to the right of a 6-word kinetic headline where the third word is stroke-only."

❌ "A cool hero with motion."

If you cannot write the hero moment in one specific visual sentence, your approach isn't ready.

## Known convergence patterns — flag and avoid

LLMs default to the same handful of looks. If your approach has any of these, push harder:

- **Dark background + gold/red accent + ticker bar** — the universal "edgy editorial" default
- **Purple-to-blue gradient on white** — the 2024 AI cliché
- **Centered hero with subtitle and two pill buttons** — the SaaS default
- **Card grid → features → CTA template** — the template default
- **"Drop announcement" energy** when the brief isn't about drops
- **Grain overlay as the only texture** — grain is fine, but it's not personality
- **Inter at default weight 400** — Inter is the SMPLX font, but only at the extremes
- **Bouncy/elastic easing** — feels dated
- **Gradient text on big headlines** — feels 2023
- **Generic checkmark feature lists** — every SaaS page in history

## The ambition test

Before committing the approach, ask: "If a senior creative director who has shipped award work saw this approach doc, would they say it's ambitious — or would they say it's safe?"

If the answer is "safe," push harder on ONE axis. Usually it's the primary technique (people default to CSS animations) or the typography (people default to Inter 400).

## What the approach doc must contain

1. **One-sentence concept** — what is this? In the voice of the brief.
2. **Palette** — 3 hex values with roles (dominant / accent / neutral). One sentence on rationale.
3. **Typography** — exact typefaces, weights, scale endpoints. One sentence on pairing rationale.
4. **Primary visual technique** — the named move. One sentence on how it serves the brief.
5. **Layout pattern** — section sequence and spatial composition. One paragraph.
6. **Voice** — register + one sample headline.
7. **Hero moment** — the single most-specific visual sentence.
8. **What this is NOT** — 3 bullets naming directions you considered and rejected (forces convergence-avoidance to be explicit).
9. **Outcome compliance** — bullet through every "must achieve" in the brief, naming HOW this approach delivers it.

## Length

The whole doc should be under 600 words. Long approach docs are a tell that the writer hasn't committed yet.

## Anti-patterns in the approach doc itself

- "I could also do X" — commit, don't optionalize
- "Either A or B depending on the mood" — pick one
- "Modern, clean, sophisticated" — these words mean nothing
- "Think Apple meets Stripe with a touch of Linear" — please no
- "Bold and confident" — show it in your sample headline, don't claim it

## Visual references — pixels transfer taste, words don't

This is the single biggest lesson from running the lean pipeline against raw one-shots: **text descriptions of visual design are inert to an LLM.** Telling Claude "deep black canvas with violet accent and oversized pill button" doesn't actually transfer the taste of the page, because the model never saw it. It's like describing a song with adjectives.

Rules:

1. **Always attach the actual image** when citing a visual reference. If you're using Refero, Awwwards, FWA, or any other source — fetch the preview JPG/PNG, save it to disk, and include it as a vision attachment to the designer/builder call. Don't paste the description and stop there.

2. **For raw-dog (no pipeline) work**: when the user gives you a reference URL or screenshot, view it with `vision_analyze` before writing any code. The "see it first" step is not optional — without it you'll produce a generic-grade build no matter how good the prose description is.

3. **For pipeline work**: seed the per-run moodboard directory with real reference images BEFORE the designer/builder runs. The existing `moodboard_images` plumbing already passes vision attachments to GPT-5 and Gemini direct-API builders; the designer (which routes through Hermes for Claude) should be given file paths and explicitly instructed to open them.

4. **Force explicit citation**: prompt the designer to name WHICH reference's specific moves they're borrowing and which they're rejecting. Vague synthesis ("inspired by editorial websites") is the failure mode — name the visual move and where you saw it.

5. **Never ship a creative brief that lists references as URLs only.** If the brief says "think Highsnobiety editorial, not Stripe SaaS" without attaching actual screenshots, that line does almost no work. Either attach the images or drop the line.

The mistake I made in the lean pipeline v3: I wrote 8KB of carefully-described refero references in markdown and injected them into the prompt. Output was identical to the baseline. Then v4 attached the actual JPGs — output started showing the specific visual moves from the refs (split-hero composition, off-white CTA fill, hairline dividers as primary structure).

See `references/refero-starter-references.md` for a known-good starting set of 5 refero references (Atlas Card, Pipe, Pop Manifesto, Riptype, Sequel) — each strong on a different axis (single-accent palette, split-hero composition, color-block sections, hairline grid, off-white CTA) — plus the `curl` commands to fetch the preview JPGs locally for raw-dog builds. Use them as a fallback starter set when refero search is slow or unavailable.

## When to load this skill

- Whenever you're about to design a concept (raw-dog OR pipeline designer node)
- Whenever you're reviewing an approach doc someone else wrote
- Whenever a build feels like it converged on a generic look — re-read the approach, see where it caved
- Whenever you're tempted to describe a visual reference in prose instead of attaching the actual image — load this skill, see the rule above, attach the image
