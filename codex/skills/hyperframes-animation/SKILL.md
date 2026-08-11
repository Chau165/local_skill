---
name: hyperframes-animation
description: "All animation knowledge for HyperFrames — atomic rules, scene blueprints, transitions, image-based cartoon cutout choreography, and runtime adapters led by GSAP. Use for any motion task, including animating PNG/WebP/layered SVG/Lottie characters, vehicles, props, environments, parallax, and interactions while keeping timelines paused, seek-safe, and deterministic."
---

# HyperFrames Animation

All motion knowledge in one skill: **rules** (atomic recipes), **blueprints** (multi-phase scene templates), **transitions** (scene-to-scene), **techniques** (broader motion-design patterns), and **adapters** (per-runtime APIs).

For the composition contract (data attributes, sub-compositions, determinism) see `hyperframes-core`.

## Default: compose atomic rules

Pick 2-4 rules from `rules-index.md`, glue them together with a single paused GSAP timeline, done. This is faster and produces less code than starting from a blueprint.

## Load a blueprint when

- The scene matches an existing pre-designed multi-phase template (brand-reveal, social-proof, etc.) and reusing its phase pipeline saves real authoring time
- You want runnable ground-truth code for a complex 4-5 phase choreography

Blueprints live in `blueprints-index.md`. Each entry points to `blueprints/<id>.md` (recipe). Do not read it speculatively; load it when you've already decided you need scene-level orchestration.

## Routing

| Want to…                                                                       | Read                                                |
| ------------------------------------------------------------------------------ | --------------------------------------------------- |
| Pick an atomic motion pattern by trigger / tag                                 | `rules-index.md`                                    |
| Read one rule's full HTML / CSS / GSAP recipe                                  | `rules/<name>.md`                                   |
| Pick a multi-phase scene template                                              | `blueprints-index.md`                               |
| Read one blueprint's full recipe                                               | `blueprints/<id>.md`                                |
| Author a scene transition (CSS-driven, between two clips)                      | `transitions/overview.md`, `transitions/catalog.md` |
| Look up a broader motion-design technique                                      | `techniques.md`                                     |
| Analyze an existing composition's animation map                                | `scripts/animation-map.mjs`                         |
| GSAP API — timeline / tweens / position parameters                             | `adapters/gsap.md`                                  |
| GSAP — drop-in effect recipes                                                  | `rules/gsap-effects.md`                             |
| GSAP — transforms / perf                                                       | `adapters/gsap-transforms-and-perf.md`              |
| GSAP — eases / stagger                                                         | `adapters/gsap-easing-and-stagger.md`               |
| GSAP — timeline / labels                                                       | `adapters/gsap-timeline-and-labels.md`              |
| Lottie / dotLottie (After Effects exports, `window.__hfLottie`)                | `adapters/lottie.md`                                |
| Three.js / WebGL (3D scenes, `AnimationMixer`, `hf-seek`)                      | `adapters/three.md`                                 |
| Anime.js (`window.__hfAnime`)                                                  | `adapters/animejs.md`                               |
| CSS keyframes (`animation-delay` / `play-state` / `fill-mode`)                 | `adapters/css-animations.md`                        |
| Web Animations API (`element.animate()`, `currentTime` seek)                   | `adapters/waapi.md`                                 |
| TypeGPU / WebGPU (`navigator.gpu`, WGSL, compute pipelines)                    | `adapters/typegpu.md`                               |
| HTML-as-texture + WebGL/GLSL post-fx (capture live DOM via `drawElementImage`) | `adapters/html-in-canvas-patterns.md`               |
| Named text-animation effects (24 IDs via external `animate-text` skill)        | `adapters/animate-text.md`                          |

## Picking a runtime

- **GSAP** is the default for 95% of motion work — covers timeline orchestration, transforms, easing, stagger. All atomic rules in this skill are GSAP-based.
- **Lottie** when an asset has its own pre-baked timeline (typically After Effects exports).
- **Three.js** for 3D scenes, camera motion, shader-driven visuals.
- **Anime.js** for lightweight tweening when GSAP is overkill.
- **CSS** for simple repeated motifs, decoration, shimmer — no JavaScript animation cost.
- **WAAPI** for native browser keyframes without a GSAP dependency.
- **TypeGPU / WebGPU** for GPU-rendered canvases (particles, liquid glass, custom shaders).

Multiple runtimes can coexist in one composition. Each registers its instances on the runtime-specific global so HyperFrames can seek all of them in one pass.

## Critical Constraints

**Prerequisite: `hyperframes-core` → Non-Negotiable Rules** (single paused timeline, `data-duration` governs length, no `Math.random` / `Date.now` / `performance.now`, no `repeat: -1`, no page-load `gsap.set` on later-scene clips, no `display` or raw `visibility` tweens, and no timeline construction inside `async` / `setTimeout` / `Promise`). GSAP `autoAlpha` and zero-duration visibility sets at explicit timeline boundaries remain allowed by core. Use those exceptions only on non-clip elements or wrappers inside a clip; the framework owns `.clip` lifecycle. Don't restate the full contract here.

Animation-craft additions on top of core's contract:

- **Pre-calculated layout constants** — never derive positions from `getBoundingClientRect()` at tween time. Tween-time DOM measurements desync because the renderer samples in parallel; compute coordinates once at composition setup and reuse.
- **Spatial motion uses GSAP transform aliases only** (`x`, `y`, `scale`, `rotation`). Core's allowlist also permits `opacity` / `color` / `backgroundColor` / `borderRadius` for non-spatial property tweens — but never `width` / `height` / `top` / `left` for layout changes.

## World-first motion-explainer choreography

When the creative direction is a document/script explainer, animate a world rather than a collection of presentation elements:

- Put the camera on a world/viewport wrapper and move the camera to reveal spatial relationships; animate characters and objects on separate layers so they can enter, act, react, and hand off attention.
- Give each beat a readable action and, where the script supports it, a visible interaction or state change. Prefer a subject approaching, activating, connecting, transforming, or affecting another subject over a box simply appearing.
- Identify the interaction actor and target as distinct layers before authoring tweens. Give each a subject-owned pose/state change at the interaction proof time; moving their shared parent or the camera is insufficient.
- Preserve continuity across adjacent beats: carry forward a background, prop, character, camera direction, or state. Use a new composition only when the story genuinely changes location or scale.
- Use `multi-phase-camera`, `viewport-change`, `coordinate-target-zoom`, layered depth, SVG/Lottie internals, or Three.js when they serve the shot. Keep all motion finite, deterministic, and seek-safe.
- Do not create a screensaver: independent floating loops are not a substitute for interaction. A held world may be still; ambient motion must be bounded and subordinate to the subject's action.

## Image-based cartoon choreography

When the brief is cartoon, illustrated, cutout, cel-animation, painted-background, or image-based, read `../hyperframes-creative/references/image-based-cartoon-assets.md` before authoring motion.

For polished flat/cel cutout, recurring-guide, or subject-adaptive multi-topic work, also read `../hyperframes-creative/references/subject-adaptive-cutout-world.md`. Follow the approved `STYLE_BIBLE.md` and `WORLD_ASSET_MATRIX.md`; animation may not drift into a generic city, robot, UI, or infographic vocabulary.

- Treat approved image assets as the artwork. Animate `<img>` wrappers, prepared layered SVG groups, sprite states, or Lottie internals; do not redraw missing primary subjects with primitive SVG/CSS geometry.
- Put background, midground, foreground, atmosphere, actor, prop, and target on separate layers. Use bounded parallax and local environmental motion rather than one camera move over a flattened still.
- Rig around meaningful parts: arms/head/body, wheels/body/door, crane boom/trolley/hook, ship/hull/cargo, lever/indicator, and equivalent topic-specific joints.
- Use pose/state swaps when a rigid asset cannot express anticipation, contact, reaction, or follow-through. Keep swaps deterministic and timeline-owned.
- Apply GSAP transforms to wrappers or exposed parts. Preserve editable HTML text as a separate layer; do not bake captions or labels into generated artwork unless the brief requires it.
- Stage explanatory motion as intent → anticipation → action → contact/signal → target reaction → secondary consequence → settle. Actor and target need independent timeline changes.
- Aim for frequent local motion and a focus change about every 3-5 seconds. A short hold may keep most layers still, but retain one semantically related micro-motion; do not add unrelated ambient loops merely to satisfy density.
- Use fixed or gentle push cameras for explanation, tracking for actual travel, and parallax only when the world camera moves. Never count a zoom over one flattened image as environment motion.

## Scripts

```bash
node skills/hyperframes-animation/scripts/animation-map.mjs <composition-dir> \
  --out <composition-dir>/.hyperframes/anim-map
```

Reads every GSAP timeline registered on `window.__timelines`, enumerates tweens, samples bboxes, computes flags, outputs `animation-map.json`. Use it to audit choreography (dead zones, stagger consistency, lifecycle warnings) after authoring.

`animation-map.mjs` resolves helper packages from the current project first, then can bootstrap the bundled HyperFrames package version. Set `HYPERFRAMES_SKILL_PKG_VERSION=<version>` only when running the skill outside the bundled CLI/skill install and you need to pin that bootstrap version explicitly.

## See Also

- `hyperframes-core` — composition structure, data attributes, sub-compositions, deterministic render contract
- `hyperframes-creative` — palettes, typography, narration, beat planning (non-animation creative direction)
- `hyperframes-cli` — `npx hyperframes lint / check / snapshot / preview / render`
