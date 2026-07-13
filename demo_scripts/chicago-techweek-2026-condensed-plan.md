---
type: plan
title: "Chicago Tech Week 2026 — Condensed Talk Plan"
status: draft
category: content
priority: high
created: 2026-07-13
updated: 2026-07-13
tags: [chicago-techweek-2026, condensed, talk, elastic-bedrock-memory]
---

# Chicago Tech Week 2026 — Condensed Talk Plan

**Event:** Chicago Tech Week meetup, Wednesday 2026-07-20
**Duration:** 25 min (hard budget, leaves slack for a 30 min slot)
**Audience:** Technical, general (not AWS-specific) — mixed devs, similar vibe to AWS Summit crowd but no cloud-vendor assumption
**Source material:** AWS Summit NYC 2026 talk (60 min) — this is a cut-down, not a rewrite

**Working title:** *From Stateless to Stateful: Giving AI Agents Memory* (drop "Bedrock" from the title — it's AWS-specific branding, not relevant here)

---

## Calibration from the actual AWS Summit run

Live, the 60-min-scripted talk actually ran **~52 min** — 8 min short — and that *included* an unscripted 3+ min Top Gun aside (the "gutsy maneuver / getting yelled at" bit used to explain playback-demo vs. live-demo). So:

- Scripted content alone ran **~49 min**, close to the original per-segment estimate (~48 min) — that estimate is a trustworthy baseline, not padded.
- **The live demo segments ran faster than scripted** (Act 1, live-build, Act 2, Act 3) — there's more headroom to compress those than the original plan assumed.
- **Vamping is a feature, not a bug** — Jeff likes to riff (Top Gun aside, etc.) and it worked live. The condensed version should budget an explicit, flexible slot for one short riff rather than eliminate personality entirely.
- Net: this is a **52→25 min cut (~52%)**, not a 60→25 cut — less drastic than first framed, and the demo segments specifically can be tightened harder than v1 of this plan assumed.

---

## Guiding cuts

1. **No AWS/Bedrock framing.** Reframe as "your AI coding agent" generically — provider-agnostic is a better story for a non-AWS audience anyway.
2. **De-emphasize the specific coding agent.** Kiro stays on screen (least rework) but isn't branded/repeated. "My AI coding assistant" in narration, one MCP-portability aside.
3. **Cut the FAQ-as-content segment entirely** — was 6 min of scripted Q&A filling slack in the 60-min slot. Real Q&A after, not simulated Q&A inside the budget.
4. **Fold Act 3 into a single beat** at the tail of Act 2 rather than a standalone segment — the read-back is confirmation, not new information.
5. **Push the live-build and Act 1/Act 2 pacing tighter than v1's estimate** — live timing showed these run faster than scripted once you know the beats cold. Less narration per command, don't wait for full doc-count callouts.
6. **Recap becomes one slide, ~90 seconds** — audience just watched the proof, don't re-litigate it.
7. **Keep one vamp slot, budgeted explicitly (~2 min, elastic)** — this is the one place personality/banter is allowed to breathe. If it runs long, it's the first thing to trim back down live; if the room's flat, it's the first place to add color.
8. **CTA stays but trimmed** — repo link + one line, no blog-specific pitch.

---

## Condensed run-of-show (25 min)

| # | Segment | Medium | Min | Note |
|---|---|---|---|---|
| 1 | Intro + amnesia hook | slides | 2 | tight, no AWS framing |
| 2 | Act 1 — amnesiac agent (refunds built wrong) | live screen | 3 | 2-3 slips is enough, don't force all 3 |
| 3 | Live-build the memory system (indices → agent → tools → load history) | live screen | 4 | live ran faster than scripted; skip mapping deep-dive |
| 4 | Wire memory to the agent (MCP config + restart) | live screen | 1 | two files, say it fast |
| 5 | Act 2 — memory-wired agent (refunds nailed + write new fact) | live screen | 4 | the money-shot segment, protect this one |
| 6 | Act 3, folded — one cross-session read-back beat | live screen | 1 | one question, one answer, no audit-trail tour |
| 7 | Recap (one slide, design decisions as bullets) | slides | 1.5 | don't re-narrate the story |
| 8 | FAQ-as-content | — | 0 | **cut** |
| 9 | **Vamp slot** — one short riff/analogy (Top-Gun-style, your call) | slides or live | 2 | elastic: first thing to trim if running long |
| 10 | CTA / repo link | slides | 1 | no blog pitch |
| — | **Total content** | | **19.5** | |
| — | Buffer / breathing room | | 3.5 | absorbs live-demo variance + vamp overflow |
| — | **Real Q&A** (outside the 25) | | — | not counted in budget |

19.5 scripted + 3.5 buffer = 23, leaving ~2 min of true slack inside the 25-min slot even after accounting for vamp running long. Q&A happens after, not squeezed inside.

---

## What carries over verbatim (don't rewrite)

- Act 1 setup line and the ask prompt (works fine without AWS framing — just drop "checkout service... Bedrock" specifics if any crept into narration)
- The three slips to elicit: float-cents bug, missing Stripe idempotency key, missing auth
- The breaking-point line: *"Every one of those corrections is something my team already decided."*
- The three `setup/*.py` commands and their one-liners
- The Act 2 verbatim-same-prompt beat and the "don't talk over the tool call" instruction
- The `save-knowledge-fact` beat introducing a new policy (90-day / partial-cap)
- The closing line, reworked to drop Bedrock: *"Your inference layer doesn't matter. Elastic handles the memory, the search, and the observability. Wire them together and your agents remember what matters."*

## What gets rewritten

- **Intro/hook (Segment 1):** cut AWS Summit-specific framing ("developers and architects at AWS Summit"). New hook line: *"AI coding agents can read your whole codebase and still have no idea what your team decided last sprint. That's the problem tonight."*
- **Segment 3 narration:** shorter. Skip explaining what ES|QL tools are in detail — say "semantic search tools and a write tool" and move on.
- **Segment 6 (folded Act 3):** instead of a full new-session demo, either (a) do it live but fast — one question, one answer, no Kibana audit-trail tour — or (b) show a screenshot/GIF if time is tight on the day. Decide during rehearsal based on how Segments 1-5 are tracking.
- **Recap (Segment 7):** one slide with 3 bullets max — semantic_text = the pipeline, Agent Builder = the MCP server, decisions compound over time. Don't re-narrate the story.
- **CTA (Segment 9):** *"Repo's public: github.com/jeffvestal/elastic-bedrock-memory. Clone it, run three setup scripts, wire your MCP config, ask your agent about the project. Five minutes if you've got an Elastic Cloud trial."* No blog CTA unless one exists for this audience by then.

---

## Timing risk notes

- **The vamp slot (Segment 9) is the primary lever, not an afterthought** — it's designed to flex. Running hot: cut it to one line or skip it. Running cold / room's with you: let it breathe toward 3-4 min and trim Segment 7 (recap) to compensate.
- Segment 3 (live-build) is the secondary buffer — live timing already showed this goes faster than scripted once rehearsed; if a command lags, skip the doc-count callout, don't stop to explain `semantic_text` mapping.
- Segment 2 (Act 1) only needs ~2 of the 3 slips to land the point; don't force all three if Kiro behaves well.
- If genuinely short on time, Segment 6 (folded Act 3) is the first full cut — Act 2's `save-knowledge-fact` beat already proves write-and-persist.

---

## Slide deck

Built — Elastic-branded (not AWS), 10 slides, matches the run-of-show above. See `demo_scripts/chicago-techweek-2026-slides-handoff.md` for the slide inventory, notes, and what's still open.

Deck: https://docs.google.com/presentation/d/1UvBedVZ0tSn-NsB2GcBukrGdWCH0UB6fAVlU44Yv-fQ/edit

---

## Open items before Wednesday

- [ ] Rehearse condensed version once out loud, timed against the real baseline (52 min actual, not the 60 min script) — verify the vamp slot and tightened demo segments land at ~23 min before real Q&A
- [ ] Pick the vamp bit for this crowd — Top Gun riff can stay if it still lands for a non-AWS audience, or swap for something else; keep it to ~2 min as scripted, not the 3+ min it ran live
- [ ] Decide live vs. pre-recorded for the folded Act 3 beat (Segment 6) based on rehearsal timing
- [ ] Update slide deck: drop AWS-branded slides, cut FAQ slides, condense recap to 1 slide, update title slide (drop "Bedrock" if title changes)
- [ ] Scrub narration notes/run-book for "Bedrock"/"AWS"-specific lines before using on stage
