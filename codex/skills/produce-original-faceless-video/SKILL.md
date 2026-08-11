---
name: produce-original-faceless-video
description: Produce an original, source-backed, animation-forward faceless motion-explainer package from channel-profile.json plus a topic, duration, language, aspect ratio, and image_only or image_video mode. Use when Codex must create a continuous world with interacting subjects, generated or resolved image-based cartoon assets, layered environments, a motion storyboard, rough/final renders, and an auditable manifest, optionally animated through local HyperFrames without copying a reference identity or publishing without approval.
---

# Produce Original Faceless Video

Create an original production package. Treat the channel profile as constraints and inspiration, never as a script, identity, logo, voice, or shot list to copy.

## Initialize the workspace

Collect a completed analyzer `channel-profile.json`, topic, duration in seconds, language, aspect ratio, and mode. Accept only `image_only` or `image_video`. Reject draft, ungrounded, malformed, or copying-unsafe profiles before creating a workspace.

Run:

```text
python scripts/production_workspace.py init --output <workspace> --channel-profile <channel-profile.json> --topic "<topic>" --duration-seconds <seconds> --language <language> --aspect-ratio <W:H> --mode <image_only|image_video>
python scripts/production_workspace.py validate --workspace <workspace> --stage structure
```

Do not overwrite a non-empty workspace. Revalidate the copied profile on every `validate` run to catch tampering. Read [production-schema.md](references/production-schema.md) before editing the generated JSON files.

## Follow the gated workflow

1. Inspect the brief and profile. Extract reusable constraints such as pacing, audience, format, color direction, and shot density. Derive the new video's world, setting, subjects, props, and visual metaphors from the current topic and source-backed script; never seed a default AI/robot/code/dev or other domain. If sibling `hyperframes-motion-brief.md` or `visual-style-brief.md` files are supplied, use only their evidence-backed abstract motion and art grammar. Record whether the reference is montage-driven or spatially continuous; do not inherit montage cuts when the approved brief requires one world. Exclude protected identity, distinctive wording, logos, characters, thumbnails, palettes, compositions, and voice likeness.
2. Draft `concept.json`. Make the premise, hook, viewer promise, angle, structure, and differentiation original. Register each factual claim in `production-manifest.json` with at least one source.
3. Present the concept. Stop until the user explicitly approves it. Record the approval in both the concept status and `checkpoints.concept`, then validate `--stage concept`.
4. Draft `script.json` and `storyboard.json`. Label every script segment as factual, creative, or opinion. Attach `claim_ids` to every factual segment and shot. Before writing shots, derive the required `storyboard.world` contract from the topic and script: setting, subject roster, props, action verbs, continuity anchors, and camera space. Set `visual_grammar` to `world_motion_explainer` and `presentation_allowed` to `false` unless the user explicitly asked for a presentation. Every shot must identify its setting, participating world-subject IDs, action, interaction target/event, and continuity anchor, as well as a complete `motion_design` plan with independently animated layers, environment motion, subject motion, interaction beats, and an implementation method. A shot that cannot name a subject acting on a target is not ready to build. Open every cited source, record claim-level support evidence, and complete the manual claim audit. Remove unsupported claims; do not treat structural validation as proof of truth.
5. Present the script and citation map. Stop until approval. Record `checkpoints.script`, then validate `--stage script`.
6. Discover only tools and providers actually available. Read [provider-adapters.md](references/provider-adapters.md). When the local HyperFrames skills and CLI are available, read [hyperframes-local-adapter.md](references/hyperframes-local-adapter.md) and add the `hyperframes-local` render adapter; otherwise record it as blocked rather than inventing a fallback. Do not invent an endpoint, model, price, credential, or capability.
7. Populate the provider plan and budget estimate, including uncertainty and contingency. Present it. Stop before any paid call or external API call unless the matching adapter IDs, cumulative cost limit, and `checkpoints.budget` are explicitly approved. Never store credential values; store environment-variable names only.
8. Produce assets in the selected mode. When the brief requests cartoon, illustrated, cutout, cel-animation, painted-background, or image-based visuals, read `../hyperframes-creative/references/image-based-cartoon-assets.md` and make it the asset contract. For a polished flat/cel cutout direction, recurring animated guide, or multi-topic subject-adaptive format, also read `../hyperframes-creative/references/subject-adaptive-cutout-world.md`. Create `STYLE_BIBLE.md`, `WORLD_ASSET_MATRIX.md`, `ASSET_PLAN.md`, `asset-manifest.json`, an asset contact sheet, and actual local image files before authoring HyperFrames frame HTML. Generate or resolve illustrated characters, objects, buildings, vehicles, props, and layered backgrounds; split them into independently animatable environment, subject, prop, effect, and text layers. Do not substitute raw rectangles, circles, polygons, generic icons, or CSS boxes for a required illustrated asset. `image_only` still requires local subject/environment motion and does not permit a static slideshow. In `image_video`, mix layered stills and motion clips when supported. Record provenance, license, generation settings, local path, pivot, state or pose, and SHA-256 for every ready asset.
9. Pass the asset gate before composition. Every storyboard subject and interaction target must map to a ready manifest asset or an explicitly allowed graphic-support layer such as a rail, pipeline, route, gauge, chart line, particle, mask, or editable text/UI. Confirm the style bible, topic-to-world matrix, asset plan, manifest, contact sheet, and local files agree on silhouette, perspective, outline hierarchy, palette roles, scale, interaction states, and movable parts. If a required asset is unavailable, stop and report it; never let the renderer invent a primitive placeholder.
10. Use only a clearly synthetic TTS voice, the user's own recording with consent, or no narration. Refuse to clone or imitate any real person's voice. Keep `voice.real_person_clone` false.
11. Render an 8–15 second representative motion proof before the full rough. With HyperFrames, run its local lint/check/snapshot sequence and `world-motion-audit.mjs` before rendering the proof. Reject it if it relies on camera movement alone, flattened backgrounds, primitive placeholder subjects, cuts between static frames, or an audit BLOCK. Then render the rough, run motion QA, present it, and stop for `checkpoints.rough`. Apply approved revisions only.
The representative proof must show a context-appropriate focal subject, its environment, and an explanatory interaction; it does not require a character when the topic is better represented by places, objects, systems, events, or abstractions. Derive the subject from the approved topic and script.

12. Render the final cut, validate `--stage final`, and present it for `checkpoints.final`. Keep publishing manual and outside this workflow. Never auto-upload, schedule, or publish.

## Enforce animation-forward motion

Read [motion-standard.md](references/motion-standard.md) before drafting the storyboard or selecting providers.

The animation standard is domain-neutral: it requires a continuous, context-appropriate world and visible relationships, but it does not prescribe a subject type. The current topic decides whether the actors are people, animals, objects, places, systems, events, or abstractions.

- Keep meaningful local motion inside shots. A zoom, pan, crop, parallax-free push, crossfade, or scene cut alone does not count.
- Animate at least two independently moving visual layers per shot. Use subject, environment, particles, diagram elements, foreground, midground, or background layers as appropriate.
- Give explanatory shots a visible cause-and-effect interaction: point and reveal, tool and result, object and reaction, input and transformation, or action and environmental response.
- Animate characters with position, pose, gesture, face, squash/stretch, secondary motion, or reaction. Bobbing a flattened character sticker is insufficient by itself.
- Keep camera-only or static treatment below the manifest limits. Never stretch one flattened image across a long narration segment.
- Prefer layered 2D, vector animation, rigs, masks, particles, procedural diagrams, or verified video generation. Use Ken Burns motion only as a short supporting treatment.

Populate `manifest.motion_quality` from the rendered file. Run the deterministic motion screen and then manually verify independent layer motion and interaction because frame-difference metrics cannot distinguish a full-frame camera pan from real object animation.

## Orchestrate local HyperFrames safely

Use HyperFrames as an optional local render runtime, not as a replacement for this skill's approvals or production records. Read `hyperframes-core`, `hyperframes-animation`, and `hyperframes-cli` when their instructions apply; use `faceless-explainer` only for its composition and motion techniques. This skill remains the source of truth for the original concept, citations, rights, manifest, and all checkpoints.

- Prefer GSAP timelines for 2D explanatory scenes. Use Three.js only when the original storyboard needs real depth, camera movement, particles, or shaders; never add it merely to imitate a reference.
- In image-based cartoon mode, HyperFrames is the compositor and animation runtime. Place approved PNG/WebP/layered SVG/Lottie assets and animate their wrappers or exposed parts; do not redraw missing primary assets with SVG primitives.
- For subject-adaptive cutout worlds, keep the recurring guide visually consistent while regenerating environments, props, buildings, vehicles, machines, and secondary characters from the current topic. Treat a fictional animated guide as compatible with faceless production; faceless forbids a real talking-head presenter, not an original drawn face.
- Target frequent local motion with a visual-focus change roughly every 3-5 seconds. During explanatory holds, keep one semantically related micro-motion active; reserve tracking and parallax for real subject or camera travel.
- Give each shot a stable composition ID matching `storyboard.json`, a paused/seek-safe timeline, at least two independently animated layers, and a visible interaction or environmental response where the shot explains a process.
- Before the proof, write `hyperframes/world-motion-proof.json`. Map each storyboard shot to its composition ID, environment layers, subject layers, interaction actor/target/event, and proof timestamps. Do not render while this mapping is incomplete or says `presentation_allowed: true` for a non-presentation brief.
- Keep the HyperFrames world content-specific. Reuse the same environment, subjects, props, and state across adjacent shots only when the approved storyboard says they belong to the same world; do not reuse a fixed asset vocabulary across unrelated topics.
- Keep HyperFrames project files inside `hyperframes/`; keep exports under the existing `renders/` directory and register the rendered export with adapter ID `hyperframes-local` in the manifest.
- Do not automatically run HyperFrames `skills update`, `auth`, `cloud`, `publish`, `feedback`, remote TTS, or `media-use` catalog/generation flows. A remote or paid feature is allowed only through a separately observed provider adapter after the matching approval and budget gates.
- If local HyperFrames validation or rendering is unavailable, mark the adapter blocked and stop before claiming an animated render. Do not silently replace it with static slides, image pans, or a cloud render.
- After `check` passes and before asking for rough/final approval, launch the local Studio with `node <HYPERFRAMES_CLI_SKILL>/scripts/start-preview.mjs --project hyperframes --port <available-port>`. Hand the emitted `url` to the user and preserve `.hyperframes/preview.json` for a later edit session. Never substitute a file path, screenshot, or plain player URL for the Studio project URL.

## Enforce evidence and rights

- Prefer primary or authoritative sources. Record title, locator, publisher, dates, and verification state.
- Treat every number, date, event, quote, comparison, and real-world assertion as factual. Map it to one or more claim IDs and source IDs.
- Paraphrase source material. Do not reproduce copyrighted scripts, narration, thumbnails, or shot sequences.
- Record license terms for user-supplied, licensed, public-domain, generated, and rendered assets. Do not use an asset when its rights are unknown or incompatible with the requested use.
- Record generation provider, model, prompt, time, reference assets, and adapter ID for AI-generated assets.

## Validate each handoff

Run the narrowest applicable stage:

```text
python scripts/production_workspace.py validate --workspace <workspace> --stage concept
python scripts/production_workspace.py validate --workspace <workspace> --stage script
python scripts/production_workspace.py validate --workspace <workspace> --stage rough
python scripts/production_workspace.py validate --workspace <workspace> --stage final
```

Fix all validation errors before advancing. If a required tool, permission, source, license, or approval is missing, leave the workspace resumable and report the exact blocker.
