---
name: creative-build-craft
description: How to build a creative web prototype that doesn't read as "generated." Use during the build phase (raw-dog OR pipeline builder node) — covers the move set that separates award-grade work from generic landing pages, performance constraints, and a build checklist that catches the usual AI failure modes before you ship.
---

# Creative Build Craft

The approach is the contract. The build is the execution. Most builds fail at execution because the model defaults to the simplest path even when the approach asked for something specific.

## The build directive

**Your job is to render the approach doc faithfully, not to reinterpret it.** If the approach says "WebGL fluid sim background," you do not ship CSS gradients with a comment that says "WebGL would be better here." You ship the WebGL or you push back BEFORE building, not after.

If the approach is ambiguous, ask before assuming. If the approach is broken, push back. If the approach is clear, execute it.

## The move set — what separates award work from slop

A flat AI landing page has none of these. A good one has 3-4. An award-grade one has 6+.

1. **Custom cursor** — always with `mix-blend-mode: difference` so it works over light AND dark sections. Inflates on interactive elements. ~25 lines.

2. **Kinetic typography** — words or characters reveal independently with staggered timing. Not "the whole headline fades in" — that's a slideshow. Word-by-word with rotation/translation offsets so each word arrives separately.

3. **Layered atmosphere** — at least 2 layers of texture/motion that aren't UI:
   - Animated grain (SVG filter, NOT a static image)
   - Atmospheric bloom (radial gradient that drifts slowly)
   - Conic-gradient sweep (CSS @property + animation)
   - Subtle parallax on hero elements

4. **Real depth** — actual 3D transforms, not just box-shadows. Card tilt on cursor. Perspective on the parent. `transform-style: preserve-3d`. Use this when the layout has a "showpiece" object (card, product, sneaker, etc.).

5. **A ticker, marquee, or infinite scroll element** — when the brief has tactile/drop/announcement energy. Done right = `animation-play-state: paused` on hover. Done wrong = forgotten to dupe contents and you see the seam.

6. **Hairline dividers as primary structure** — `1px solid rgba(255,255,255,0.12)` everywhere. Not borders. Not shadows. Editorial grids are made of hairlines.

7. **Type scale jumps that break taste** — 11px caps right next to 148px display. Not "h1 → h2 → h3." Extreme contrast. The headline should hurt a little.

8. **One unexpected color move** — acid green ribbon on an otherwise red/cream palette. Hot orange on otherwise dark. The thing that someone notices.

9. **Interactive elements respond within 100ms** — buttons lift, links underline-grow, accordion plus-marks rotate, cards transform on hover. Not "animate everything," but "respond to every interaction."

10. **A final CTA section that feels earned** — full-bleed accent color, diagonal pattern, oversized headline, single button. Not "thanks for reading, sign up below."

## Performance rules (hard constraints)

Violating these = broken builds, no matter how nice the design is.

- **Animate only `transform` and `opacity`.** Never `width`, `height`, `top`, `left`, `margin`, `padding`. These trigger layout.
- **GSAP/timelines/RAF loops MUST be cleaned up on state transitions.** Leaks = jank.
- **Cap device pixel ratio at 1.5x** for any canvas/WebGL. 2x doubles your pixel cost for no visible benefit.
- **Blur/bloom effects render at half resolution.** The blur hides the lower res. Free performance.
- **Throttle ambient effects to 30fps** if they're not responding to input. Interaction layer stays 60fps.
- **Pre-allocate inside render loops.** Don't `new Object()` per frame.
- **Test on a MacBook Air, not the dev machine.** If it's janky there, it ships broken.

## Mobile is its own design, not a shrunk desktop

- Custom cursor: disable below 900px (`body { cursor: auto }`)
- Touch targets: 44px minimum
- Hover states: rebuild as tap states or remove
- 3D tilt: disable (no cursor)
- Type scale: usually needs its own clamp() endpoints, not just smaller
- Marquee speed: slower (smaller screens = less distance)
- Grid layouts: usually want to stack, not just narrow

## CDN deps — keep the list short and safe

Allowed without warning:
- Google Fonts (`https://fonts.googleapis.com`)
- Inline SVG (no fetch)
- Inline base64 images
- CSS gradients / conic-gradient / @property
- Web Audio API (synthesized)
- Canvas 2D, WebGL, WebGPU

Banned in single-file prototypes:
- Custom .woff/.woff2 from arbitrary CDNs (CORS blocks from file://)
- `https://images.unsplash.com` / placeholder.com / picsum (CORS + fragile URLs)
- Tailwind CDN with custom config (defaults are slop)
- Lottie JSON from CDN (fine if inlined)
- React/Three from CDN (fine, but document the version)

## Hard rules that prevent hallucinated bugs

- Never put React hooks at module scope. They MUST be inside a component. Module-scope hooks crash silently in CDN React.
- Always `createRoot()`, never `ReactDOM.render()`. React 18 baseline.
- Test the "Try Again" / reset path. Most state bugs hide there.
- Test every state transition manually OR via a Playwright walker before shipping.
- If using `Math.random()` inside render, wrap in `useMemo` with a stable seed.

## Build checklist — verify before declaring done

- [ ] Does the hero moment from the approach doc render exactly as described?
- [ ] At least 3 layers of motion (ambient / midground / interaction)?
- [ ] At least one moment of expressive typography (not just "big headline")?
- [ ] Custom cursor (desktop) AND it disables on mobile?
- [ ] Every interactive element responds within 100ms?
- [ ] Animations only on `transform` / `opacity`?
- [ ] Cleaned up RAF/GSAP on unmount?
- [ ] Mobile tested at 375px AND 414px?
- [ ] Reset/retry path works?
- [ ] No CORS-blocked external fetches?
- [ ] No `console.error` in the browser console on load?
- [ ] If multi-step: every state renders correctly?
- [ ] File opens cleanly via `open file.html` — no build step required?

## When to load this skill

- Whenever you're building a creative web prototype (raw OR pipeline)
- Whenever you're reviewing a build — use the move set + checklist as the rubric
- Whenever a build feels generic — diagnose against the move set and find what's missing
