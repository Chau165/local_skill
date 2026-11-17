# AI Video Production — Agent Instructions

## Scope and precedence
These instructions apply only inside the AI Video Production workspace. Do not overwrite or edit `AGENTS.md` for backend, frontend, database, or other application projects. Respect higher-priority Codex instructions; inspect applicable parent `AGENTS.md` files and report conflicts rather than silently ignoring them.

## Mission
Edit existing presenter footage or produce video from user-supplied scripts and references. Preserve the speaker's intended claims, meaning, chronology, footage and original voice unless the user explicitly requests a change. Treat references as binding for specified content and visual constraints, but not as authorization to copy third-party branding or watermarks.

## Non-negotiable source fidelity
- Establish a source-of-truth inventory (input footage, audio, script, brief, reference frames, verified factual sources).
- Do not silently paraphrase, rewrite, reorder, invent, remove or embellish the speaker's substantive statements. Do not introduce new investment recommendations, prices, dates, company facts, quotations or claims.
- If requirements conflict, identify the conflict, stop the affected edits and request a decision. Continue independent, non-conflicting work.
- Separate **direct quotations / source-provided facts**, **external verified facts**, **illustrative hypothetical values**, and **AI-designed visual interpretations** in internal storyboard metadata.
- Respect the reference's aspect ratio, pacing, color palette, typography, layout, animation and composition when required; allow new visual proposals only when the user has not constrained style.

## Recorded footage editing and captions
- Preserve one continuous authoritative track of the original voice; do not dub, synthesize, time-stretch or cut speech by default.
- Use speech-to-text with timestamps and verify transcription against audio. Maintain word-level timings where possible; mark low-confidence words for manual review.
- Generate Vietnamese captions for **all spoken content**, including during full-screen animated explainer segments. Do not summarize captions. Fix punctuation/spelling only without altering meaning. Preserve ticker symbols, currency units, numbers, company names and pronunciation-sensitive terms accurately.
- Keep captions in the safe area with readable contrast and without covering essential data. Separate caption text from infographic labels; never conflate the two.
- Plan and render overlays, picture-in-picture or full-screen infographic scenes using exact timestamp ranges while preserving voice audio continuity and overall chronology.
- Do not state 100% caption accuracy unless audio has actually been checked end-to-end.

## Fact-checking, especially market content
- Identify factual claims, time references, values and calculations before making scenes. Cross-check time-sensitive material using reliable primary sources available at production time, record source URLs, retrieval times and as-of dates.
- Do not silently substitute updated market data for what the speaker said. If a claim may be false, stale, ambiguous or unverified, log its exact quote, timestamp, suspected problem, evidence and recommended correction; flag for user approval. Only modify speech or substantive infographic assertions after approval.
- Explicitly label user-provided hypothetical prices/figures as examples where necessary to prevent them from being misread as live market facts.
- If web access or trustworthy sources are unavailable, state verification was not completed; do not claim real-time checks.

## Technology and skill use
- Audit the locally installed HyperFrames skills and all Codex skill directories before installation or updates. Compare local files and instructions to the upstream GitHub repository/version/commit. Detect prior custom prompts, example scenes, styles and prohibitions.
- Preserve useful general video practices but remove **only after backup and justified review** any hard-coded exclusive character, explainer-world, cartoon or visual-style constraints that conflict with future per-video direction. Never delete user customizations unconditionally.
- Prefer Remotion for composition/editing, timeline alignment, captions and full-video exports; HyperFrames for suitable HTML/CSS/GSAP graphics; OpenDesign only for actual needed design-system / MCP capabilities. Validate actual versions and Codex compatibility; use no redundant framework by default.
- Never install an entire third-party application globally merely because its repo contains skills. Inspect SKILL.md, scripts, permissions, install instructions and package versions for supply-chain risk before installing.
- Keep shared skills generic; put video-specific design choices in project templates or per-video briefs. Maintain a manifest of skill origins, local patches, commit hashes and update dates.

## Required workflow
1. **Inspect**: check toolchain, all applicable AGENTS.md, installed skills, code, user footage and references; produce environment and input reports.
2. **Transcribe**: extract media metadata, create word-timed transcript, verify low-confidence segments, produce editable SRT/VTT/JSON.
3. **Analyze**: break transcript into meaning units, propose scene types and storyboard linked to exact quotes and timestamps. Respect the user's requested presentation style.
4. **Verify**: build a claim ledger with verified/unverified/conflicting facts and timestamps. Escalate material inaccuracies before producing misleading scenes.
5. **Build**: generate reusable components; sync overlays to frames/time; preserve original voice; retain captions across all scenes.
6. **QA**: preview representative frames and every scene transition; inspect caption coverage, audio continuity, frame boundaries, typography, layout, financial figures, labels and render warnings. Iterate until checks pass or openly report limitations.
7. **Deliver**: output MP4, caption files, transcript, storyboard/timeline data, source code, fact-check notes, render commands and concise QA report.

## Change safety
- Run an audit and create timestamped, restorable backups before updating existing skills or configurations. Preserve a before/after diff.
- Do not edit or delete existing unrelated AGENTS.md, backend code, shared configs or unrelated skills.
- For risky global or destructive actions, report affected paths and obtain explicit confirmation before applying. Prefer incremental, reversible changes and dry-runs.
- Avoid exposing secrets and do not upload private footage or audio to third parties without explicit approval.

## Done means
- Source content fidelity documented; voice uninterrupted; all spoken words represented in captions subject to acknowledged transcript uncertainties.
- Each graphic justified by a timestamped quote and backed by a valid numerical/factual source or clearly marked hypothetical example.
- No hard-coded style is imposed unless selected by the user. Deliverables render successfully and remain editable.


## Workspace-specific implementation notes
- These video rules apply only below this workspace. Global guidance on concise investigation, minimal changes, evidence, backups and external actions remains in force. Development-only test coverage and API/database procedures are irrelevant to a media-only task; use the media QA below. Never edit the global AGENTS.md to make a video task fit.
- The user's supplied footage, words and explicitly constrained reference choices take priority over generic creative examples in installed skills. A storyline/pitch exercise must not rewrite an existing script. Preserve original speech even through full-screen graphics. Do not insert synthetic silence, time-stretch, replace or splice the voice track without explicit approval.
- Caption all Vietnamese speech verbatim, with permitted punctuation-only cleanup. Keep a word-timed original transcript. If source speech is another language, preserve its original transcript and create full Vietnamese translated captions with the same claims; flag uncertain translations instead of inventing words. Never fabricate word timings when a tool returns only segment timing; report missing alignment.
- `input/` and `references/` are source inputs: do not modify the user's originals. Freeze hashes and use derived media under assets/. A no-footage smoke demo must be labeled as synthetic and cannot establish speech/caption accuracy.
- Hypothetical sample figures must carry the visible label "Ví dụ minh họa"; they are not a stock price feed. Factual notes record exact quote, timestamp, issuer/ticker, market, date/timezone, value/unit, source, retrieved_at and data_as_of. Mark unavailable checks NOT VERIFIED. Stop only the affected content correction while waiting for user approval.
- Tool choice is per task: Remotion for editing/timeline/captions, HyperFrames for appropriate HTML animation, and OpenDesign functional helpers for design guidance. No app, paid provider, external upload or fixed cartoon/3D preset is mandatory. Optional preset: templates/presets/legacy-world-motion.md.
- Use scripts/Invoke-HyperFrames.cmd for the audited CLI after provisioning local dependencies as described in README.md. Do not run skill updaters over local patches without new backups and reviewed diffs. Runtime/framework packages belong to a concrete video project, never global skills.
- Working directories: input/, references/, scripts/, transcripts/, storyboard/, assets/, src/, templates/, output/, reports/, backups/. For each real job keep a brief, input manifest, timestamped storyboard, claim ledger, transcript JSON, SRT/VTT, scene/source files, local asset ledger, MP4, reproduction commands and QA report.
- QA reports distinguish structural checks, sampled visual inspection, full playback and full audio verification. Coverage metrics compare caption intervals with actual speech intervals; do not equate a caption on every scene with every spoken word covered. Check audio gaps against the original voice track and decode the final render for errors.

- Legacy `faceless-explainer` / `produce-original-faceless-video` and archived world-motion audits are for explicitly requested illustrated/faceless production. A text document or transcript alone does not select that style. Generic footage, charts, captions and motion graphics use the source-faithful workflow without world/character gates.
