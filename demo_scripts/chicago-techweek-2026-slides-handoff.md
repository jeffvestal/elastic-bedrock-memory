# Slides Handoff — Chicago Tech Week 2026

**Deck:** https://docs.google.com/presentation/d/1UvBedVZ0tSn-NsB2GcBukrGdWCH0UB6fAVlU44Yv-fQ/edit
**Template:** Elastic official brand template (`1fcpLW-I4WPNvatVx1jNPfFaYPlw6aKahiFfsB7CHcaE`) — NOT the AWS-themed deck used for the original talk
**Slide count:** 10 slides
**Built from:** `demo_scripts/chicago-techweek-2026-condensed-plan.md` run-of-show

---

## Slide Inventory

| # | Object ID | Title | Segment | Budget |
|---|---|---|---|---|
| 1 | g3d80320b934_0_4059 | From Stateless to Stateful: Giving AI Agents Memory | Title/cover | — |
| 2 | g32b87f81189_0_0 | Agenda | Agenda (5 stops) | ~15 sec |
| 3 | g338e106dda4_0_39 | The Amnesia Problem | Hook | 1 min |
| 4 | g3d80320b934_0_812 | Memory-as-a-Service Architecture | Architecture + segue to live-build | 1 min |
| 5 | g3d80320b934_0_3796 | Same Prompt, Four Acts | Demo lead-in (4 cards: Act 1 / Live-Build / Act 2 / Act 3) | ~10 sec, then live |
| 6 | g3d80320b934_0_3362 | What Just Happened | Recap comparison | 1 min |
| 7 | g3d80320b934_0_2343 | Key Design Decisions | Recap bullets | 1.5 min |
| 8 | g3d80320b934_0_1045 | Live vs. Playback | **Vamp slot** — elastic, ~2 min | flex |
| 9 | g3d80320b934_0_2108 | Build This Yourself | CTA steps | 1 min |
| 10 | g32b87f81189_3_36 | Thank you! | Closing | — |

All slides have speaker notes matching `demo_scripts/chicago-techweek-2026-condensed-plan.md` timing. Slide 8's notes flag it explicitly as the flex point — cut first if running long, expand first if running short.

---

## What's Different From the AWS Deck

- **Template:** Elastic's own brand template, not the AWS dark-teal one. Copied via `gws drive files copy` (fileId `1fcpLW-I4WPNvatVx1jNPfFaYPlw6aKahiFfsB7CHcaE`), then populated via `batchUpdate`.
- **No Bedrock/AWS branding anywhere** — title, agenda, architecture slide all reworded to be provider-agnostic ("your AI coding agent... anything that speaks MCP").
- **No FAQ slides** — cut entirely; real Q&A happens after the talk instead of scripted FAQ-as-content.
- **No Kiro branding** — Kiro may still run on screen during the live demo, but isn't named on any slide.
- **Vamp slot is now an explicit slide** (#8, "Live vs. Playback") rather than an unscripted aside — Jeff's Top Gun-style riff from the AWS talk worked live, so this version budgets a deliberate placeholder for it instead of cutting personality.
- **Down from 26 slides to 10** — most of the AWS deck's deep-dive slides (memory taxonomy, Elastic-as-vector-DB, Jina diagram, autonomy/self-improving-agents slide, enterprise-scale slide, both FAQ slides) were cut for time; the condensed talk leans on the live demo, not slides, to carry the content.

---

## Still To Do

- [ ] No custom diagrams/images added yet — architecture slide (#4) and demo lead-in (#5) are text-only for now. Consider a simple architecture diagram if time allows before 2026-07-20.
- [ ] Decide the actual vamp content for slide 8 (Top Gun riff again, or something new for a non-AWS room) and update speaker notes once decided.
- [ ] Proofread slide 4's architecture description length — may want to trim for a single eye-pass at speaking distance.
- [ ] Confirm Elastic brand checklist manually in Slides UI: dominant Elastic Blue + white, accent colors used sparingly, Inter fonts, no full-width teal bars, logo at 100% opacity.

---

## API Pattern Used

```bash
gws drive files copy \
  --params '{"fileId": "1fcpLW-I4WPNvatVx1jNPfFaYPlw6aKahiFfsB7CHcaE", "supportsAllDrives": true, "includeItemsFromAllDrives": true}' \
  --json '{"name": "From Stateless to Stateful - Chicago Tech Week 2026", "parents": ["root"]}'

gws slides presentations batchUpdate \
  --params '{"presentationId": "1UvBedVZ0tSn-NsB2GcBukrGdWCH0UB6fAVlU44Yv-fQ"}' \
  --json "$BODY"
```

Text edits used `deleteText` (`textRange.type: ALL`) + `insertText` targeted by `objectId`, not `replaceAllText` — the template reuses identical placeholder strings ("Title here", "Bullet point 1", "Lorem ipsum...") across many slides we kept, so a deck-wide text-match replace would have corrupted more than one kept slide at once.

Slide reordering used `updateSlidesPosition` — note the API requires the moved slide set to already be in relative presentation order; a single call reordering 10 slides out of their original relative order fails with "slides should be in presentation order, with no duplicates." Did it as 4 sequential single-slide moves instead.
