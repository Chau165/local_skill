# Evidence schema

Store evidence as UTF-8 JSON Lines in `evidence.jsonl`. Write exactly one JSON object per non-blank line and one atomic claim per object.

## Record shape

```json
{
  "id": "ev-001",
  "status": "observed",
  "topic": "hook",
  "claim": "The sample opens with a result-first visual before the setup.",
  "source_ids": ["src-video-001"],
  "locator": {"kind": "timestamp", "value": "00:00-00:05"},
  "basis_evidence_ids": [],
  "confidence": "high",
  "reason": null,
  "notes": "Paraphrased; no script text retained."
}
```

Use these fields:

- `id`: Use a unique lowercase ID matching `ev-[a-z0-9-]+`.
- `status`: Use exactly `observed`, `inferred`, or `unknown`.
- `topic`: Use a lowercase slug such as `hook`, `pacing`, `visual-style`, `narrative-structure`, `audio-style`, `publishing-cadence`, `motion-density`, `camera-motion`, `subject-motion`, `environment-motion`, `interaction-motion`, `depth-motion`, `static-hold`, `retention`, `revenue`, or `spoken-words`.
- `claim`: State one concise, paraphrased claim. Do not paste a script, transcript, title, channel name, or brand wording.
- `source_ids`: Reference IDs from `job-spec.json`.
- `locator`: For an observation, provide `kind` and `value`, such as `timestamp` / `00:12-00:18`, `frame` / `thumbnail grid row 2`, or `page-region` / `Videos tab, first six cards`.
- `basis_evidence_ids`: For an inference, reference one or more earlier evidence records that justify it.
- `confidence`: Use `low`, `medium`, `high`, or `not-applicable`.
- `reason`: Explain why an unknown cannot be resolved; otherwise use `null`.
- `notes`: Add a short audit note or use `null`.

## Status rules

Use `observed` only for a directly visible or audible fact. Require at least one valid source ID and a precise locator. Leave `basis_evidence_ids` empty.

Use `inferred` only for a conclusion derived from recorded evidence. Require at least one valid, acyclic `basis_evidence_ids` link. Do not present an inference as direct observation.

Use `unknown` when evidence is absent, inaccessible, or insufficient. Set `confidence` to `not-applicable`, provide a non-empty `reason`, and do not invent a value.

## Source and screenshot rules

Trace source IDs to the `sources` array in `job-spec.json`. Do not cite an unregistered page, image, or video.

Do not use a screenshot-only evidence chain for `retention`, `revenue`, or `spoken-words`. A single image cannot establish those claims. Keep retention and revenue unknown unless suitable first-party analytics are supplied. Use video audio or legitimate captions only to summarize spoken structure; never retain a full transcript or reproduce distinctive phrasing.

Use only temporal video evidence for motion topics. Inspect consecutive frames or playback intervals and use timestamp ranges. A single frame cannot establish movement. Separate global camera movement from subject, environment, parallax, particle, diagram, or interaction movement.

## Originality rules

Record patterns, not assets. Do not embed or reproduce a channel name, handle, logo, banner, thumbnail, script, transcript, voice sample, or voiceprint. Prefer descriptions such as "high-contrast subject-background separation" over element-by-element reconstruction instructions.
