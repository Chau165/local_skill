---
name: faceless-explainer
description: "Turn arbitrary text — an article, notes, a topic, a brief, or a script — into a faceless motion-explainer video with a continuous world, generated or resolved image-based cartoon assets, layered environments, characters/objects, interactions, camera movement, and supporting text. Use for illustrated topic explainers, concept breakdowns, how-tos, and listicles. Presentation/infographic/card grammar is only used when explicitly requested. Unclear → /hyperframes."
---

> **Local custom-skill mode:** Do not run `npx hyperframes skills update faceless-explainer` automatically. Use the installed local skill files so customizations remain intact. Update only after explicit user approval.

> **media-use**: Before sourcing or generating audio/images/logos, call `/media-use`. For a cartoon/illustrated brief, also read `../hyperframes-creative/references/image-based-cartoon-assets.md`; for polished flat/cel cutout, recurring-guide, or multi-topic subject-adaptive work, also read `../hyperframes-creative/references/subject-adaptive-cutout-world.md`. Use available image-generation or sprite-generation capabilities to create local production assets when catalog assets do not fit. Run `--adopt` first to register existing assets.

> **World-first default**: For document/script explainers, read `../hyperframes-creative/references/world-continuity.md`. Build a persistent world and a subject roster from the source before choosing layouts. Concrete nouns should become visible characters, props, machines, buildings, locations, or interface-like objects; text, cards, and diagrams remain supporting evidence.

> **Asset-first cartoon default**: When the user requests cartoon, illustrated, cutout, cel-animation, painted-background, or image-based visuals, primary subjects and environments must be real local illustration assets. HyperFrames composes and animates them; it does not replace them with primitive SVG/CSS geometry.

# Faceless Explainer to HyperFrames

## Non-presentation render gate

Unless the user explicitly asks for a presentation, slide deck, infographic, dashboard, or UI-first treatment, treat every missing world field as a blocking build defect. Before dispatching a frame worker, `STORYBOARD.md` must name the setting, focal subject, action, distinct interaction actor/target, and continuity anchor. A title card, card grid, paragraph, diagram, entrance tween, camera move, or crossfade cannot fill a missing field. Redesign the beat in-world instead.

Use this skill to turn a body of text into a motion-explainer: pick a design system, derive a world bible, plan a teaching story, and build it frame by frame in HyperFrames. **Faceless** means the visuals are invented or resolved downstream — there is no website capture requirement. The default visual unit is a continuous world with characters/objects acting in space, not a presentation slide.

> **The front door is `/hyperframes`.** You are the orchestrator. Run each step, verify its gate, and only then continue. This skill is for **explaining a topic from text, with no product and no website to capture**. Any other intent, a bare "make a video", or any uncertainty → read `/hyperframes` first — the intent layer owns every route decision, and a fresh creation arriving here without `BRIEF.md` goes through it anyway (Setup's opening rule).

You are the orchestrator. Work in `videos/<project>/`. Run steps in order and pass each gate before continuing. User-gated steps are Step 0, Step 3, and Step 6. Read `../hyperframes-core/references/brief-contract.md` before Step 0 — it defines the gate types and how `BRIEF.md`'s `flow`/`storyboard` derive the mode that governs the Step 3/4/6 gates. Do every step yourself except Step 5, where you dispatch one sub-agent per frame. Do not put design or motion rules here; those live in the frame-worker sub-agent, this skill's local `../hyperframes-animation/rules/` + `../hyperframes-animation/blueprints/`, and `hyperframes-creative`.

Workflow: Step 0 setup → `hyperframes.json`; Step 1 brief → `capture/extracted/`; Step 2 design system → `frame.md`; Step 3 storyboard/script → `STORYBOARD.md` and `SCRIPT.md`; Step 3.1 audio → `audio_meta.json`; Step 4 visual design → enriched `STORYBOARD.md`; Step 4.5 illustrated assets → `STYLE_BIBLE.md`, `WORLD_ASSET_MATRIX.md`, `ASSET_PLAN.md`, `asset-manifest.json`, and `public/assets/`; Step 5 frames → `compositions/frames/NN-*.html` and `index.html`; Step 6 final render → `renders/video.mp4`.

---

## Step 0: Setup

Goal: Enter with a confirmed brief, create the HyperFrames project, and make the brief durable.

**The brief is confirmed by the intent layer, not by questions asked here.** Opening rule, in order: **(1)** `BRIEF.md` exists → read it and ask nothing — the brief is settled, and its `flow`/`storyboard` derive the mode (brief contract § 1). **(2)** No `BRIEF.md` but the project exists (`hyperframes.json` / `STORYBOARD.md` on disk) → resume from the storyboard's frontmatter and the recorded preferences; never re-interrogate a half-built project. **(3)** Neither — a fresh creation request that arrived here directly → read `/hyperframes` and run its intent layer (`references/intent-interview.md`): it checks recipes and remembered defaults, conducts this route's questions (`../hyperframes/references/routes/faceless-explainer.md`), and hands back the locked brief. Edit requests skip all of this — go do the edit.

Initialize only if `hyperframes.json` is missing. Name `<project>` from the topic in kebab-case, such as `compound-interest-explained`; never use workspace name or timestamp.

`HYPERFRAMES_SKIP_SKILLS=1 npx hyperframes init "videos/<project>" --non-interactive --example=blank --skill=faceless-explainer` — keep the environment flag enabled so `init` does not refresh the installed global skills. In PowerShell, set `$env:HYPERFRAMES_SKIP_SKILLS='1'` before running the command.

After init, let `<PROJECT_ROOT>` be `videos/<project>` and run every subsequent relative-path command with that directory as its working directory. In the commands below, `.` means `<PROJECT_ROOT>`; never write `.media`, `capture`, or output files in the caller directory.

**Write `BRIEF.md` immediately after init** (never before — `init` refuses a non-empty directory): the intent layer's locked brief, shape per `../hyperframes-core/references/brief-format.md`. Resolve `<MEDIA_DIR>` as the installed `/media-use` skill directory. Then record each preference-backed answer with `node <MEDIA_DIR>/scripts/prefs.mjs record --hyperframes .` (`brief-format.md` names the subset). If the intent layer adopted a recipe, run `node <MEDIA_DIR>/scripts/recipe.mjs use --hyperframes . --name <name>`; it copies its `frame.md` into the project (Step 2 is then skipped) and returns the skeletons Step 3 drafts from. A recipe fills answers, not approvals; the review gates still run.

**Show sign-in status before proceeding past Setup** — run `npx hyperframes auth status` and relay its output verbatim. It reports whether voice/BGM will use HeyGen or local engines and, when signed out, how to sign in. Apply one branch:

- **Collaborative:** wait for the user to sign in or explicitly choose `offline` / `go`.
- **Autonomous:** state the status and continue through the available local engines.

Do not silently omit a required capability when no offline provider exists; surface the blocker. Do not fold this decision into another question or write keys into a per-repo `.env`. Auth ownership and offline fallbacks: `/media-use` `references/setup-providers.md` § Providers.

**Gate:** `hyperframes.json` and `BRIEF.md` exist; the preference-backed answers were recorded (brief contract § 2); sign-in status was shown (signed in, or continuing offline).

---

## Step 1: Brief (no capture)

Goal: Fold the user's text into the project as the source of information. There is no website capture; visual assets are generated or resolved later from the approved world and storyboard.

Save the user's full input verbatim, then create the synthetic capture package by hand:

- `capture/extracted/visible-text.txt` — the full article / notes / topic / brief, verbatim. This is the source of **information**, not a story template (Step 3 reshapes it).
- `capture/extracted/tokens.json` — `{ "title": "", "description": "", "colors": [], "fonts": [] }`. Fill `title`/`description` from the brief. Leave `colors`/`fonts` empty unless the user explicitly gave brand colors or fonts — then add them (the design preset supplies a complete palette regardless).

If the user pasted a script or wants their wording kept, save it verbatim as `user_script.txt`; `VO_MODE` (verbatim or restructured) comes from `BRIEF.md` — the intent layer asks it when a script arrives. Ask once here only if the brief somehow lacks it, and store the answer for Step 3.

Do **not** run `npx hyperframes capture` when there is no URL. Keep user-supplied visual references separate from production assets and record them as style/context evidence; do not reuse a protected reference character, logo, or composition. Production-ready illustrated assets are planned and generated in Step 4.5.

**Gate:** `capture/extracted/visible-text.txt` and `capture/extracted/tokens.json` exist; you can state the explainer's topic and audience in one clear sentence.

World-first rule: no supplied asset inventory does not mean no visual subject planning. For concrete nouns in the source, name the needed character/object/place in `focal`, `roles`, or `asset_candidates`. In image-based cartoon mode, Step 4.5 must create or resolve these assets before HTML authoring. Do not silently replace a concrete subject with a text card or primitive placeholder.

---

## Step 2: Design System

Goal: Choose one shipped frame preset; a script turns it into this video's `frame.md` + caption skin.

Choose a preset whose palette and depth can support a continuous world. A preset may supply typography and surfaces, but it must not force every beat into a card or infographic layout.

When `BRIEF.md` names a `style_preset` — the user picked it by eye from the showcases at the intent layer — use it; the judgment call is yours only when the brief is silent. Then you make the one call — **which preset**: read `../hyperframes-creative/references/design-spec.md` and browse `../hyperframes-creative/frame-presets/`; pick the preset whose look best fits the topic, tone, and audience. Then run:

```bash
node <SKILL_DIR>/scripts/build-frame.mjs --preset <name> --hyperframes .
```

The script does the rest deterministically: copies the preset's `FRAME.md` → `frame.md` and **remixes** it onto any brand tokens in `capture/extracted/tokens.json` (brand colors mapped onto the preset's color keys by role; the preset's display + body fonts swapped for the brand's), copies the preset's caption skin to `.hyperframes/caption-skin.html`, and self-validates (exits 1 on a broken mapping). Proceed as soon as it exits 0 — no hand-editing of the spec.

A faceless explainer usually has **no brand colors/fonts** (`tokens.json` colors/fonts empty) → the script keeps the preset's own palette, a complete shippable design. Only when the user named brand colors/fonts add them to `tokens.json` before running, and only adjust `frame.md` by hand afterward if a mapping truly needs it.

**Gate:** `build-frame.mjs` exited 0 — `frame.md` exists from a named preset, and (when the preset ships one) `.hyperframes/caption-skin.html` exists as the caption skin source; the chosen preset was recorded as a preference (`--key style_preset --workflow <this workflow>`, brief contract § 2).

---

## Step 3: Storyboard and Script

Goal: Turn the text into an approved frame-by-frame teaching plan.

Read `../hyperframes-creative/references/story-spine.md` (hook language, value-before-evidence, storyboard-as-proposal), `../hyperframes-creative/references/world-continuity.md`, `references/story-design.md`, `../hyperframes-animation/blueprints-index.md`, `../hyperframes-core/references/storyboard-format.md`, and `../hyperframes-core/references/script-format.md`. Use them to write `STORYBOARD.md` and, when narration is needed, `SCRIPT.md`. Set the frontmatter `duration:` from the brief's `length` — a rough expectation; assembly reports where the cut lands against it.

Use `story-design.md` for the explainer structure (concept / how-to / listicle / story), hook strategy, clarity techniques, emotional beats, the type-enum mapping, and `VO_MODE`. The video's sequence comes from **narrative design, not the input text's paragraph order** — reorder, merge, omit, compress. Build a small world bible in `## Video direction`: world, subject roster, action verbs, continuity anchors, and camera space. For each beat, name the place, focal character/object, action, interaction or state change, and what persists from the previous beat. As a **soft guide**, consult the role→blueprint menu in `../hyperframes-animation/blueprints-index.md`: for each beat, write the voiceover in the shape its candidate blueprint implies and tag that candidate `blueprint:` id when one fits. Teaching truth still decides which beats exist — never force a beat to fit a blueprint, and never invent a beat just because a proven shape is available. Do not leave `focal`/`roles` as generic text when the source names a concrete subject; record the needed visual subject in those fields and use `asset_candidates` when a resolved or generated asset is appropriate. Use the exact required fields from the storyboard and script references.

After drafting, run the review loop's plan pass — `../hyperframes-core/references/review-loop.md` § 1: open the board (don't ask whether to), present the plan as a proposal, and ask the two questions — approve or change, and **sketches first** (recommended) or skip. Feedback loops through chat or the board's comments file until approved. This is a **checkpoint gate** (brief contract § 1): in autonomous mode there is no board and nothing to ask — post the same summary as a heads-up and proceed; sketches collapse into the build, and the one preview question comes at Step 6.

**Gate:** `STORYBOARD.md` exists, every frame has the required narrative fields, `SCRIPT.md` exists when narration is needed, and the user approved the frame-by-frame plan (autonomous: the summary was posted as a heads-up).

---

## Step 3.1: Audio

Goal: Generate narration, word timings, music, and audio metadata from the approved script.

Start audio after Step 3 approval. Run it in the background, then continue to Step 4. (Sign-in status was already shown in Step 0; the engine falls back automatically.)

**Choose the narration voice from the user's ask before invoking.** If the request named a voice, gender, or tone, pick a matching voice id and pass it with `--voice <id>`. The pipeline default is otherwise **Marcia (female)** on HeyGen / `am_michael` on Kokoro — so a request like "a male voice" is silently ignored unless you pass the flag. Voice ids are provider-specific; resolve against whichever provider Step 0's sign-in status selected: **HeyGen** (signed in) via `node <MEDIA_DIR>/audio/scripts/heygen-tts.mjs --list` (or `GET /v3/voices?engine=starfish`); **Kokoro** (offline) via the voice table in `<MEDIA_DIR>/audio/references/tts.md` (prefixes `am_`/`bm_` male, `af_`/`bf_` female). When the user expressed no preference, fall back to the remembered voice (brief contract § 2) before the pipeline default, and say which one you used; omit `--voice` only when neither names one. When the user explicitly picked a voice this run, record it (`prefs.mjs record --key voice`).

`node <SKILL_DIR>/scripts/audio.mjs --script ./SCRIPT.md --storyboard ./STORYBOARD.md --hyperframes . --out ./audio_meta.json --voice <voice-id> &`

The audio script handles narration, word timings, BGM lookup from HeyGen's music library, and timing metadata. BGM mood comes from the storyboard's `music:` field. This uses the HeyGen Audio API for retrieval, not generation, and the same `~/.heygen` credential as TTS. For provider details, read `../media-use/audio/references/tts.md`.

If there is no narration and no `SCRIPT.md`, skip voice generation. BGM may still run if the storyboard has a music mood.

**The canonical fully-silent marker** (shared across the workflows that reuse this audio model): `music: none` in the STORYBOARD.md top YAML block **and** no `SCRIPT.md`. That combination marks the project silent — no narration, no BGM, no SFX. `audio.mjs` recognizes it and generates nothing (it removes any stale `audio_meta.json`; an absent `audio_meta.json` is what assemble treats as silent), so this step is a clean skip. `music: none` with narration keeps TTS and turns only BGM off. Use exactly this spelling — don't improvise other markers.

Silence controls audio only. When the brief requests editable captions or caption placeholders, create `silent-captions.json` even though no `SCRIPT.md` or `audio_meta.json` exists. Use `{ "groups": [{ "frame": 1, "start": 0.0, "end": 4.0, "text": "..." }] }`; `start` and `end` are frame-relative seconds and must stay within that frame. The text may be a placeholder, summary, or approved silent subtitle. It remains independent editable HTML and may not be baked into artwork.

**Gate:** audio job has started, or the project is marked silent (`music: none` + no `SCRIPT.md`).

---

## Step 4: Frame Visual Design

Goal: Add the visual direction, layout intent, and motion choices to each storyboard frame.

**Sketch the board first (collaborative only).** The moment the plan is approved, run the sketch pass — `../hyperframes-core/references/review-loop.md` § 2 (don't wait on Step 3.1; sketches don't use timings): wireframe every frame yourself, mark each `built`, pause for the one layout question when the board is full, and revise only the sketches named until the board is confirmed. Only then write the visual design below onto the confirmed layouts. In autonomous mode, or when the user chose to skip sketches at Step 3, skip this pass — frames go straight from `outline` to `animated` at Step 5.

Edit `STORYBOARD.md` in place. Do not create another storyboard. Use `frame.md` as source of truth for color, type, layout feel, and style.

Read `references/visual-design.md`, `../hyperframes-creative/references/world-continuity.md`, `../hyperframes-animation/blueprints-index.md`, `references/motion-language.md`, and `../hyperframes-animation/rules-index.md`. Use `visual-design.md` for the method (the time-coded shot sequence, the inline Layout vocabulary, and the invented-visual treatment), plus the required `## Video direction` block. Apply world-continuity as a hard default: establish the setting, introduce the subject, show the action and interaction, then use camera movement or a state change to carry the teaching. Use `../hyperframes-animation/blueprints-index.md` to pick each frame's shot shape. Use `motion-language.md` (the motion vocabulary + the motion doctrine) and `../hyperframes-animation/rules-index.md` (valid rule names) for motion — do not invent motion names.

For every frame, write a **time-coded shot sequence** into `STORYBOARD.md` per `visual-design.md`'s method: pick the frame's blueprint (or compose), instantiate it with THIS frame's **invented or resolved visual subjects**, and pace each Scene's action to the voiceover so the frame develops across its full duration instead of front-loading then freezing. Because the explainer is faceless, `focal`/`roles` name the concrete visual elements you design or resolve — a robot, agent, building, machine, map, room, prop, or abstract subject when the idea requires it. State the setting, action, interaction, continuity anchor, camera move, and only then the supporting text inline per Scene. Add one video-wide `## Video direction` block containing the world bible and the anti-presentation negative list.

Do not change story, script, `transition_in`, or the source text. Do not write HTML in this step. Mark each frame's required environment layers, subject assets, props, vehicles, pose/state variants, and independently moving parts so Step 4.5 can produce them.

**Gate:** every frame has a time-coded shot sequence whose reveals are paced to the voiceover (no front-loading); each frame names its invented `focal` and/or `roles`; `## Video direction` exists. Collaborative: the sketch board was confirmed.

---

## Step 4.5: Illustrated Asset Production

Goal: Finish the visual asset set before HyperFrames frame HTML is authored.

For cartoon, illustrated, cutout, cel-animation, painted-background, or image-based briefs, read `../hyperframes-creative/references/image-based-cartoon-assets.md` and treat its asset-first gate as mandatory. For polished flat/cel cutout, a recurring animated guide, or subject-adaptive production across unrelated topics, also read `../hyperframes-creative/references/subject-adaptive-cutout-world.md`.

1. Write `STYLE_BIBLE.md` from the approved visual direction. Define original palette roles, outline hierarchy, flat/cel shading, texture limits, character proportions, perspective, horizon, shadow, scale, depth layers, and text safe areas.
2. Write `WORLD_ASSET_MATRIX.md`. For each narration beat map concept, physical metaphor, setting, actor, prop, target, reaction, and camera handoff. Use the current topic's vocabulary; do not seed a generic city, robot, classroom, dashboard, or reference-channel motif.
3. Write `ASSET_PLAN.md` from the confirmed storyboard and matrix. List every background, midground, foreground, character, building, vehicle, machine, prop, pose/state, and movable part by stable asset ID and frame usage.
4. Use `/media-use` to adopt suitable user/project assets and resolve licensed candidates. When they do not fit the requested original cartoon world, use available image-generation or sprite-generation capabilities to create original local assets. Do not copy reference characters, logos, palettes, poses, or distinctive compositions.
5. Store ready assets under `public/assets/`. Prefer transparent PNG/WebP for cutout subjects, layered SVG only when it is a finished illustration rather than primitive geometry, and separate environment layers for parallax.
6. Write `asset-manifest.json` with local path, dimensions, transparency, layer role, frame usage, pivot, pose/state, provenance, license/usage state, generation prompt/reference summary, and SHA-256.
7. Create an asset contact sheet and inspect style consistency, scale, perspective, outline weight, palette roles, ground line, shadow direction, and missing interaction parts.

Raw rectangles, circles, polygons, emoji, generic icons, and CSS boxes may not stand in for a named primary subject or environment asset. SVG/Paper.js remains allowed for rails, pipelines, routes, gauges, chart lines, particles, masks, highlights, and editable text/UI. If a required illustrated asset is missing, stop here and report it.

**Gate:** `STYLE_BIBLE.md`, `WORLD_ASSET_MATRIX.md`, `ASSET_PLAN.md`, `asset-manifest.json`, the contact sheet, and local files agree; every storyboard subject and interaction target maps to a ready manifest asset or an explicitly allowed graphic-support layer.

---

## Step 5: Build Frames

Goal: Build every storyboard frame as an HTML composition and assemble the playable video.

Wait for Step 3.1 audio to finish if audio was started. Then sync durations and fetch SFX; skip both if silent.

`node <SKILL_DIR>/scripts/audio.mjs sync-durations --audio-meta ./audio_meta.json --storyboard ./STORYBOARD.md`

`node <SKILL_DIR>/scripts/audio.mjs fetch-sfx --storyboard ./STORYBOARD.md --hyperframes .`

Duration sync is mechanical: real voice duration wins; silent frames keep estimates; never hand-edit synced durations.

Before dispatch, read `../hyperframes-core/references/subagent-dispatch.md`. Build the per-frame packets and the worker role payload:

`node <SKILL_DIR>/scripts/frame-packets.mjs --project "$PROJECT_DIR" --storyboard "$PROJECT_DIR/STORYBOARD.md"`

The builder writes one bounded packet per frame under `.hyperframes/frame-packets/` (the frame's exact storyboard block + the blueprint body + every cited rule recipe, inlined) and `_role.md` (`../hyperframes-core/references/frame-worker-core.md` + this skill's `sub-agents/frame-worker.md`, concatenated verbatim — the complete worker role). Dispatch one sub-agent per frame, in parallel if possible; otherwise run workers in waves. Each worker gets exactly one frame: its prompt carries `_role.md` and that frame's packet — paste both in full, or hand the two file paths for the worker to read first (equivalent; the worker starts from exactly those two documents either way) — plus a dispatch context with `PROJECT_DIR`, `frame_id`, whether the frame has a **confirmed sketch** on disk (the worker dresses that layout rather than redrawing it — frame-worker core § When a confirmed sketch exists), canvas size, and caption status + keep-out band if captions are enabled.

Workers read their packet, `frame.md`, `STYLE_BIBLE.md`, `WORLD_ASSET_MATRIX.md`, `ASSET_PLAN.md`, and `asset-manifest.json`; they never open `STORYBOARD.md` or the skill documents. Each worker writes only `compositions/frames/NN-*.html`. Workers must never edit the storyboard or regenerate approved assets. In image-based cartoon mode, workers place manifest assets with `<img>`, prepared layered SVG, or Lottie and animate wrappers/exposed parts with GSAP. They must not redraw a missing primary asset from primitive geometry.

**Full-bleed backgrounds ride on a `class="clip"` layer, never the `#root`.** A frame's ground (color field / gradient / grid) is its own full-duration background clip — a `background` set on the `#root` / `data-composition-id` element is clip-gated to the frame's window and is not a dependable ground, so dark content can land on the black host `body` and render invisible. The video's base ground is painted by the assembler from `frame.md`'s `canvas` color onto the index `#root`. (Full rule + self-check: `../hyperframes-core/references/frame-worker-core.md`.)

As each worker returns, the orchestrator marks that frame as `animated` in `STORYBOARD.md`.

After audio timings exist, build captions in the background and assemble the index:

Narrated branch:

`node <SKILL_DIR>/scripts/captions.mjs build --storyboard ./STORYBOARD.md --audio-meta ./audio_meta.json --hyperframes . --out ./caption_groups.json &`

Silent editable-caption branch:

`node <SKILL_DIR>/scripts/captions.mjs build --storyboard ./STORYBOARD.md --silent-source ./silent-captions.json --hyperframes . --out ./caption_groups.json &`

`node <SKILL_DIR>/scripts/assemble-index.mjs --storyboard ./STORYBOARD.md --hyperframes .`

`captions.mjs` uses the project's `.hyperframes/caption-skin.html` (copied in Step 2) as the caption look, injecting brand tokens from `frame.md`; with no skin present it renders the built-in default pill. `captions: skipped (<reason>)` is valid only when the approved brief does not request captions or caption placeholders. A silent preview with requested editable captions must use the silent branch and may not pass by skipping captions.

**Gate:** every frame is marked `animated` (collaborative: the sketch board was confirmed at Step 4), every primary visual maps to `asset-manifest.json`, no primitive placeholder replaced a requested illustrated asset, `index.html` exists, and captions are built or explicitly skipped only when the brief permits it. If silent editable captions were requested, `silent-captions.json`, `caption_groups.json`, and `compositions/captions.html` must exist.

---

## Step 6: Finalize

Goal: Verify the assembled video, get user approval, and render the final MP4.

Inject transitions, run checks, pause for review, then render.

`node <SKILL_DIR>/scripts/transitions.mjs inject --storyboard ./STORYBOARD.md --hyperframes .`

`node <SKILL_DIR>/scripts/transitions.mjs verify --storyboard ./STORYBOARD.md --index ./index.html`

`npx hyperframes lint`

`npx hyperframes check`

`npx hyperframes snapshot --at <frame-midpoints>`

`node <HYPERFRAMES_CLI_SKILL>/scripts/world-motion-audit.mjs --project .`

`snapshot` stitches the captured frames into one contact sheet (`snapshots/contact-sheet.jpg`). Glance at it; if nothing is obviously broken, move on — don't linger here.

If a command fails, surface stderr and stop — don't pile on recovery commands. Fix it yourself: the cheapest safe edit to `compositions/frames/NN-*.html`, then rerun the failed check.

**Known false-positive — do not chase it.** `check` may report a handful of `text_box_overflow` findings of ~1–4px on the **caption** highlight words (selector `#caption-word-*` / `.caption-line`). The caption pill uses a deliberately snug `line-height` (set once in `scripts/captions.mjs`) and has **no `overflow:hidden`**, so a heavy display glyph's ink spills a few px into the pill's own padding — nothing is actually clipped. Treat these as expected and proceed. Do **not** inflate the caption `line-height` (it balloons the pill, which is worse). Only act on a `text_box_overflow` when it names a **frame** element (`#el-NN-*`), not a caption word.

After checks pass, pause for user review — the review loop's final look (`../hyperframes-core/references/review-loop.md` § 4): one question, on the Studio that has been open since Step 3 — render now, or what changes? (Autonomous: the one kept question, preview first or render.) Then deliver the MP4 with the contact sheet and the frame ids so revisions can target a single frame.

Preview: start Studio in the background, then hand the exact URL to the user: `node <HYPERFRAMES_CLI_SKILL>/scripts/start-preview.mjs --project . --port <available-port>`. Its `url` is the editable Studio URL; `.hyperframes/preview.json` records the port and relaunch command. Keep the server running through the review. Do not give only an MP4 path, `index.html`, a screenshot, or a `play` URL.

Render only after user approval (autonomous mode: after the preview-or-render question):

`npx hyperframes render --skill=faceless-explainer --quality high --output renders/video.mp4`

Do not rerun `lint`, `check`, or `snapshot` after rendering unless the user asks.

**Gate:** `lint` and `check` passed and the snapshots were inspected before render; user approved at the review pause (autonomous: checks passed and the delivery includes the contact sheet); `renders/video.mp4` exists. Final reply states MP4 path and final duration.

---

## Quick Reference

**Formats:** landscape `1920x1080`; portrait `1080x1920`; square `1080x1080` — derived from the destination (brief contract § 2). Set the format once in the storyboard frontmatter.

**Faceless deltas vs a captured-asset workflow:** no website capture is required. In image-based cartoon mode, visuals are planned in Step 4, generated/resolved in Step 4.5, registered in `asset-manifest.json`, and only then composed by Step 5 workers. Workers invent choreography, not substitute artwork. Typography, diagrams, and data-viz remain supporting treatments.

World-first delta: when the source names concrete subjects, the storyboard records them and the asset pass creates or resolves environments, characters, objects, and interaction parts before frame authoring. Typography, abstract graphics, diagrams, and data-viz remain valid for abstract beats or supporting evidence, not as default replacements for concrete topics.

**Background scripts:** the workflow ships only these under `scripts/`: `build-frame` for adopting + brand-remixing a frame preset into `frame.md` (+ caption skin); `audio` for TTS, transcription, BGM, SFX, and duration syncing; `captions`; `transitions` for inject and verify; and `assemble-index`. Everything else is the `hyperframes` CLI.

The reusable, domain-agnostic shot shapes live in `../hyperframes-animation/blueprints/` (indexed by `../hyperframes-animation/blueprints-index.md`).

| Read                                                                                                                                                        | When                                                                           |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| `[../hyperframes-core/references/brief-contract.md](../hyperframes-core/references/brief-contract.md)`                                                      | Gate types, mode derivation from `BRIEF.md`, field semantics.                  |
| `[../hyperframes-creative/references/story-spine.md](../hyperframes-creative/references/story-spine.md)`                                                    | Step 3: story doctrine — hook language, value-before-evidence, proposal shape. |
| `[../hyperframes-creative/frame-presets/](../hyperframes-creative/frame-presets/)`                                                                          | Step 2: choose and adopt a frame preset.                                       |
| `[../hyperframes-creative/references/design-spec.md](../hyperframes-creative/references/design-spec.md)`                                                    | Step 2: apply brand tokens correctly.                                          |
| `[references/story-design.md](references/story-design.md)`                                                                                                  | Step 3: plan the explainer story.                                              |
| `[../hyperframes-animation/blueprints-index.md](../hyperframes-animation/blueprints-index.md)`                                                              | Step 3: role→blueprint menu. Step 4: pick the shot shape.                      |
| `[../hyperframes-core/references/storyboard-format.md](../hyperframes-core/references/storyboard-format.md)`                                                | Step 3: write `STORYBOARD.md`.                                                 |
| `[../hyperframes-core/references/script-format.md](../hyperframes-core/references/script-format.md)`                                                        | Step 3: write `SCRIPT.md`.                                                     |
| `[../media-use/audio/references/tts.md](../media-use/audio/references/tts.md)`                                                                              | Step 3.1: choose or understand TTS providers and voices.                       |
| `[references/visual-design.md](references/visual-design.md)`                                                                                                | Step 4: write the frame's shot sequence (+ Layout vocabulary).                 |
| `[../hyperframes-creative/references/subject-adaptive-cutout-world.md](../hyperframes-creative/references/subject-adaptive-cutout-world.md)`                  | Step 4.5: style bible, world-asset matrix, guide rig, and asset gate.          |
| `[references/motion-language.md](references/motion-language.md)`                                                                                            | Step 4: the motion vocabulary + the motion doctrine.                           |
| `[references/cut-catalog.md](references/cut-catalog.md)`                                                                                                    | Step 4-5: the cut catalog (worker builds within-frame seams).                  |
| `[../hyperframes-animation/rules-index.md](../hyperframes-animation/rules-index.md)` + `[../hyperframes-animation/rules/](../hyperframes-animation/rules/)` | Step 5: local rule recipe bodies for the cited motions.                        |
| `[../hyperframes-core/references/frame-worker-core.md](../hyperframes-core/references/frame-worker-core.md)`                                                | Step 5: the shared worker contract (packet builder prepends it to the delta).  |
| `[sub-agents/frame-worker.md](sub-agents/frame-worker.md)`                                                                                                  | Step 5: the workflow's frame-worker delta.                                     |
| `[../hyperframes-core/references/subagent-dispatch.md](../hyperframes-core/references/subagent-dispatch.md)`                                                | Step 5: dispatch sub-agents safely.                                            |
