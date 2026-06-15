# Slides Handoff — AWS Summit NYC 2026

**Last updated:** 2026-06-15  
**Deck:** `https://docs.google.com/presentation/d/1bJmOPJLSAJhAMu07gV0r00hM-sfx_Eu9kCaTqq8NYZA/edit`  
**Slide count:** 26 slides (as of this session)

---

## What Was Done

### Speaker notes
- All 26 slides have speaker notes matching the slide content
- Previously scrambled notes (from template copy) were corrected

### Images inserted
All content images use this left-column transform:
`scaleX=1.833, scaleY=1.031, translateX=300000, translateY=1800000, unit=EMU`

| Slide | Title | Image file | Notes |
|---|---|---|---|
| 6 | Every AI Agent Starts with Amnesia | slide07_amnesia.png.png | session timeline |
| 11 | Why Elasticsearch for Agent Memory? | slide09_scale.png.png | ES strengths |
| 13 | Memory-as-a-Service Architecture | slide13_arch_v3.png.png | Kiro→MCP→AB→ES flow |
| 14 | Jina Embeddings Power Semantic Recall | slide13_jina_v2.png.png | Jina v5 ingest+search |
| 17 | What Just Happened | slide16_what_happened.png.png | Act1 vs Act2 comparison — image on RIGHT side (Jeff moved it, intentional) |
| 19 | Memory Is a Search Problem… | slide_scale_cost_graph.png.png | cost-vs-context graph |
| 20 | From Recall to Self-Improving Agents | slide_autonomy_loop.png.png | agent loop diagram |
| 23 | Everything You Need to Build This | slide22_repo.png.png | repo file tree |
| 24 | 5-Minute Quickstart | slide23_quickstart.png.png | 7-step quickstart |

### Native shapes (no image)
- **Slide 12** — "Elastic as a Vector Database": 3×2 card grid, ROUND_RECTANGLE, dark fill (#171726), teal borders (#00BCD4). Jeff resized slightly after creation.
- **Slide 16** — "Demo" lead-in: 2×2 card grid, same dark/teal style. Content: Act 1 / Live Build / Act 2 / Act 3. Replaced a white-background image that didn't fit the dark AWS template.

### New slides added
- **Slide 19** — "Memory Is a Search Problem, Not a Context Problem" — replaced the weak old scale slide. Cost-vs-context graph showing flat retrieval cost vs steep context-stuffing cost.
- **Slide 20** — "From Recall to Self-Improving Agents" — new slide on autonomous agents + shared memory store. Speaker notes include conflict-detection answer to pre-empt Q&A.

---

## Current Slide Inventory

| # | Object ID | Title |
|---|---|---|
| 1 | g3eedd9bca2e_1_685 | (title/cover) |
| 2 | g3eedd9bca2e_1_588 | From Stateless to Stateful |
| 3 | g3eedd9bca2e_1_21 | What You'll Walk Away With |
| 4 | g3eedd9bca2e_1_27 | Agenda |
| 5 | g3eedd9bca2e_1_45 | The Amnesia Problem |
| 6 | g3eedd9bca2e_1_49 | Every AI Agent Starts with Amnesia |
| 7 | g3eedd9bca2e_1_55 | The Context Window Trap |
| 8 | g3eedd9bca2e_1_61 | Enterprise Memory at Scale |
| 9 | g3eedd9bca2e_1_67 | Memory-as-a-Service |
| 10 | g3eedd9bca2e_1_71 | Memory Taxonomy |
| 11 | g3eedd9bca2e_1_77 | Why Elasticsearch for Agent Memory? |
| 12 | elastic_vectordb_slide | Elastic as a Vector Database (native shapes) |
| 13 | g3eedd9bca2e_1_83 | Memory-as-a-Service Architecture |
| 14 | g3eedd9bca2e_1_638 | Jina Embeddings Power Semantic Recall |
| 15 | g3eedd9bca2e_1_96 | Let's See It |
| 16 | g3eedd9bca2e_1_689 | Demo (native shapes — 4 act cards) |
| 17 | g3eedd9bca2e_1_647 | What Just Happened |
| 18 | g3eedd9bca2e_1_107 | Key Design Decisions |
| 19 | g3eedd9bca2e_1_113 | Memory Is a Search Problem, Not a Context Problem |
| 20 | autonomy_slide | From Recall to Self-Improving Agents |
| 21 | g3eedd9bca2e_1_119 | Common Questions — Adoption |
| 22 | g3eedd9bca2e_1_125 | Common Questions — Running It |
| 23 | g3eedd9bca2e_1_131 | Build This Yourself |
| 24 | g3eedd9bca2e_1_624 | Everything You Need to Build This |
| 25 | g3eedd9bca2e_1_142 | 5-Minute Quickstart |
| 26 | g3eedd9bca2e_1_152 | (closing/CTA) |

---

## Known Issues / Still To Do

- **Slide 14 image** — Jeff noted it looks similar to slide 12's content (Elastic VDB). May need a fresh Jina-specific diagram. Not yet fixed.
- **Slide 14 image file** is `slide13_jina_v2.png.png` — a Jina embedding flow diagram. Verify it looks correct in the deck.
- All local images are in `slides_images/` in this repo.

---

## API Patterns Used

**gws CLI for all Slides API work:**
```bash
gws slides presentations batchUpdate \
  --params '{"presentationId": "1bJmOPJLSAJhAMu07gV0r00hM-sfx_Eu9kCaTqq8NYZA"}' \
  --json "$BODY"
```

**Image workflow:** nanobana2 → upload to Drive → make public → replaceImage → delete Drive file

**Left-column image transform (ABSOLUTE mode):**
```json
{"scaleX": 1.833, "scaleY": 1.031, "shearX": 0, "shearY": 0,
 "translateX": 300000, "translateY": 1800000, "unit": "EMU"}
```

**Native shape style (dark AWS template):**
- Fill: `{"red": 0.09, "green": 0.09, "blue": 0.15}`
- Border: `{"red": 0.0, "green": 0.737, "blue": 0.831}` (teal), weight 25400 EMU
- Title text: teal, bold
- Body text: `{"red": 0.8, "green": 0.8, "blue": 0.85}` (light gray)
