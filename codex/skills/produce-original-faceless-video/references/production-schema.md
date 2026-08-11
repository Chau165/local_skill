# Production workspace schema

## Contents

1. Analyzer handoff
2. Workspace layout
3. Shared rules
4. Brief and concept
5. Script and storyboard
6. Production manifest
7. Stage gates

## Analyzer handoff

Accept only a completed `channel-profile.json` from `analyze-faceless-channel`. Both `init` and `validate` enforce this contract:

- Require `schema_version: "1.0"`, a non-empty `job_id` and `language`, and `analysis_status: "complete"`.
- Require at least one `source_coverage[]` item. Give each item a unique source ID, `status: "observed"`, and non-empty notes.
- Require at least one pattern with ID, category, label, claim, status, confidence, adaptation principle, and one or more non-empty evidence IDs.
- Keep `originality_guardrails.mode` exactly `pattern-transfer-only`.
- Include every `prohibited_copying` value: `channel_name_or_handle`, `logo`, `banner`, `thumbnail`, `script_or_transcript`, and `voice_or_voiceprint`.
- Include every `requirements` value: `create_original_brand_identity`, `create_original_visual_assets`, `write_original_script`, and `use_non-impersonating_voice`.
- Exclude source payload fields such as channel identity, logo/banner/thumbnail data, scripts/transcripts, voice samples/voiceprints, clone instructions, and narrator identity.
- Require `motion_profile`. A completed profile with temporal video evidence must separate camera, subject, environment, interaction, and depth motion. Do not accept camera movement as a substitute for environmental animation.

Reject the handoff before writing any workspace file when any requirement fails. Revalidate `input/channel-profile.json` at every stage so a post-init edit cannot weaken the guardrails. The producer can verify that pattern evidence IDs are present, but cannot validate them against the analyzer's separate `evidence.jsonl`; preserve the analyzer workspace for that referential audit.

## Workspace layout

```text
workspace/
  input/channel-profile.json
  input/brief.json
  concept.json
  script.json
  storyboard.json
  production-manifest.json
  assets/source/
  assets/generated/
  renders/
```

Use relative paths rooted at the workspace. Keep all JSON as UTF-8 with `schema_version: "1.0"`.

## Shared rules

- Keep IDs unique within their collection. Use IDs such as `src-001`, `claim-001`, `seg-001`, `shot-001`, `asset-001`, and `adapter-001`.
- Keep timing in seconds. Make `end_seconds` greater than `start_seconds`, avoid overlaps, and stay within the brief duration.
- Use ISO 8601 UTC timestamps, for example `2026-08-06T10:30:00Z`.
- Preserve the brief's topic, duration, language, aspect ratio, and mode across all files.
- Store no API keys, access tokens, passwords, or signed URLs.

## Brief and concept

`input/brief.json` is immutable production input:

```json
{
  "schema_version": "1.0",
  "project_id": "topic-1234abcd",
  "created_at": "2026-08-06T10:30:00Z",
  "channel_profile": "input/channel-profile.json",
  "topic": "Example topic",
  "duration_seconds": 300,
  "language": "vi",
  "aspect_ratio": "9:16",
  "mode": "image_only"
}
```

`concept.json` contains `status`, `topic`, `audience`, `premise`, `viewer_promise`, `angle`, `hook_options[]`, `selected_hook`, `structure[]`, `differentiation[]`, `claim_ids[]`, and `notes[]`. Use `draft`, `pending_review`, `approved`, or `rejected` for status. Keep claim IDs empty when the concept makes no factual assertion.

## Script and storyboard

`script.json` contains `status`, `title`, `language`, `duration_seconds`, and `segments[]`. Each segment has:

```json
{
  "id": "seg-001",
  "start_seconds": 0,
  "end_seconds": 12,
  "content_type": "factual",
  "narration": "Narration text",
  "on_screen_text": "Short caption",
  "claim_ids": ["claim-001"],
  "delivery_notes": "Calm, clear"
}
```

Use `factual`, `creative`, or `opinion` for `content_type`. Give every factual segment at least one claim ID. Split mixed segments until the factual mapping is unambiguous.

`storyboard.json` contains `status`, `mode`, `aspect_ratio`, `duration_seconds`, `visual_grammar`, `presentation_allowed`, `world`, and `shots[]`. For a normal script/topic explainer, use `visual_grammar: "world_motion_explainer"` and `presentation_allowed: false`.

`world` is the binding scene contract, not optional creative prose:

```json
{
  "setting": "A topic-specific persistent place or spatial system",
  "visual_vocabulary": ["environment", "subject", "prop"],
  "subjects": [{"id": "subject-001", "role": "focal actor", "description": "Context-specific subject"}],
  "continuity_anchors": ["A prop, state, direction, or place carried between shots"]
}
```

Each shot has:

Before drafting `shots[]`, derive the world and subject vocabulary from the approved topic and script. The example names below are placeholders for schema shape only; they are not defaults and must be replaced with context-appropriate environments, subjects, props, and interactions.

```json
{
  "id": "shot-001",
  "segment_ids": ["seg-001"],
  "start_seconds": 0,
  "end_seconds": 6,
  "media_type": "image",
  "setting": "The relevant part of the persistent world",
  "world_subject_ids": ["subject-001"],
  "action": "The focal subject performs a script-grounded verb.",
  "interaction_target": "The object, subject, or environment state affected.",
  "continuity_anchor": "What persists or changes from the prior shot.",
  "visual_description": "Original visual description",
  "motion": "Slow push in",
  "motion_design": {
    "implementation": "layered_2d",
    "camera_motion": "Slow push while preserving readable labels.",
    "subject_motion": "The guide points, reacts, and changes pose.",
    "environment_motion": ["Background lights pulse independently.", "Foreground particles drift on a separate path."],
    "animated_layers": ["guide-character", "environment-particles", "background-lights"],
    "interaction_event": "The guide points and the selected tool station responds with a visible result.",
    "timing_beats": ["0.0s environment loop begins", "1.2s guide points", "1.5s station responds"],
    "loop_strategy": "Ambient layers loop with offset periods and no visible simultaneous reset.",
    "camera_only": false
  },
  "transition": "cut",
  "asset_ids": ["asset-001"],
  "claim_ids": ["claim-001"],
  "generation_prompt": "Prompt for a new asset",
  "negative_prompt": "Logos, watermarks"
}
```

Use `image`, `graphic`, or `text` in `image_only`. `image_video` may also use `video`. A final rendered video is an output asset and does not violate `image_only`.

`image_only` restricts source media; it does not authorize a static slideshow. Every production shot requires independently animated local layers and an interaction beat. A single flattened image with zoom, pan, crop, rotation, blur, crossfade, or scene transitions does not satisfy `motion_design`.

For a non-presentation brief, reject a storyboard whose world is missing, whose `presentation_allowed` is true, or whose shots cannot name setting, subject, action, target, and continuity. These are production blockers, not suggestions to make prettier cards.

## Production manifest

Use these top-level keys:

```json
{
  "schema_version": "1.0",
  "project_id": "topic-1234abcd",
  "created_at": "2026-08-06T10:30:00Z",
  "mode": "image_only",
  "aspect_ratio": "9:16",
  "duration_seconds": 300,
  "language": "vi",
  "sources": [],
  "claims": [],
  "claim_audit": {
    "status": "pending",
    "reviewed_by": "",
    "reviewed_at": "",
    "methodology": "",
    "limitations": "Semantic source relevance requires manual review"
  },
  "assets": [],
  "asset_inventory_complete": false,
  "original_assets_only": true,
  "motion_quality": {
    "status": "pending",
    "analysis_method": "",
    "sample_rate_fps": 0,
    "meaningful_motion_screen_time_ratio": 0.0,
    "distributed_motion_screen_time_ratio": 0.0,
    "independent_layer_motion_shot_ratio": 0.0,
    "interaction_shot_ratio": 0.0,
    "camera_only_screen_time_ratio": 1.0,
    "max_static_hold_seconds": null,
    "automated_report_path": "",
    "automated_report_sha256": "",
    "manual_reviewed_by": "",
    "manual_reviewed_at": "",
    "notes": []
  },
  "provider_plan": [],
  "voice": {},
  "budget": {},
  "permissions": {},
  "checkpoints": {},
  "renders": {},
  "publish": {}
}
```

### Sources and claims

Define each source as:

```json
{
  "id": "src-001",
  "title": "Source title",
  "locator": "https://official.example/item",
  "source_type": "official_primary",
  "publisher": "Publisher",
  "published_at": "2026-07-01",
  "accessed_at": "2026-08-06T10:30:00Z"
}
```

Use `official_primary`, `primary`, `secondary`, or `user_provided` for `source_type`. A locator may be a stable web URL or a workspace-relative user-provided file. Do not use a search-results URL as evidence.

Define every factual claim as:

```json
{
  "id": "claim-001",
  "text": "One atomic factual assertion",
  "source_ids": ["src-001"],
  "verification_status": "verified",
  "notes": "Directly supported by section 2",
  "evidence": [
    {
      "source_id": "src-001",
      "support_locator": "Section 2, paragraph 3",
      "support_summary": "Short paraphrase of how the source supports this claim",
      "checked_at": "2026-08-06T10:30:00Z"
    }
  ]
}
```

Use `verified`, `unverified`, or `disputed`. Do not approve a script containing a referenced unverified or disputed claim. Record a source-specific evidence locator and support summary for each claim. Set `claim_audit.status` to `manual_reviewed` only after a reviewer opens the cited material and records reviewer, time, method, and limitations. The validator checks ledger completeness and gate state; it cannot prove that a source semantically supports a claim.

### Assets

Define every planned or ready asset as:

```json
{
  "id": "asset-001",
  "type": "image",
  "role": "shot-001 background",
  "local_path": "assets/generated/asset-001.png",
  "status": "ready",
  "sha256": "64 lowercase hexadecimal characters",
  "provenance": {
    "origin": "generated",
    "creator": "AI-generated",
    "source_locator": "tool-run identifier or source location",
    "retrieved_at": "2026-08-06T10:30:00Z",
    "license": {
      "name": "Applicable provider terms",
      "terms_locator": "Stable terms document or local rights record",
      "commercial_use_allowed": true,
      "checked_at": "2026-08-06T10:30:00Z"
    },
    "generation": {
      "adapter_id": "adapter-001",
      "provider": "Observed tool or provider name",
      "model": "Observed model name",
      "prompt": "Exact production prompt",
      "generated_at": "2026-08-06T10:30:00Z",
      "reference_asset_ids": []
    }
  }
}
```

Use `image`, `video`, `voice`, `music`, `sfx`, `font`, `render`, or `other` for type. Use `planned`, `ready`, or `rejected` for status. Use `generated`, `licensed`, `public_domain`, `user_owned`, or `rendered` for origin. Set `generation` to `null` for a non-generated source asset. Record license metadata for every origin, including provider terms for generated assets and a rights record for user-owned assets. A ready production asset requires `commercial_use_allowed: true`; keep incompatible or unresolved assets planned/rejected. Calculate SHA-256 from the ready local file.

Keep `original_assets_only` true to attest that no asset was copied from the analyzed channel. Set `asset_inventory_complete` true only after every storyboard, audio, font, and render asset is listed; the rough and final gates require it.

### Motion quality

Follow [motion-standard.md](motion-standard.md). Keep `motion_quality.status` pending until the rendered file passes both deterministic frame-change analysis and manual layer/interaction review. Use workspace-relative paths and SHA-256 for the automated report. A camera pan over a flattened image may create pixel change but must be counted as camera-only during manual review.

### Provider plan, voice, and budget

Each `provider_plan[]` item records `id`, `capability`, `adapter_kind`, `adapter_name`, `env_vars[]`, `model`, `requires_external_api`, `requires_paid_call`, `estimated_units`, `estimated_cost`, `currency`, and `status`. Use `tool`, `local_command`, or `external_api` for adapter kind and `planned`, `approved`, `executed`, or `blocked` for status. Store environment-variable names only.

Use this voice structure:

```json
{
  "mode": "tts_synthetic",
  "provider": "Observed provider",
  "voice_id": "Synthetic voice ID",
  "real_person_clone": false,
  "consent": {
    "confirmed": false,
    "evidence_locator": "",
    "confirmed_at": ""
  },
  "synthetic_voice_evidence": {
    "verified": true,
    "terms_locator": "Verified provider voice terms",
    "checked_at": "2026-08-06T10:30:00Z",
    "notes": "Verified as a synthetic catalog voice, not a real-person clone"
  }
}
```

Use `tts_synthetic`, `original_recording`, or `none`. Require consent evidence for an original recording. For TTS, record evidence that the selected catalog voice is synthetic and independently licensed, and list the ready generated voice asset through an executed `tts` adapter. Never set `real_person_clone` to true.

The budget contains `currency`, `estimate_status`, `estimated_total`, `contingency_percent`, `line_items[]`, and `assumptions[]`. Each line item records provider/capability, units, unit price, subtotal, and price basis. Mark estimates as estimates; do not invent current pricing.

Permissions contain separate `paid_calls`, `external_api_calls`, and `publishing` objects. Each has `approved`, `approved_by`, `approved_at`, `scope`, and `limit`. An approval applies only to its recorded scope and limit.

### Checkpoints, renders, and publishing

Create `concept`, `script`, `budget`, `rough`, and `final` checkpoints. Each checkpoint contains `status`, `approved_by`, `approved_at`, and `notes`. Advance only after status becomes `approved` with approval metadata.

`renders.rough` and `renders.final` each contain `asset_id` and `status`. Use `not_started`, `ready`, or `rejected`.

Keep `publish.automatic` false. Record `publish.status` as `not_requested` unless a separate publishing workflow is explicitly requested. This production skill does not publish.

## Stage gates

- `structure`: require readable files, consistent brief fields, safe relative paths, valid references, and no voice cloning.
- `concept`: additionally require an approved, differentiated concept and approved concept checkpoint.
- `script`: additionally require approved timed script segments, verified citations, approved script checkpoint, and a complete animation-forward `motion_design` for every shot.
- `rough`: additionally require an approved budget checkpoint, rights-complete ready assets, an approved rough render, and passing automated plus manual motion quality.
- `final`: additionally require an approved final render, passing final motion quality, and final checkpoint. Continue to prohibit automatic publishing.
