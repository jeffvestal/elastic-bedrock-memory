# fslides Design System — Style Guide

Chicago Tech Week 2026 · "From Stateless to Stateful"

This guide is the single source of truth for building new slides. Read it once, build a slide in under ten minutes.

---

## 1. Design Philosophy

This deck uses a **postmodern brutalist** aesthetic. The rules are not arbitrary — every choice reinforces the "exposed infrastructure" metaphor that mirrors the talk's theme (agents that know how they're built).

**Core principles:**

- **Hard shadows, no blur.** Shadows are solid offsets (`6px 6px 0px #111`), never blurred. Blur implies polish; hard shadows imply structure.
- **Exposed framework labels.** UI scaffolding is made visible: `[ ACT_01 ]`, `SECTION_02`, `[ TYPE_03 ]`. Labeling the frame is intentional, not careless.
- **Memphis dot-grid texture.** Every slide has a subtle radial dot pattern (`opacity: 0.06`) baked into `.slide::before`. You get it for free. Do not suppress it.
- **Yellow + black as the power move.** `--yellow` (#FEC514) is reserved for emphasis and hierarchy breaks. A full yellow-fill card or callout bar is a statement — use it once per slide, not three times.
- **Zero gradients. Zero glows.** Flat fills only. If you find yourself writing `background: linear-gradient` or `box-shadow: 0 0 20px`, stop.

---

## 2. Color Tokens

All tokens are defined in `slides/shared.css` under `:root`. Always use the CSS variable, never a raw hex value in slide HTML.

| Token | Value | When to use |
|---|---|---|
| `--black` | `#111111` | Primary text, borders, hard shadows, `.bg-black` slides |
| `--white` | `#FFFFFF` | Card fills on dark slides, reversed text |
| `--cream` | `#F4F0E8` | Default slide background (`.slide` base) |
| `--yellow` | `#FEC514` | Primary accent — one dominant use per slide |
| `--poppy` | `#FF6B47` | Secondary accent for warnings or contrast beats |
| `--teal` | `#00BFA5` | Tertiary accent, data/success states |
| `--blue` | `#0B64DD` | Links, technical identifiers |
| `--shadow` | `6px 6px 0px var(--black)` | Standard hard shadow |
| `--shadow-yellow` | `6px 6px 0px var(--yellow)` | Shadow on dark-fill boxes |
| `--shadow-sm` | `3px 3px 0px var(--black)` | Small hard shadow for cards, pills |

**Yellow economy:** Each slide should contain at most one element that uses `--yellow` as a fill color. A `callout-bar`, a highlighted card, or a `.pill.fill-yellow` — pick one. If everything is yellow, nothing is.

---

## 3. Typography

Two fonts only. Loaded from Google Fonts in `shared.css`.

### Inter (primary)

The workhorse. Use for all body copy, headings, and UI text.

| Element | Size | Weight | Notes |
|---|---|---|---|
| `h1` | 72px | 900 | `letter-spacing: -0.035em`, `line-height: 0.96` |
| `h1.outline` | 72px | 900 | `color: transparent`, `-webkit-text-stroke: 3px` |
| `h2` | 40px | 800 | `letter-spacing: -0.025em`, `line-height: 1.1` |
| `h3` | 18px | 800 | `text-transform: uppercase`, `letter-spacing: -0.01em` |
| `p.body` | 19px | 400 | `line-height: 1.6`, `max-width: 860px` |
| Card body text | 13.5–15px | 400 | `line-height: 1.5–1.6` |

**`h1 .accent`:** Wrap a word in `<span class="accent">` to color it `--yellow`. On `bg-black` slides it stays yellow. On `bg-yellow` slides it becomes outlined black.

### Space Mono (structural / framework)

Reserved for anything that signals "machine" or "exposed system": meta labels, eyebrows, pills, monospaced callouts, footer text, large numbered indices.

| Element | Size | Weight | Letter-spacing |
|---|---|---|---|
| `.meta-label` | 10px | 700 | 0.22em |
| `.eyebrow` | 11px | 700 | 0.22em |
| `.pill` text | 11px | 700 | 0.16em |
| `.footer span` | 10px | 400 | 0.18em |
| `.vert-label` | 10px | 400 | 0.2em |
| Agenda numbers | 72px | 700 | -0.04em |

**Rule:** If it's human-readable prose, use Inter. If it's a label, an identifier, a code fragment, or a numeric counter, use Space Mono.

---

## 4. Component Patterns

### 4.1 Section Header Slide (bg-black)

Used to introduce each act. Always `bg-black`. Vertical yellow accent bar on the left, large `h1` centered vertically, `[ ACT_NN ]` eyebrow above.

```html
<div class="slide bg-black">

  <!-- Yellow vertical accent bar -->
  <div class="yellow-rect reveal d1" style="
    position: absolute;
    width: 6px; height: 120px;
    background: var(--yellow);
    top: 50%; left: 64px;
    transform: translateY(-50%);
  "></div>

  <!-- Content block -->
  <div style="
    position: absolute;
    top: 50%; left: 108px;
    transform: translateY(-50%);
  ">
    <div class="eyebrow reveal d2" style="color: var(--yellow); opacity: 1; margin-bottom: 20px;">
      [ ACT_02 ]
    </div>
    <h1 class="reveal d3">Section<br>Title Here</h1>
    <div class="reveal d4" style="
      font-family: 'Space Mono', monospace;
      font-size: 13px;
      letter-spacing: 0.2em;
      text-transform: uppercase;
      color: rgba(255,255,255,0.4);
      margin-top: 28px;
    ">Subtitle or kicker line</div>
  </div>

  <!-- Decorative circles (optional) -->
  <div style="
    position: absolute;
    width: 320px; height: 320px;
    border-radius: 50%;
    border: 2.5px solid rgba(255,255,255,0.12);
    bottom: -80px; right: 80px;
  " class="reveal d2"></div>

  <!-- Exposed label, top right -->
  <div style="position: absolute; top: 40px; right: 64px;">
    <span class="meta-label reveal d1">SECTION_NN</span>
  </div>

</div>
```

### 4.2 Content Slide Structure

Standard content slide on `--cream` background. Absolute positioning for header + body zones.

```html
<div class="slide">

  <!-- Header zone: eyebrow + h2, top-left; meta-label top-right -->
  <span class="eyebrow reveal d1" style="
    position: absolute; top: 32px; left: 64px;
    opacity: 0.4;
  ">[ SECTION_NN ] — Slide Context</span>

  <span class="meta-label reveal d1" style="
    position: absolute; top: 32px; right: 64px;
  ">SLIDE_LABEL</span>

  <div style="position: absolute; top: 72px; left: 64px; right: 64px;">
    <h2 class="reveal d2">Slide Title</h2>
  </div>

  <!-- Body zone: starts ~168px from top -->
  <div style="position: absolute; top: 168px; left: 64px; right: 64px; bottom: 80px;">
    <!-- content here -->
  </div>

  <!-- Footer always last -->
  <footer class="footer">
    <span>Jeff Vestal · Elastic</span>
    <span>Chicago Tech Week 2026</span>
  </footer>

</div>
```

**Standard padding:** `left: 64px`, `right: 64px`. Top of header eyebrow: `32px`. Top of h2: `72px`. Body starts: `~168px`. Footer clears at `bottom: 28px` with `padding-top: 10px` inside.

### 4.3 .card and .card.fill-yellow

The base card is white-fill, 2px black border, small hard shadow.

```html
<!-- Default card -->
<div class="card reveal d3">
  <h3>Card Title</h3>
  <p>Supporting detail text at 13.5px, line-height 1.5.</p>
</div>

<!-- Yellow highlight card (one per grid max) -->
<div class="card fill-yellow reveal d2">
  <h3>Highlighted Card</h3>
  <p>Yellow fill, shadow stays black (4px 4px 0 var(--black)).</p>
</div>
```

Cards live inside `.card-grid`. See Section 5 for grid layout.

### 4.4 .callout-bar

A full-width bottom-of-slide summary bar. Black background, yellow text for labels, white for prose. Always placed just above the footer.

```html
<div class="callout-bar reveal d5" style="
  border: 2.5px solid var(--black);
  box-shadow: 5px 5px 0 var(--black);
  background: var(--black);
  color: var(--yellow);
  padding: 13px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
">
  <span style="
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    opacity: 0.5;
    white-space: nowrap;
  ">Verdict</span>

  <div style="width: 1px; height: 16px; background: rgba(254,197,20,0.3); flex-shrink: 0;"></div>

  <p style="font-size: 16px; font-weight: 700; line-height: 1.35; color: var(--white);">
    Key takeaway sentence. Use <em style="color: var(--yellow); font-style: normal;">yellow inline</em> to stress the crux.
  </p>
</div>
```

The `.callout-bar` class in `shared.css` (on the agenda slide) uses the same visual treatment but without the border/shadow wrapper — match the specific slide's existing declaration or use inline styles to be explicit.

### 4.5 .hard-box

Heavier than a card. Used for standalone sticker-like elements — speaker bio box, prominent solo stat, single highlighted idea.

```html
<!-- Default hard-box -->
<div class="hard-box reveal d3">
  <p>Important isolated content.</p>
</div>

<!-- Yellow fill -->
<div class="hard-box fill-yellow reveal d3">
  <p>Power-move accent.</p>
</div>

<!-- Black fill (shadow becomes yellow) -->
<div class="hard-box fill-black reveal d3">
  <p style="color: var(--white);">Inverted sticker.</p>
</div>

<!-- Cream fill (slightly warmer than white) -->
<div class="hard-box fill-cream reveal d3">
  <p>Softer variant.</p>
</div>
```

All `.hard-box` variants: `border: 2.5px solid var(--black)`, `border-radius: 0` (no rounding — ever), `padding: 20px 24px`.

### 4.6 .pill

Inline badge/tag. Use for technology labels, status tags, or category markers. Always Space Mono uppercase.

```html
<!-- Default pill -->
<span class="pill reveal d2">Elasticsearch</span>

<!-- Yellow fill pill -->
<span class="pill fill-yellow reveal d2">Live Demo</span>

<!-- Black fill pill -->
<span class="pill fill-black reveal d2">New</span>

<!-- Inline in a tag-row -->
<div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;" class="reveal d3">
  <span class="pill fill-yellow">Elasticsearch</span>
  <span class="pill">Agent Builder</span>
  <span class="pill">Semantic Search</span>
</div>
```

### 4.7 .meta-label and [ EXPOSED_LABEL ] Convention

The `[ BRACKET_LABEL ]` convention is the deck's signature postmodern move. It makes structural metadata visible — section numbers, act counters, type identifiers — as if you are showing the audience the slide's own scaffolding.

```html
<!-- Top-right meta label (most common) -->
<span class="meta-label" style="position: absolute; top: 32px; right: 64px;">
  SLIDE_TYPE
</span>

<!-- Eyebrow label (top-left, before h2) -->
<div class="eyebrow" style="opacity: 0.4; margin-bottom: 6px;">
  [ SECTION_02 ] — Context
</div>

<!-- Inside a card as a type marker -->
<div class="tax-card-meta">[ TYPE_01 ]</div>

<!-- Vertical edge label -->
<span class="vert-label" style="position: absolute; left: 20px; top: 50%; transform: translateY(-50%);">
  [ TALK_01 · CHICAGO TECH WEEK 2026 ]
</span>
```

**Convention for bracket labels:**
- Uppercase, underscores for spaces: `ACT_01`, `SECTION_02`, `TYPE_03`, `PROBLEM_01`
- Include a human readable suffix after ` — ` when used as eyebrow: `[ ACT_01 ] — The Problem`
- `meta-label` opacity is `0.35` by default (set in `shared.css`)
- `eyebrow` opacity is `0.4–0.5` when used as a secondary label; `opacity: 1` only when it's yellow on `bg-black`

### 4.8 .footer

Always the last element inside `.slide`. Position is absolute.

```html
<footer class="footer">
  <span>Jeff Vestal · Elastic</span>
  <span>Chicago Tech Week 2026</span>
</footer>
```

`shared.css` handles positioning (`bottom: 28px`, `left/right: 64px`), the top border, and Space Mono styling. Do not override these. On `bg-black` slides the border-top becomes `rgba(255,255,255,0.2)` automatically via `.bg-black .footer`.

---

## 5. Layout Patterns

The slide canvas is always **1280 x 720px**, `overflow: hidden`. Prefer absolute positioning over flex/grid on the slide root — it makes z-stacking and decorative geometry predictable.

### 5.1 Two-Zone Split (title / section splash)

Left content zone + right panel. The right panel is typically `bg-black` or a solid color.

```html
<div style="position: absolute; inset: 0; display: grid; grid-template-columns: 1fr 420px;">
  <div style="display: flex; flex-direction: column; justify-content: center; padding: 72px 64px 72px 72px; gap: 28px;">
    <!-- left content -->
  </div>
  <div style="background: var(--black); position: relative; overflow: hidden;">
    <!-- right panel: geometry, rotated text, accent block -->
  </div>
</div>
```

Right panel width is typically 380–460px. Narrower for supporting panels, wider if it carries content.

### 5.2 card-grid cols-2

Two equal columns. Good for before/after comparisons, two-option decisions.

```html
<div class="card-grid cols-2" style="position: absolute; top: 168px; left: 64px; right: 64px;">
  <div class="card reveal d2">...</div>
  <div class="card fill-yellow reveal d3">...</div>
</div>
```

### 5.3 card-grid cols-3

Three equal columns. Standard for taxonomy slides (Episodic / Semantic / Procedural), feature triads.

```html
<div class="card-grid cols-3" style="position: absolute; top: 168px; left: 64px; right: 64px;">
  <div class="card reveal d2">...</div>
  <div class="card fill-yellow reveal d3">...</div>
  <div class="card reveal d4">...</div>
</div>
```

### 5.4 card-grid cols-5

Five equal columns. Dense comparison grids (e.g., "5 reasons"). Cards should have smaller internal text (12–13px) and reduced padding.

```html
<div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; flex: 1;">
  <div class="trap-card highlight reveal d2">...</div>
  <div class="trap-card reveal d3">...</div>
  <!-- ... -->
</div>
```

Note: `cols-5` is not a named class in `shared.css` — write it inline. Five cards at 1280px with 64px margins leaves ~194px per card after gap. Test at actual resolution.

### 5.5 vs-row (Comparison)

Side-by-side comparison with a center divider.

```html
<div class="vs-row" style="position: absolute; top: 168px; left: 64px; right: 64px;">
  <div>
    <!-- Left side content -->
  </div>
  <div class="vs-marker">vs</div>
  <div>
    <!-- Right side content -->
  </div>
</div>
```

`vs-row` uses `grid-template-columns: 1fr 40px 1fr`. The `vs-marker` is Space Mono, `opacity: 0.4`.

### 5.6 Agenda List (numbered rows)

Sequential list with large outlined numbers. Items separated by hairline borders.

```html
<div style="display: flex; flex-direction: column; gap: 0;">
  <div style="display: flex; align-items: center; border-bottom: 1.5px solid rgba(17,17,17,0.15); padding: 14px 0;" class="reveal d2">
    <div style="
      font-family: 'Space Mono', monospace;
      font-size: 72px; font-weight: 700;
      color: transparent;
      -webkit-text-stroke: 1.5px rgba(17,17,17,0.18);
      min-width: 110px; text-align: right;
      padding-right: 28px; flex-shrink: 0;
      letter-spacing: -0.04em;
    ">01</div>
    <div>
      <span style="
        font-family: 'Space Mono', monospace;
        font-size: 10px; text-transform: uppercase;
        letter-spacing: 0.35em; opacity: 0.35;
      ">Category Label</span>
      <div style="font-size: 22px; font-weight: 800; letter-spacing: -0.02em;">Item Title</div>
    </div>
  </div>
  <!-- repeat for each item -->
</div>
```

---

## 6. Do / Don't

### Do

- Use `border-radius: 0` on all boxes, cards, and hard-boxes. Circles and pills are the only exceptions.
- Add `reveal dN` to every element that should animate in — stagger delays so the slide reads top-to-bottom or left-to-right.
- Use `--shadow` (`6px 6px 0px var(--black)`) on prominent elements, `--shadow-sm` (`3px 3px 0`) on cards.
- Use `position: absolute` for geometric accents (circles, rectangles, vertical bars) so they layer without disrupting flow.
- Keep the `.footer` as the last element inside `.slide`.
- Use `opacity: 0.06` on `.bg-text` elements (the huge outlined background words). They are structure, not decoration.
- One `fill-yellow` element per slide. If you need two, you've chosen the wrong accent for one of them.
- Wrap technical identifiers in `[ BRACKETS ]` in Space Mono.

### Don't

- **No gradients.** Not `linear-gradient`, not `radial-gradient` (the dot pattern in `::before` is the one exception and is already written for you).
- **No glows.** No `box-shadow` with a non-zero blur radius. `box-shadow: 0 0 20px rgba(...)` is never correct here.
- **No border-radius on boxes.** Not even `4px`. Rectangles are rectangles.
- **No `font-family` overrides on body text.** Use Inter unless you mean Space Mono structurally.
- **No inline color hex values** except where a specific opacity variant is needed (`rgba(17,17,17,0.15)`). Always prefer CSS variables.
- **Do not suppress `.slide::before`** (the dot texture) with `overflow: visible` hacks or `z-index` overrides.
- **Do not use `font-weight: 400` on headings.** h1=900, h2=800, h3=800. Lighter weights are for body only.
- **No more than 3 animated delay classes on a single element.** `reveal d4` is fine. `reveal d2 d5` is not a thing.
- **Do not skip the footer** on any content slide (title-card / section-header slides may omit it; all others include it).
- **No shadows on `.bg-black` elements using `var(--shadow)`** (black on black is invisible). Use `var(--shadow-yellow)` or a white-offset variant instead.

---

## 7. Reveal Animation Classes

All reveal animations use the same `fade-up` keyframe (opacity 0→1, translateY 12px→0, 0.35s ease). The `reveal` class starts elements at `opacity: 0`.

| Class | Delay | Use for |
|---|---|---|
| `reveal d1` | 0.04s | First element — eyebrow, meta-label, structural chrome |
| `reveal d2` | 0.12s | Primary heading (h1/h2) or first card |
| `reveal d3` | 0.20s | Secondary heading, second card, body intro |
| `reveal d4` | 0.28s | Third element, supporting content |
| `reveal d5` | 0.36s | Callout bar, fourth card |
| `reveal d6` | 0.44s | Fifth item, closing element |
| `reveal d7` | 0.52s | Last element — use sparingly |

**Stagger strategy:**

- Decorative chrome (circles, vertical bars, background shapes): `d1`
- Main heading: `d2` or `d3` depending on whether there's an eyebrow
- Cards in a grid: stagger each one — `d2`, `d3`, `d4`, etc.
- Callout bar: always the last content element before the footer — use `d5` or `d6`
- The footer itself does not get a `reveal` class (it should be visible immediately to orient the audience)

**Example stagger for a 3-card grid:**

```html
<div class="eyebrow reveal d1">[ SECTION_NN ]</div>
<h2 class="reveal d2">Slide Title</h2>
<div class="card-grid cols-3">
  <div class="card reveal d3">Card 1</div>
  <div class="card fill-yellow reveal d4">Card 2</div>
  <div class="card reveal d5">Card 3</div>
</div>
<div class="callout-bar reveal d6">...</div>
```

---

## Quick Reference: Building a New Slide

1. Copy the shell from Section 4.2 (content slide) or 4.1 (section header).
2. Decide on one dominant yellow element (usually a card or callout bar).
3. Set `[ SECTION_NN ]` eyebrow and `SLIDE_LABEL` meta-label.
4. Add body content inside the body zone (top ~168px, bottom ~80px).
5. Assign `reveal dN` in reading order — first visible thing gets `d1`.
6. Add the footer.
7. Add one geometric accent (circle, rect, dot) if the slide has open space — optional, but it kills dead zones.

Total: 10 minutes. If it's taking longer, the layout is probably fighting absolute positioning — simplify the structure first.
