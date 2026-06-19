---
name: creative-taste-gate
description: How to evaluate creative work honestly. Use when reviewing an approach doc, a built prototype, or comparing multiple concepts side-by-side. Replaces phantom-heuristic QA loops with one human-judgment pass that asks "would an award jury stop?" instead of "does this contain the word 'profit'."
---

# Creative Taste Gate

This is the only QA the creative pipeline actually needs. Replace the QA loop + playability loop + judge polish + pairwise rank with one pass that uses creative judgment instead of regex.

## The two questions

For any creative output (approach doc OR built prototype), answer two questions:

**1. Did this hit the brief?**
- Read the brief's outcome requirements
- For each one, point to where the output delivers it
- Anything missing → flag as a gap, not as "fails"

**2. Would an award jury stop scrolling?**
- Not "is this technically correct"
- Not "does this compile"
- Would a human with taste lean forward, or scroll past?

If "yes" to both → ship.
If "no" to brief compliance → iterate the build, not the concept.
If "no" to taste → iterate the concept, not the build.

These failure modes need different fixes. Don't conflate them.

## Reviewing an approach doc

Check each of the 5 axes (see creative-approach-craft):

| Axis | Strong | Weak |
|---|---|---|
| Palette | 3 hex values, one dominant | "earth tones," "warm + cool" |
| Typography | named typefaces + weights + scale | "modern sans-serif" |
| Technique | named primary move | "interactive animations" |
| Layout | section sequence written out | "modular layout" |
| Voice | sample headline in the register | "confident and bold" |

Also check:
- Hero moment is one specific visual sentence (close-eyes test)
- Approach has explicit "what this is NOT" rejections
- No convergence patterns (see creative-approach-craft for the list)

## Reviewing a built prototype

Open the file in a browser. Look at it like a human first. Then go through the move set (see creative-build-craft) and tally:

**Award-grade:** 6+ moves present, executed well
**Solid:** 3-5 moves, basic execution
**Generic:** 0-2 moves, defaults everywhere

For each move that's missing or weak, name the specific section.

Also check:
- Does the rendered build match the approach doc's hero moment?
- Performance: does it hold 60fps on mid-tier hardware? (Open Activity Monitor)
- Mobile: does 375px viewport actually work, or is it a desktop layout squashed?
- The "Try Again" / reset path: does state actually reset?
- Console: open DevTools, scroll the page, look for errors

## Comparing N concepts

When 2+ concepts are on the table:

1. **Convergence check** — do any two concepts share a dominant axis (palette family, primary technique, layout pattern, voice)?
   - If yes → the convergent one with weaker execution gets killed
   - If yes → flag for the designer that the brief's diversification guidance isn't pulling them apart

2. **Range check** — plot concepts on the brief's chosen axes (e.g., minimal ↔ maximal, editorial ↔ experiential). If they cluster, you got less range than you paid for.

3. **Brief fit ranking** — for each concept, which outcome requirements does it nail vs. fumble? A concept that nails 80% of the brief in a thrilling way beats one that nails 100% of the brief in a boring way.

4. **Pick one and explain why** — verbally. "Concept B wins because the hero moment is the only one that passes the close-eyes test, and concept A's palette already exists on 30 SaaS landing pages."

## What this skill does NOT do

- It does not check "does the page contain the word 'total profit'" or any other brief-specific lexicon
- It does not run a Playwright walker looking for 5 rounds of state progression on a landing page
- It does not auto-patch builds 20 times trying to satisfy phantom heuristics
- It does not need a deterministic pairwise scoring rubric

It does one human-judgment pass with two questions. That's it.

## Anti-patterns in taste gates

- **"This score is 7.2/10"** — fake precision. Use "strong / solid / weak" verbally.
- **"Concept A wins by 3 points"** — pairwise rankings without rationale.
- **Reading the code to evaluate the design** — open the browser. Look at the page. Code is downstream.
- **Fixing it yourself instead of flagging it** — if you're the gate, name what's wrong and route back. Don't silently patch.
- **Hedging** — "it's pretty good but could be better" is not a verdict. "Ship" or "iterate, specifically X" are verdicts.

## The escalation rule

If you flag something for iteration and the iterated version comes back with the same problem, escalate to the human. Don't run a 20-iter polish loop hoping it converges. It won't.

## When to load this skill

- Whenever you're reviewing an approach doc
- Whenever you're reviewing a built prototype
- Whenever you're comparing concepts to pick a winner
- Whenever you're tempted to write a QA/playability check based on string-matching brief keywords (don't — load this instead)
