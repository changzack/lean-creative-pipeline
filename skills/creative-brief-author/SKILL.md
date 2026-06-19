---
name: creative-brief-author
description: How to write a creative brief that doesn't doom the run. Use BEFORE kicking off any creative work — the brief defines whether designers can hit it. Covers the 8-section structure, what to make non-negotiable vs. open, how to write outcome requirements (not tool requirements), and how to write diversification guidance that actually produces divergent concepts.
---

# Creative Brief Author

A bad brief produces bad output no matter how good the designer is. A great brief makes mediocre designers ship strong work. The brief is the single highest-leverage artifact in the creative pipeline.

## The 8 sections

Every brief has exactly these 8 sections. No more, no less. Renaming them is fine; reordering is fine; skipping them isn't.

### 1. Outcome / Goal (1-3 sentences)

What does success look like for the END USER? What are they feeling at the end?

✅ "A 60-second pizza slicing game where the player feels the small joy of a clean cut and gets an honest 0-1000 score on how close to a perfect half they came."

❌ "Build a pizza game."

The test: if you handed this to two different designers, would they both know what "done" looks like?

### 2. Target Audience (2-4 sentences)

Who is this for? What's their context? What do they already know? Demographic + psychographic + situational.

This shapes voice, density, technical complexity, and tone. A page for Complex readers is not a page for enterprise IT buyers, and the brief has to say so.

### 3. Required Deliverables (numbered list, concrete artifacts)

Every item is a CONCRETE artifact. Maps directly to what the build must contain.

✅
1. Single self-contained `index.html` file
2. Top-down view of a pizza with crust, cheese, sauce, and at least one identifiable topping
3. Drag-to-slice interaction with visible cut line
4. Score 0-1000 based on circular-segment area math
5. Italian-feeling background music (synthesized, mute toggle required)
6. Score reveal screen after the cut
7. "Slice Again" reset
8. Touch + mouse support

❌
1. Make it fun
2. Add Italian vibe
3. Score the player

Each deliverable should be testable: you can look at the build and say "yes that's there" or "no it isn't."

### 4. Taste Constraints & Anti-Patterns (do / don't lists)

**Do** = things that PRESERVE the brief's spirit. Specific, not vague.
**Don't** = the failure modes you've seen before. Specific, not vague.

✅ Do: "Make the pizza look hand-crafted — gradients, irregular topping placement, char spots on the crust."
✅ Don't: "Don't render the pizza as a flat orange disc with emoji toppings."

❌ Do: "Make it look good."
❌ Don't: "Don't make it look bad."

Cite known convergence patterns to avoid (see creative-approach-craft). Cite previous run failures by reference.

### 5. Outcome Requirements (MUST ACHIEVE / MUST NOT)

This is the hard quality bar. Frame as OUTCOMES, not TOOLS.

✅ "Background atmosphere must visibly react to game state in real-time."
❌ "Must use Three.js with UnrealBloomPass."

The designer picks the technique. The brief specifies the experience.

Always include a technical floor:
- "Must include at least one effect that requires GPU-accelerated rendering (WebGL/WebGPU/shader)" — prevents regression to CSS-only safe defaults
- "Holds 60fps on integrated GPU"
- "Animations on transform/opacity only"

### 6. Look & Feel References (optional)

URLs, file paths to moodboards, named design systems, or named brands ("think Highsnobiety editorial, not Stripe SaaS").

Optional but powerful. Empty is fine. Vague is harmful — "modern and clean" is worse than nothing.

### 7. Diversification Guidance (only if running parallel designers)

When the pipeline fans out to 3+ designers, this section tells them which AXES to diverge on. Not what answer to land on — what direction to explore.

✅ "Three designers, three distinct VISUAL REGISTERS — all hitting the same brief, but:
- One **editorial / magazine** — refined typography, restrained palette, feels like a print page
- One **street / hype** — high contrast, bold accents, ticker bars, sticker-collage energy
- One **luxury / atmospheric** — dark, slow, gold/cream, atmospheric blur"

❌ "Three designers should explore different directions."

The test: if you read the guidance, do you know which axis each designer should own?

### 8. Sample Data (only if the artifact needs real content)

If the build needs real text/data (tier prices, quiz questions, copy), provide it VERBATIM in a fenced code block. Builders use this exact content to avoid drift and invention.

```
TIER 1 — Regular ($0/mo)
  - Full access to Complex.com, always free
  - ...

TIER 2 — Obsessed ($9/mo)
  - ...
```

If the brief doesn't need real content (a generic showpiece), skip this section.

## Outcome vs. Tool — the most common brief mistake

The brief specifies WHAT, the approach specifies HOW.

| ❌ Tool requirement | ✅ Outcome requirement |
|---|---|
| "Must use GSAP" | "Headline must reveal word-by-word with staggered timing" |
| "Use a serif font" | "Typography must feel editorial and printed, not screen-native" |
| "Three.js scene in the background" | "Background must have real depth and react to scroll position" |
| "Custom cursor" | "Interactive elements must respond within 100ms with a non-default cursor treatment" |

Tool requirements cap the ceiling. The designer might invent something better with a technique you didn't anticipate. Specify the experience, let the designer pick the technique.

## The "non-multistep" rule

If the artifact is NOT a multi-step experience (no rounds, no quiz questions, no game progression — it's a landing page or share card or static showpiece), say so EXPLICITLY in the brief:

> "This is a single-screen artifact. There is no progression, no rounds, no end-state."

This tells the pipeline's playability gate to skip. Without this, the gate hunts for state progression that doesn't exist and burns budget on phantom errors.

## The "diversification" warning

Three parallel designers will converge to the same look unless you give them axes to diverge on. The convergence default is:

- Dark background + ticker + grain + red accent + bold display sans
- 3-column tier grid with middle tier "MOST WANTED"
- Generic "obsessed-fan" copy register

If you don't want this, your diversification section must name the axis you want them to split on (palette family / primary technique / tone / spatial composition). And only diversify when you need range — for many briefs, you only want ONE strong direction, not three takes.

## Brief length

Most briefs should be 400-1000 words. Under 200 = under-specified. Over 1500 = you're pre-designing the solution.

If you find yourself writing "and the headline should be 96px Inter weight 900 in hot red," stop. That's the approach doc's job, not the brief's.

## Validation before launching

Before kicking off a pipeline run or raw-dog build:

- [ ] Outcome section: would two designers know what "done" looks like?
- [ ] Audience: specific enough to shape voice?
- [ ] Deliverables: each item testable in a built page?
- [ ] Taste constraints: cite specific anti-patterns, not vague ones?
- [ ] Requirements: outcome-framed, not tool-framed?
- [ ] Technical floor present (60fps / GPU rendering / no layout animations)?
- [ ] Multi-step vs. static called out explicitly?
- [ ] Diversification guidance: names the axes (only if running parallel designers)?
- [ ] Sample data provided verbatim if needed?

If any answer is no, fix the brief before spending money on a run.

## When to load this skill

- Whenever you're writing a creative brief for raw-dog OR pipeline
- Whenever you're about to spend >$5 on a creative run — re-validate the brief first
- Whenever a previous run produced disappointing output — review the brief, not the designer
