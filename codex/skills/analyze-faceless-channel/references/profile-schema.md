# Channel profile schema

Store the synthesized profile as UTF-8 JSON in `channel-profile.json`.

## Top-level shape

```json
{
  "schema_version": "1.0",
  "job_id": "job-...",
  "analysis_status": "complete",
  "language": "vi",
  "summary": {
    "status": "inferred",
    "claim": "The format uses fast visual proof followed by a compact explanation.",
    "evidence_ids": ["ev-001", "ev-002"]
  },
  "source_coverage": [
    {"source_id": "src-video-001", "status": "observed", "notes": "Reviewed in full."}
  ],
  "motion_profile": {
    "status": "observed",
    "evidence_ids": ["ev-motion-001", "ev-motion-002"],
    "motion_density": "continuous",
    "camera_motion_patterns": ["Slow tracking move supports the main action."],
    "subject_motion_patterns": ["The guide changes position and pose inside the shot."],
    "environment_motion_patterns": ["Particles and background elements move independently."],
    "interaction_patterns": ["A subject action triggers a visible environmental response."],
    "depth_patterns": ["Foreground, subject, and background move at different rates."],
    "static_hold_behavior": "No long static hold was observed in the reviewed intervals.",
    "adaptation_principle": "Build original scenes with continuous independent layer motion and original interactions."
  },
  "patterns": [],
  "unknowns": [],
  "originality_guardrails": {
    "mode": "pattern-transfer-only",
    "prohibited_copying": [
      "channel_name_or_handle",
      "logo",
      "banner",
      "thumbnail",
      "script_or_transcript",
      "voice_or_voiceprint"
    ],
    "requirements": [
      "create_original_brand_identity",
      "create_original_visual_assets",
      "write_original_script",
      "use_non-impersonating_voice"
    ]
  }
}
```

## Motion profile

Use `continuous`, `frequent`, `selective`, `sparse`, or `unknown` for `motion_density`. Keep all pattern arrays as arrays of concise paraphrases. Do not store source frames, character identities, or shot-recreation instructions.

When a sample video was reviewed, set `status` to `observed` or `inferred`, cite temporal evidence IDs, and describe camera, subject, environment, interaction, and depth behavior separately. Never treat a zoom, pan, crop, or transition alone as environmental animation.

Keep the profile content-neutral: observed nouns may be recorded as context, but reusable patterns and `adaptation_principle` must describe motion roles and narrative functions rather than prescribing the reference's subject matter for future videos.

Without temporal video evidence, use:

```json
{
  "status": "unknown",
  "evidence_ids": [],
  "motion_density": "unknown",
  "camera_motion_patterns": [],
  "subject_motion_patterns": [],
  "environment_motion_patterns": [],
  "interaction_patterns": [],
  "depth_patterns": [],
  "static_hold_behavior": "Unknown without temporal video evidence.",
  "adaptation_principle": "Do not infer motion from still images."
}
```

## Pattern shape

```json
{
  "id": "pattern-001",
  "category": "narrative-structure",
  "label": "Result-first hook",
  "claim": "Show the outcome before explaining the process.",
  "status": "inferred",
  "confidence": "medium",
  "evidence_ids": ["ev-001", "ev-004"],
  "adaptation_principle": "Apply the function to a new topic with an original sequence and original visuals."
}
```

Require every pattern to contain at least one valid evidence ID. Use `observed`, `inferred`, or `unknown` consistently with the evidence. Keep `adaptation_principle` abstract and original; never turn it into instructions for reproducing a source asset.

## Unknown shape

```json
{
  "topic": "retention",
  "status": "unknown",
  "reason": "No first-party retention analytics were supplied.",
  "evidence_ids": []
}
```

Keep unsupported conclusions in `unknowns`, not in confident pattern claims. Use `not-applicable` confidence only in evidence records; omit confidence from unknown profile entries.

## Completion rules

Keep `analysis_status` as `draft` while sources are unreviewed. Before setting it to `complete`:

1. Add at least one evidence record and one evidence-linked pattern.
2. Add one `source_coverage` entry for every registered source.
3. Mark each coverage entry `observed` or explain it as `unknown`.
4. Preserve every required originality guardrail exactly.
5. Complete `motion_profile`; temporal video sources may not remain motion-unknown.
6. Validate the workspace with `scripts/channel_workspace.py validate`.
