---
name: hyperframes-creative
description: Non-animation creative direction for HyperFrames videos. Use for design specs, palettes, typography, narration, beat planning, audio-reactive visuals, brand/style decisions, and image-based cartoon asset direction. When a user requests illustrated characters, objects, buildings, or environments, enforce an asset-first cartoon pipeline before HyperFrames animation. For atomic motion patterns and scene blueprints, use `hyperframes-animation`.
---

# HyperFrames Creative

Brand, pacing, style, narration, and composition direction. Use after the technical contract from `hyperframes-core` is in place.

For motion patterns, scene blueprints, transitions, and CSS marker effects, use `hyperframes-animation` — this skill is intentionally non-animation.

> **Read these two FIRST for any non-trivial composition — they override web instincts:**
>
> - `references/house-style.md` — "interpret the prompt, generate real content," the lazy-default list, and the background/foreground layer recipe. This is what turns a literal restyle into a _concept_.
> - `references/video-composition.md` — video-medium scale, depth, and foreground detail. It explains how to avoid empty web-page layouts without imposing a universal element count.
>
> Skipping these is the single biggest cause of generic, web-page-looking output. They are not optional rows in the routing table below — for anything beyond a one-line edit, open both before you choose colors or write HTML.

## Default visual mode for explainers

When the source is an article, document, notes, or script, the default is **world-first motion-explainer** unless the user explicitly requests presentation/infographic/card grammar. Read [`references/world-continuity.md`](references/world-continuity.md) before planning. Derive a persistent world, concrete subjects, actions, interactions, and camera space from the source material; keep text, cards, and diagrams subordinate to that visual action.

Do not choose a domain-specific visual preset. The topic and script decide whether the world is a market, classroom, hospital, courtroom, landscape, workshop, household, or something else.

Treat the anti-presentation gate in `world-continuity.md` as render-blocking for this mode. A clear palette, typography, card, or infographic may support the world, but cannot become its principal visual unit. If a planned beat lacks setting, focal subject, action, target, or continuity, redesign it before HTML is authored.

## Image-based cartoon mode

When the brief asks for a cartoon, illustrated, cutout, cel-animation, painted-background, or image-based world, read [`references/image-based-cartoon-assets.md`](references/image-based-cartoon-assets.md) before planning assets or HTML. Treat this as an art-medium contract, not a mood suggestion.

When the requested direction also calls for a recurring animated guide, polished flat-cartoon or limited cel rendering, multiple unrelated topic domains, or subject-specific environments, read [`references/subject-adaptive-cutout-world.md`](references/subject-adaptive-cutout-world.md). Create `STYLE_BIBLE.md` and `WORLD_ASSET_MATRIX.md` before `ASSET_PLAN.md`; this prevents a generic world or a reference channel's surface nouns from becoming the default asset vocabulary.

- Require illustrated local asset files for primary characters, buildings, vehicles, props, and environment layers.
- Require `ASSET_PLAN.md`, `asset-manifest.json`, and an asset contact sheet before frame authoring.
- Prohibit primitive geometry, emoji, generic icons, and CSS boxes as finished stand-ins for those primary assets.
- Keep SVG/Paper.js for rails, pipelines, routes, gauges, particles, masks, chart lines, and editable text/UI.
- Preserve the requested broad qualities from references without copying their protected characters, logos, or compositions.

## Workflow

1. If a project has a design spec, **read it first** and treat its frontmatter tokens as brand truth (colors, fonts, spacing, tone, constraints). Which file to read (precedence `frame.md` → `design.md` → `DESIGN.md`) and how to parse it (frontmatter = normative, prose = context) are defined once in [`references/design-spec.md`](references/design-spec.md) — resolve and load per that doc.
2. If no design spec exists and the user asks for visual direction, choose a route:
   - Ready-made frame-preset (optional) → `frame-presets/` (adopt a `FRAME.md` as `frame.md`; see `references/design-spec.md`)
   - Named style or mood → `references/visual-styles.md`
   - Fast defaults → `references/house-style.md`
   - Interactive selection → `references/design-picker.md`
3. For multi-scene work, plan beats and rhythm before writing HTML → `references/beat-direction.md`. For scene transitions, jump to `hyperframes-animation/transitions/`.
4. For motion-heavy work, read `references/motion-principles.md` (high-level guardrails), then go to `hyperframes-animation` for atomic rules.

## Routing

| Topic                                                                         | Read                                           |
| ----------------------------------------------------------------------------- | ---------------------------------------------- |
| Adopt a ready-made frame-preset as `frame.md` (optional)                      | `frame-presets/` · `references/design-spec.md` |
| Default palettes, motion, typography, lazy defaults to question               | `references/house-style.md`                    |
| Named style presets, mood-to-style routing                                    | `references/visual-styles.md`                  |
| Palette-specific color tokens                                                 | `palettes/*.md`                                |
| Composition patterns — PiP, text-behind-subject, title card, slide show       | `references/composition-patterns.md`           |
| Stats / infographic presentation                                              | `references/data-in-motion.md`                 |
| Structured expansion for open-ended prompts                                   | `references/prompt-expansion.md`               |
| Video-medium density, scale, color, frame composition                         | `references/video-composition.md`              |
| Per-beat direction, rhythm planning, transition timing                        | `references/beat-direction.md`                 |
| Post-authoring spec verification (colors, type, corners, spacing, depth)      | `references/design-adherence.md`               |
| High-level motion guardrails and GSAP-quality rules                           | `references/motion-principles.md`              |
| Image-based cartoon assets, cutout layers, and the pre-HTML asset gate        | `references/image-based-cartoon-assets.md`      |
| Subject-adaptive flat/cel cutout worlds, original guides, and topic asset kits | `references/subject-adaptive-cutout-world.md`   |
| Font selection, pairings, rendered-video type guardrails                      | `references/typography.md`                     |
| Story doctrine — hook language, value-before-evidence, storyboard-as-proposal | `references/story-spine.md`                    |
| Script pacing, tone, openings, number pronunciation                           | `references/narration.md`                      |
| Precomputed audio bands mapped to motion                                      | `references/audio-reactive.md`                 |

## Scripts

- `scripts/contrast-report.mjs` — inspect contrast warnings from rendered frames.
- `scripts/extract-audio-data.py` — pre-extract audio bands for audio-reactive compositions.
- `scripts/package-loader.mjs` — support script for bundled creative tooling.

`contrast-report.mjs` resolves helper packages from the current project first, then can bootstrap the bundled HyperFrames package version. Set `HYPERFRAMES_SKILL_PKG_VERSION=<version>` only when running the skill outside the bundled CLI/skill install and you need to pin that bootstrap version explicitly.

Run from the repo root with explicit paths, for example:

```bash
python skills/hyperframes-creative/scripts/extract-audio-data.py <audio-file>
```

Animation analysis (`animation-map.mjs`) lives in `hyperframes-animation/scripts/`.

## Boundaries

- Do not override `hyperframes-core` technical rules.
- Do not require a design system for a minimal technical composition.
- Do not add extra scenes, narration, music, captions, or transitions unless the request calls for them or you first propose the expansion.
- Keep recipe references task-specific; do not read every reference for simple edits.
