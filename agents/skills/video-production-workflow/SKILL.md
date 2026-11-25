---
name: video-production-workflow
description: Edit supplied presenter footage or produce video from a locked script and references with continuous original voice, complete captions, timestamped illustrations and factual source checks. Use for source-faithful video production, not ordinary application development.
---

# Source-faithful video production

Follow the active project's AGENTS.md and user brief. In the active video workspace, read its `AGENTS.md`. Do not copy video rules into application projects.

1. Inventory and hash sources; identify authoritative footage/audio, locked text, required reference qualities and permission boundaries. Probe duration, fps and streams.
2. Transcribe locally with word timestamps when supported. Verify low-confidence words against audio and produce editable transcript JSON plus SRT/VTT. Preserve an uninterrupted original audio master; speech edits or synthesis require approval. Captions cover every spoken interval, including graphics. For non-Vietnamese sources preserve the original transcript and translate captions without changing claims, marking translation uncertainties.
3. Map each illustration to an exact quote/start/end. Select overlay, PiP, full frame, chart, typography, infographic, 2D or 3D only as the brief needs. Use [retained craft](references/retained-craft.md). No default cartoon/world/character style.
4. Maintain a claim ledger: quote, timestamp, ticker/issuer, units, market/timezone, source URL, retrieved_at, data_as_of, status. Separate hypothetical examples. Report errors/staleness with evidence; wait for approval on the affected factual change. Without reliable sources mark NOT VERIFIED.
5. Prefer Remotion for frame-aligned editing/captions/final composition when appropriate; use HyperFrames for selected HTML/GSAP graphics or an existing HyperFrames project. Use the installed Remotion router/captions/docs or HyperFrames contract. OpenDesign helpers can inform layout/reference contracts; no daemon is required for those helpers. Respect the selected framework.
6. Inspect caption timing/coverage, audio continuity, safe areas, Vietnamese fonts, chart logic, representative frames and transitions; render and inspect an actual short sample. Then deliver editable sources, MP4, SRT/VTT, transcript, storyboard, assets/provenance, fact notes and honest QA.

## Optional legacy world-motion preset

Only when the user explicitly selects illustrated world-motion/cartoon choreography, consult [legacy preset](references/legacy-world-motion.md). Its 2D cutout/interaction/Three.js guidance is not a global requirement. Reuse craft selectively; a reference never authorizes changing a locked script or original voice.
