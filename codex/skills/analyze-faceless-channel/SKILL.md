---
name: analyze-faceless-channel
description: Analyze a public faceless-video channel from its URL, screenshots, sample-video URLs, or local sample clips; build an evidence-grounded profile of reusable content, 2D illustration, asset, layout, camera, and motion grammar while separating observed, inferred, and unknown claims. Use for channel research, graphic-style analysis, temporal animation analysis, format reverse-engineering, or preparing an original faceless-video concept without copying another channel's identity or protected creative assets.
---

# Analyze a Faceless Channel

## Set up the workspace

Require a language, an output workspace, and at least one of: a channel URL, a screenshot, or a sample-video URL. Accept screenshot-only jobs for visual analysis. Require channel/video/transcript evidence for full content analysis.

Run:

```bash
python scripts/channel_workspace.py init WORKSPACE \
  --screenshot "SCREENSHOT_PATH" \
  --language "vi"
```

Add `--channel-url "CHANNEL_URL"`, `--sample-video-url "VIDEO_URL"`, or `--sample-video-file "LOCAL_CLIP"` when available. Repeat source flags as needed. Preserve the generated `job-spec.json`; use its source IDs in all evidence.

## Collect evidence

Read [references/evidence-schema.md](references/evidence-schema.md) before editing `evidence.jsonl`.

Inspect only sources the user supplied or public pages accessible without bypassing authentication, access controls, paywalls, or DRM. Use free/local capabilities only; do not call a paid API.

Write one atomic claim per JSONL record. Mark every claim as `observed`, `inferred`, or `unknown`. Attach a precise locator to direct observations. Ground every inference in prior evidence IDs. Record unavailable facts as unknown instead of guessing.

Treat screenshot-only input as visual evidence only. Limit it to visible layout, color, typography, recurring composition, and other directly observed visual traits. Mark content, narration, pacing, retention, revenue, and spoken words unknown unless additional suitable sources establish them. Treat retention and revenue as unknown without suitable first-party analytics. Paraphrase structural observations; do not reproduce scripts or transcripts.

## Analyze temporal motion

When any sample video is available, inspect frame sequences rather than isolated screenshots. Sample multiple intervals across the clip and record separate evidence for:

- camera movement;
- subject or character movement and pose changes;
- background and environmental movement;
- foreground/midground/background parallax;
- particles, lights, UI, diagrams, or secondary-object loops;
- cause-and-effect interaction between a subject and its environment;
- static holds, camera-only motion, and transitions.

Do not call a global zoom, pan, crop, or crossfade "background animation." Distinguish camera motion from local object motion. Record motion as abstract temporal grammar, never as instructions to recreate a protected character, shot, or sequence.

## Keep the visual grammar domain-neutral

Separate **how** the reference moves from **what** the reference is about. Record observed subject categories and settings only as evidence-backed context. In the reusable profile and HyperFrames handoff, describe roles such as subject, environment, prop, interaction, reaction, and camera relationship; never turn the reference's robots, code panels, buildings, people, charts, or other nouns into a default asset pack for a new topic.

When handing the profile to production, state explicitly that the new video's world, characters, objects, and metaphors must be derived from the new topic and script. Transfer motion grammar, pacing, depth, and interaction principles only.

## Build the profile

Read [references/profile-schema.md](references/profile-schema.md) before editing `channel-profile.json`.

Extract only abstract, reusable patterns such as pacing ranges, hook functions, narrative stages, composition principles, motion density, layer behavior, interaction timing, caption behavior, broad audio mood, duration bands, and publishing cadence. Trace every pattern to one or more evidence IDs.

Populate `motion_profile` in `channel-profile.json`. A completed analysis with temporal video evidence must not leave motion unknown. A screenshot-only or channel-page-only analysis must keep motion unknown instead of guessing.

When the local `hyperframes` and `faceless-explainer` skills are installed and usable, also create `hyperframes-motion-brief.md` beside `channel-profile.json` using [references/hyperframes-handoff.md](references/hyperframes-handoff.md). This is a renderer-neutral handoff: translate only evidence-backed abstract motion grammar into layer, interaction, pacing, and runtime recommendations. It must not contain source-frame recreation instructions, protected characters, logos, copied compositions, or a claim that the reference used HyperFrames.

When the user asks to analyze illustration, asset, environment, character, camera, caption, or animation style, also create `visual-style-brief.md` using [references/visual-style-handoff.md](references/visual-style-handoff.md). Cover illustration mode, color/outline/texture, background-midground-foreground, character/object/building/vehicle construction, composition density, camera/parallax, action-reaction, transitions/text, motion density/static holds, and subject-adaptive asset planning. Link every recommendation to evidence IDs. State whether the source is montage-driven or spatially continuous instead of assuming a continuous world from isolated frames.

Keep uncertain fields explicit. Set `analysis_status` to `complete` only after checking every supplied source and resolving or recording all material unknowns.

## Enforce originality

Create an original adaptation, not a replica. Never copy or reproduce the source channel's:

- name or handle;
- logo or banner;
- thumbnails or thumbnail compositions element-for-element;
- script, transcript, phrasing, or story sequence;
- narrator's voice, voiceprint, or impersonation.

Do not store those materials in the profile. Retain only source URLs/paths in `job-spec.json` and evidence locators needed for auditability. Describe a transferable principle in each pattern's `adaptation_principle`.

## Validate

Run:

```bash
python scripts/channel_workspace.py validate WORKSPACE
```

Fix every reported schema, evidence-link, source, or originality-policy error before handing the workspace to another skill.
