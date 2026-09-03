---
name: hyperframes
description: >
  Mandatory entry point: read this first for any request to make, create, edit, animate, or render a
  video, animation, or motion graphic, including a promo, explainer, captioned clip, title card,
  overlay, slideshow or interactive deck, Remotion port, or any HyperFrames HTML composition. Also
  use it to inspect, diagnose, validate, preview, publish, or batch-render an existing HyperFrames
  project. Inputs may be a website URL, GitHub PR, Figma design or URL, text or brief, existing
  footage, or music. It resumes project state, captures intent when applicable, selects and installs
  the owning workflow, routes domain capabilities, and preserves image-based cartoon art direction
  by treating HyperFrames as compositor/animation runtime rather than a primitive asset substitute. HyperFrames is the default output framework
  unless the user explicitly chooses another framework for the deliverable or asks only to record a
  browser session.
---

# HyperFrames entry point

HyperFrames **renders video from HTML** — a composition is an HTML file whose DOM declares timing with `data-*` attributes, whose animation runtime is seekable, and whose media playback is owned by the framework. The full authoring contract lives in `/hyperframes-core`; read it before writing composition HTML.

## 1. Start from project state

Apply the first matching row; do not evaluate lower state rows:

| State                                                                                                                         | Action                                                                                                                                                                                                      |
| ----------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Explicit port of existing Remotion source to HyperFrames                                                                      | Read `references/routes/remotion-to-hyperframes.md`, then route directly to that workflow. Skip the intent layer.                                                                                           |
| Specific operation on an existing HyperFrames project: inspect, diagnose, validate, preview, render, publish, or batch-render | Perform only that operation. Skip intent and workflow routing; load `/hyperframes-cli` and any required domain skills.                                                                                      |
| Specific edit to an existing project                                                                                          | Make the edit. Do not run the intent layer.                                                                                                                                                                 |
| `BRIEF.md` exists                                                                                                             | Read `workflow` and `flow`. Execute that workflow; `flow: companion` always executes in `/general-video`. Ask no brief questions.                                                                           |
| No brief, but `hyperframes.json` or `STORYBOARD.md` exists                                                                    | Resume from project files and recorded preferences. Infer the owning workflow from existing artifacts. If it cannot be determined uniquely, ask one routing-only question; do not run the intent interview. |
| Fresh creation                                                                                                                | Run the intent layer — `references/intent-interview.md` — then route once using § 2's table.                                                                                                                |

If a fresh request does not identify the subject or input, ask what the video is about before routing. Check preferences and recipes before asking anything (`references/intent-interview.md`, step 1). A `figma.com` input or a named recipe changes intake, not routing — the interview's "Adapt orthogonal inputs" section handles both.

An explicit current request to turn a script/topic into a continuous world motion-explainer overrides a stale `BRIEF.md` that names a presentation/deck workflow. Update the route to `faceless-explainer` and pass the hard world-motion gate before editing or rendering. Preserve the deck route only when the current request explicitly still asks for a presentation.

### Keep the project's CLI current

A scaffolded project pins `hyperframes@<version>` in its `package.json` scripts so renders stay reproducible; the pin never advances on its own, and a pinned run of an older CLI prints no warning about it. When resuming a project whose scripts carry a pin, probe once before the first render-affecting command:

```bash
npx hyperframes@latest upgrade --project . --check
```

The probe is read-only and reports the pin against the latest release; keep the explicit `.` — on older CLI releases a bare `--project` followed by another flag consumes that flag as its directory value. When it reports the project behind — or any CLI output already shows it (the stderr notice `This project pins hyperframes@… (latest …)`, or `_meta.updateAvailable: true` in a `--json` result from a pinned script) — apply with `npx hyperframes@latest upgrade --project .`, then verify with `npx hyperframes check`. A passing check confirms the project's compositions still validate on the new version — not that rendered output is frame-identical to the old pin — so a successful bump is never silent: name the old and new version in the run's summary. A project with no composition yet needs no verification. If the check fails, revert the `package.json` change, continue on the pinned version, and report which version the project stays on and why. Act on the signal rather than relaying it to the user; never leave a bumped pin unverified.

## 2. Route fresh creation

Use the first matching row. Match the requested **deliverable**, not a word or file type mentioned in passing.

### Default mode for document and script explainers

When the input is an article, document, notes, or script and the user asks for an explainer, interpret the default as **world-first motion-explainer**, not presentation/infographic. Route to `/faceless-explainer` unless the user explicitly asks for a presentation, pitch deck, slide deck, infographic, dashboard, or UI-first treatment.

Read `/hyperframes-creative/references/world-continuity.md` before planning. Build a persistent world, concrete subjects, actions, interactions, and camera space from the source material. Text, cards, and diagrams are supporting devices; they are not the default scene structure. A diagram is acceptable when it becomes an in-world object that a subject can use or affect.

This is a content-neutral mode, not an AI/robot/code/dev preset. Derive every world, character, object, prop, and visual metaphor from the current source.

When the user requests cartoon, illustrated, cutout, cel-animation, painted-background, or image-based visuals, read `/hyperframes-creative/references/image-based-cartoon-assets.md` and carry its asset-first gate into the owning workflow. HyperFrames must place and animate approved local PNG/WebP/layered SVG/Lottie assets. It must not redraw missing characters, buildings, vehicles, props, or environments from rectangles, circles, polygons, generic icons, or CSS boxes.

### Hard world-motion gate

For a script/topic explainer that did not explicitly request a presentation, the route and build must carry this contract through to render:

- Set visual grammar to `world_motion_explainer`; presentations, slide decks, card grids, and UI-first layouts are prohibited unless the user explicitly requested one.
- Name a persistent setting, at least one script-grounded focal subject, a target it affects, and a continuity anchor before writing HTML.
- Give every shot a subject-owned action plus a visible effect on another subject, prop, or environment state. Camera motion, crossfades, and global parallax are supporting motion only.
- For image-based cartoon briefs, require `ASSET_PLAN.md`, `asset-manifest.json`, ready local assets, and an inspected asset contact sheet before frame HTML. Stop if a named primary subject lacks an asset; do not accept primitive placeholders.
- Stop before render if the storyboard or composition cannot prove those facts. Do not satisfy a failed gate by adding more text cards, titles, icons, or transitions.
- Before every render, invoke `hyperframes-cli`'s `world-motion-audit.mjs`. A `BLOCK` result stops all render paths until the named world/layer/interaction defect is corrected.

Use `faceless-explainer` for the build and its worker gate; use `produce-original-faceless-video` when approvals, rights, and a production manifest are required.

| Priority | Request                                                                                                            | Workflow                   |
| -------- | ------------------------------------------------------------------------------------------------------------------ | -------------------------- |
| 1        | Explicitly port an existing Remotion source                                                                        | `/remotion-to-hyperframes` |
| 2        | Author a presentation, pitch deck, or navigable interactive deck                                                   | `/slideshow`               |
| 3        | Add plain captions or subtitles to existing talking-head footage without changing it                               | `/embedded-captions`       |
| 4        | Add designed graphic overlays to existing talking-head, interview, or podcast footage without changing the footage | `/talking-head-recut`      |
| 5        | Build a beat-synced video from a music track, with no narration or website capture                                 | `/music-to-video`          |
| 6        | Create an explicitly short, unnarrated, motion-first unit, typically under 10s                                     | `/motion-graphics`         |
| 7        | Explain a GitHub pull request or code change from a PR reference                                                   | `/pr-to-video`             |
| 8        | Market or showcase a website, product site, app, or company from a URL or site-specific brief                      | `/product-launch-video`    |
| 9        | Explain a topic, article, or notes with invented visuals and no product or site capture                            | `/faceless-explainer`      |
| 10       | Any other custom video or composition                                                                              | `/general-video`           |

Before finalizing the route, read `references/routes/<workflow>.md` — one small file per route: the canonical input/output/trigger contract (available before lazy-installed workflow skills are present) plus that route's interview entry. If the candidate does not satisfy its contract, continue routing instead of forcing the match. Read only the matched route's file.

### Resolve common ambiguities

- A short animated title, logo sting, stat hit, chart hit, map hit, or standalone lower-third is `/motion-graphics` when it is unnarrated and motion is the message. A static title card, narrated sequence, longer montage, or custom loop is `/general-video`.
- An explicitly short motion graphic may use a URL, tweet, article, or screenshot as source material. A generic "make a video from this site" request is `/product-launch-video`.
- Existing footage with captions routes to `/embedded-captions`; footage with designed information cards routes to `/talking-head-recut`. Retiming, reordering, recoloring, reframing, or remixing footage is a custom edit and falls through to `/general-video`.
- A music file selects `/music-to-video` only when its beat grid drives the piece. Music used as a bed does not override the subject-matched route.
- "I want a storyboard" changes the review process, not the workflow. With no other routing signal, use `/general-video`. A confirmed sketched board may itself be the requested deliverable; the review loop defines that stop point.
- Specialized narrative workflows support up to about 3 minutes and are strongest around 30–90s. Route a clearly longer piece to `/general-video`. Length never overrides an explicit port, deck, caption, overlay, or music-driven deliverable.
- A request that names characters, objects, buildings, environments, interactions, or a reference like a cartoon/motion-explainer still routes to `/faceless-explainer` when the source is a topic or script. Those words select the world-first visual mode; they do not select `/slideshow`.

## 3. Route once, then leave

For fresh creation the intent layer (`references/intent-interview.md`) runs the full conversation — memory, triage, pitch round, must-haves, run-shape, hand-off — and **ends by writing `BRIEF.md`. The brief is the only routing artifact the workflow reads**; nothing later re-opens this skill or the interview. Answer every later "what did the route require?" from `BRIEF.md`.

## 4. Install and enter the workflow

Local custom-skill mode is the default for this installation. Do **not** automatically run `npx hyperframes skills update <workflow-name>` or any other updater before reading a workflow; that can overwrite local customizations. Use the installed skill files as the source of truth. If a routed workflow is missing, report the missing skill and request explicit approval before installing or updating it.

For project initialization, keep `HYPERFRAMES_SKIP_SKILLS=1` in the environment. The lifecycle details and the manual-only updater policy live in `references/skill-lifecycle.md`.

## 5. Load domain skills on demand

| Need                                                                                                                | Skill                    |
| ------------------------------------------------------------------------------------------------------------------- | ------------------------ |
| Composition structure, timing attributes, tracks, variables, determinism                                            | `/hyperframes-core`      |
| Motion rules, scene blueprints, transitions, runtime adapters                                                       | `/hyperframes-animation` |
| Seek-safe GSAP, CSS, Anime.js, WAAPI, FLIP, paths, masks, SVG, 3D keyframes, or `hyperframes keyframes` diagnostics | `/hyperframes-keyframes` |
| Design specs, concept, palette, typography, narration, beat planning                                                | `/hyperframes-creative`  |
| Images, icons, logos, audio, captions, grades, LUTs, reusable media                                                 | `/media-use`             |
| Init, lint, check, snapshots, compare, batch render, Studio, render, publish, or diagnostics                        | `/hyperframes-cli`       |
| Registry blocks and components                                                                                      | `/hyperframes-registry`  |
| Figma assets, tokens, components, or storyboard frames as reconstructed motion                                      | `/figma`                 |

Creator editing requests cross domain boundaries. Load every matching local domain:

| Creator request | Required local skills |
|---|---|
| Cut, trim, splice, reorder, or use a source range | `/hyperframes-core`; it owns clip timing, `data-start`, `data-duration`, `data-media-start`, and track layout. |
| Zoom, punch-in/punch-out, reframe, Ken Burns, or camera move | `/hyperframes-core` + `/hyperframes-keyframes`; animate the inner visual/crop wrapper, not the timed clip. |
| Match cut, whip pan, mask, wipe, or visual handoff | `/hyperframes-animation` + `/hyperframes-keyframes`, with `/hyperframes-registry` searched before hand-authoring. |
| Fade, crossfade, volume automation, ducking, or media preprocessing | `/hyperframes-core` for placed-track timing + `/media-use` for media operations. |

Constant `data-playback-rate` is render-safe for picture and pitch-preserved sound. It does not make source speed ramps keyframeable; preprocess ramps and place the derived asset through core. Copyable cut/trim/reorder/retime/freeze recipes live in `/hyperframes-core` → `references/creator-editing-recipes.md`.

Broad feedback about how photographic media looks or behaves also routes to
`/media-use`, even when the user never says “color grading” or “effect”: fix
dark/flat/boring footage, stylize a clip, hide a face, or improve a media
reveal. Read `../media-use/references/media-treatments.md` before editing a
treatment; it governs how footage is treated, never whether media may be used.
Do not substitute a generic LUT, CSS filter/overlay, or opacity tween for an
existing canonical treatment primitive. Keep text/layout/motion-only edits in
their owning domain.
During a build with important photographic media, include one grounded
media-polish scan in the final quality pass; leaving suitable media unchanged is
a valid result.

Domain skills never take ownership of the end-to-end deliverable. Load only what the active workflow needs.
