---
name: audit-faceless-video
description: Audit a faceless-video candidate before publication without changing production artifacts. Use to compare scripts, check asset rights and voice consent, detect slideshow-like/frozen motion, verify independent image layers and interactions, detect primitive-placeholder output that violates an image-based cartoon brief, and prepare a PASS, REVIEW, BLOCK, or INCOMPLETE release-readiness report.
---

# Audit Faceless Video

Perform a conservative, read-only risk screen. Treat the result as workflow evidence, not as a legal opinion, copyright ruling, consent determination, or permission to publish.

## Preserve the audit boundary

- Read the candidate script, reference transcripts, manifest, and production media without modifying, renaming, deleting, rendering, or replacing them.
- This skill never creates, repairs, or re-renders a video. If the request is to make a faceless motion-explainer from a script, stop the audit and hand off to `produce-original-faceless-video` (approval-gated package) or `faceless-explainer` (direct HyperFrames project). Return to this skill only after a candidate export exists.
- Do not use a passing or failing audit as a creative brief. The audit may identify a slideshow-like candidate, but its only remedy is a new production pass; it must not silently replace the candidate with slides, cards, or a new render.
- Write only the requested audit JSON to a distinct output path. Refuse an output path that resolves to any input path.
- Never rewrite suspicious passages, repair metadata, change assets, or publish from this skill. Report remediation actions for a separate production step.
- Keep every manual check `NOT_EVALUATED` until a human or an explicitly authorized review process records evidence.

## Run the deterministic screen

1. Collect one candidate script, at least one comparison transcript, the corresponding `production-manifest.json`, and a separate output path.
2. Read [references/audit-policy.md](references/audit-policy.md) before interpreting manifest fields or status thresholds.
3. Run:

```powershell
python scripts/audit_originality.py `
  --candidate path/to/candidate-script.md `
  --reference path/to/reference-a.txt `
  --reference path/to/reference-b.json `
  --manifest path/to/production-manifest.json `
  --output path/to/audit-report.json
```

4. Inspect the JSON even when the command exits nonzero. Interpret exit codes as `0=PASS`, `1=REVIEW`, `2=BLOCK`, and `3=INCOMPLETE`.
5. Preserve the recorded input hashes, policy version, thresholds, issues, and phrase excerpts when handing off the report.

Run the deterministic motion screen on the actual rough or final export:

```powershell
python scripts/audit_motion.py `
  --video path/to/candidate.mp4 `
  --output path/to/motion-audit.json
```

Inspect the motion JSON even when it returns `1=REVIEW` or `3=INCOMPLETE`. Record its workspace-relative path and SHA-256 in `manifest.motion_quality`. The screen measures meaningful frame change, distributed motion, scene cuts, and static runs. It cannot prove independent layer motion or interaction, so it never replaces manual playback.

Accept UTF-8 text/Markdown or JSON transcripts. For JSON, extract transcript-like fields such as `transcript`, `text`, `content`, `script`, `captions`, or segment text. Pass `--reference` repeatedly; do not concatenate reference files manually.

## Complete the manual gate

Do not change the automated status to PASS merely because the numeric overlap is low. Review and record evidence for all four gates:

- Compare visual identity, shot order, composition, thumbnails, characters, logos, color treatment, and distinctive transitions for confusing similarity.
- Verify factual claims against primary or authoritative sources and record citations or timecodes; treat a source list alone as unverified.
- Check whether synthetic voice, generated imagery, reenactment, or materially altered media needs platform- or audience-facing AI disclosure.
- Play the complete export and check sync, captions, pronunciation, clipping, loudness, black frames, encoding, safe areas, and final duration.
- Verify motion quality separately: camera movement over a flattened still does not count as animation. Check that subjects, backgrounds, particles/diagrams, and depth layers move independently and that explanatory shots contain visible cause-and-effect interaction. If the manifest names `hyperframes-local`, trace the ready render to its declared local export and shot-to-composition mapping when supplied; renderer use is provenance only, never proof of motion quality.
- Verify content fit and world continuity: the environment, characters, objects, and interactions must be grounded in the candidate's own script/topic. Do not treat an AI/robot/code/dev motif, or any other repeated reference motif, as a required visual vocabulary. Flag generic preset subjects that replace the source's actual domain, and check that adjacent shots preserve a meaningful world/subject/state anchor where the story requires continuity.
- Verify requested visual-medium fit. When the approved brief requires cartoon, illustrated, cutout, cel-animation, painted-background, or image-based assets, inspect `STYLE_BIBLE.md`, `WORLD_ASSET_MATRIX.md`, `ASSET_PLAN.md`, `asset-manifest.json`, the asset contact sheet, and representative frames. Confirm that primary characters, buildings, vehicles, props, and environments are real manifest-backed image assets and that HyperFrames only composes/animates them. Flag rectangles, circles, polygons, emoji, generic icons, CSS boxes, or crude procedural silhouettes used as finished substitutes.
- Verify asset layering: background/midground/foreground are separate when parallax or environmental motion is claimed; cutout subjects expose the parts needed by the storyboard action; a single flattened image plus camera motion does not satisfy the asset or motion contract.
- Verify subject-adaptive style consistency: the recurring guide remains visually coherent while each topic receives script-grounded environments, actors, props, buildings, vehicles or machines, and reaction states. Flag a generic asset pack reused across unrelated topics or a reference channel's surface nouns carried into the candidate.
- Verify the contact sheet against the style bible for silhouette, outline hierarchy, cel shading, texture, perspective, horizon, ground line, shadow direction, palette role, character proportion, and scale. Treat material mismatch as `REVIEW`, not as a harmless polish issue.
- Verify cutout pacing in playback: actor and target change independently, the focus evolves roughly every 3-5 seconds where the brief adopts that cadence, and short holds retain a semantically related micro-motion. Do not require unrelated ambient loops.
- Verify editable text requirements: captions and fact labels must remain independent text layers when the approved workflow promises drag-and-drop editing; baked labels or labels coupled to an unrelated moving layer require review.
- For a silent preview that requests editable captions, require `silent-captions.json`, `caption_groups.json`, and the rendered captions composition; silence is not evidence that captions were intentionally skipped.

Keep the overall release gate open until the manual checks are completed outside the script. Escalate uncertain licenses, fair-use claims, likeness or voice rights, and jurisdiction-specific questions to qualified reviewers.

## Apply the status conservatively

- Treat `BLOCK` as a stop signal for strong text-copy evidence, explicitly disallowed commercial use, a denied or revoked license, or an unconsented real-person voice clone.
- Treat `INCOMPLETE` as missing or unreadable evidence that prevents a reliable screen, including incomplete asset inventory, absent provenance/license data, or unresolved voice-consent fields.
- Treat `REVIEW` as a material risk that needs human judgment, including moderate overlap, long matching phrases, unfamiliar licenses, fair-use claims, or a consented real-person clone.
- Treat `PASS` only as passing this automated policy with complete machine-readable evidence. Require all manual gates before publication.

Treat missing `manifest.motion_quality`, a missing motion report, or pending manual motion review as `INCOMPLETE`. Treat failed motion thresholds, long frozen holds, excessive camera-only time, or slideshow-like rendering as `REVIEW` and require a new production render.

For an image-based cartoon brief, treat a missing/unreadable style bible, world-asset matrix, asset plan, asset manifest, contact sheet, or required asset files as `INCOMPLETE`. Treat systematic primitive-placeholder substitution, style drift across asset batches, generic cross-topic asset reuse, flattened-scene motion, baked editable labels, or a renderer-built vector infographic replacing the approved illustrated medium as `REVIEW` and require a new asset-production/composition pass.

Report the highest-severity status, the concrete issue codes, the affected references/assets, and the next evidence needed. Do not assert that another channel infringes copyright and do not describe the result as legally cleared.
