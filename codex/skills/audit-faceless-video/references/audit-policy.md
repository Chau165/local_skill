# Faceless-video audit policy

Use this policy for version `1.0`. Apply it as a conservative production gate, not as a legal standard.

## Inputs and read-only rule

Require all of the following:

- One non-empty UTF-8 candidate script.
- One or more non-empty UTF-8 comparison transcripts.
- One valid JSON production manifest.
- One audit output path distinct from every input path.

Read inputs only. Write only the audit JSON. Do not infer a license or consent from a URL, filename, provider name, payment, public availability, or a low text-overlap score.

## Text screen

Normalize text with Unicode NFKC, case-folding, and word tokenization. Compare five-word shingles and exact token sequences against each reference and against the union of all references.

Use these thresholds:

| Signal | REVIEW | BLOCK |
| --- | ---: | ---: |
| Candidate words covered by matching 5-word shingles | at least 18% | at least 40% |
| Longest exact matching phrase | at least 18 words | at least 40 words |

Report exact matches of at least 12 words as evidence, capped to a short excerpt. Treat quotations, titles, names, stock phrases, public-domain text, and necessary factual wording as context for manual review; the script cannot decide whether a match is lawful or protectable.

## Manifest contract

Prefer `assets[]`; accept `sources[]` as a legacy asset-inventory alias only when entries contain rights metadata. Require `asset_inventory_complete: true`, or accept `inventory_complete: true`. Require at least one production asset for every pre-publication video audit. Never let `original_assets_only: true` exempt an empty inventory or imply video release readiness without an auditable asset.

For the producer v1 manifest, inspect each `assets[]` item:

```json
{
  "id": "asset-001",
  "type": "image",
  "role": "scene-01",
  "local_path": "assets/scene-01.png",
  "status": "ready",
  "sha256": "...",
  "provenance": {
    "origin": "generated",
    "creator": "project team",
    "source_locator": "generation job or source URL",
    "retrieved_at": "2026-08-06T00:00:00Z",
    "license": {
      "name": "provider commercial terms",
      "terms_locator": "terms URL or evidence file",
      "commercial_use_allowed": true,
      "checked_at": "2026-08-06T00:00:00Z"
    },
    "generation": {
      "provider": "provider name",
      "model": "model name",
      "prompt": "recorded prompt",
      "generated_at": "2026-08-06T00:00:00Z",
      "reference_asset_ids": []
    }
  }
}
```

Also accept a top-level `license` object on an asset for compatibility. Require an asset identifier or locator, non-empty provenance, a named/statused license, evidence or terms locator, and an explicit commercial-use decision. For generated assets, require provider, model, prompt record, generation time, and a list of reference asset IDs.

For every `status: ready` asset:

- Require a non-empty relative `local_path`; reject absolute and drive-qualified paths.
- Resolve `local_path` against the directory containing the manifest, including symlink/junction resolution where the operating system exposes it.
- BLOCK a resolved path that escapes the manifest directory. Do not read or hash the escaped target.
- Require the resolved path to be an existing regular file.
- Require `sha256` to contain exactly 64 hexadecimal characters, hash the actual file read-only, and compare it with a constant-time digest comparison.
- BLOCK a digest mismatch. Treat a missing file or malformed digest as INCOMPLETE.

These checks bind the manifest entry to the exact local artifact under audit. They never authorize modifying the artifact.

Classify rights metadata as follows:

- BLOCK an explicit `commercial_use_allowed: false`, or a status such as `denied`, `revoked`, `prohibited`, `unauthorized`, or `unlicensed`.
- REVIEW `fair_use_claimed`, `editorial_only`, `restricted`, `custom`, or an unfamiliar license/status even when evidence exists.
- INCOMPLETE absent provenance, license name/status, terms/evidence locator, commercial-use decision, required generation metadata, a declared-incomplete or empty inventory, a ready-asset file, or a valid digest.
- Accept documented `original`, `owned`, `licensed`, `permission_granted`, `public_domain`, `cc0`, `cc_by`, `cc_by_sa`, `royalty_free`, or `stock_license` only with the required evidence and commercial-use decision. Attribution and exact license conditions remain manual checks.

Do not require copyright licenses for research-only `sources[]` entries that merely support `claims[]`; instead, keep their factual use in the manual citation gate. If both `assets[]` and research `sources[]` exist, audit rights on `assets[]`.

## Voice and consent

Require `voice.mode` and an explicit `voice.real_person_clone` boolean. Accept `voice.consent_verified` as a compact alias. Prefer:

```json
{
  "voice": {
    "mode": "tts_synthetic",
    "provider": "provider name",
    "voice_id": "voice identifier",
    "real_person_clone": false,
    "consent": {
      "confirmed": false,
      "evidence_locator": null,
      "confirmed_at": null
    }
  }
}
```

Apply these rules:

- PASS this component for `tts_synthetic` or `none` only when `real_person_clone` is explicitly false. Do not treat synthetic voice as proof that disclosure is unnecessary.
- Require confirmed consent plus evidence for `original_recording` or any real-person recording used by the project.
- BLOCK a real-person clone when consent is explicitly false, denied, or revoked.
- INCOMPLETE a real-person clone when consent or evidence is missing.
- REVIEW a real-person clone even with documented consent so identity, contract scope, provider terms, and disclosure can be checked manually.
- BLOCK any manifest that simultaneously declares a clone and `real_person_clone: false` through conflicting fields.

## Motion quality

Require a `motion_quality` object for rough/final video audits. Require:

- `status: passed`;
- non-empty `analysis_method`;
- positive `sample_rate_fps`;
- `meaningful_motion_screen_time_ratio >= 0.65`;
- `distributed_motion_screen_time_ratio >= 0.50`;
- `independent_layer_motion_shot_ratio >= 0.80` from manual review;
- `interaction_shot_ratio >= 0.60` from manual review;
- `camera_only_screen_time_ratio <= 0.15`;
- `max_static_hold_seconds <= 2.0` unless a documented intentional pause is manually accepted;
- a workspace-relative existing `automated_report_path` and matching `automated_report_sha256`;
- non-empty `manual_reviewed_by`, `manual_reviewed_at`, and `notes[]`.

The deterministic motion screen samples consecutive frames and reports meaningful pixel change, distributed grid change, probable scene cuts, and static runs. It cannot distinguish full-frame camera motion from independent object animation. Manually inspect the complete export and count flattened-image zoom/pan as camera-only.

During manual motion review, also assess **context fidelity**: subject, environment, prop, and interaction choices must come from the candidate topic/script. A world-first explainer is not allowed to satisfy the motion gate with a fixed domain preset or generic recurring objects unrelated to the source. Examples from a reference channel are evidence of style only, never mandatory assets.

When a ready rendered asset declares `generation.adapter_id: "hyperframes-local"`, retain that adapter and export linkage as provenance. If a `hyperframes/` project or shot-to-composition mapping is supplied, inspect it read-only only to trace approved storyboard shots to the rendered output. Do not treat the framework, a passing snapshot, or a project file as evidence that objects animated: playback evidence and the standard motion thresholds remain required.

Classify missing or pending motion evidence as `INCOMPLETE`. Classify failed thresholds, excessive camera-only treatment, long unapproved static holds, or slideshow-like rendering as `REVIEW`. Motion quality is a production-quality gate, not a copyright ruling.

## Status precedence and meaning

Apply status precedence in this order: `BLOCK`, `INCOMPLETE`, `REVIEW`, `PASS`.

- `BLOCK`: stop publication because this screen found a defined stop condition.
- `INCOMPLETE`: do not publish because required evidence or input is missing.
- `REVIEW`: do not publish until a qualified human resolves the risk.
- `PASS`: automated checks passed; this is not legal clearance and does not complete manual gates.

## Mandatory manual checks

Leave these four checks as `NOT_EVALUATED` in automated output:

1. `visual_similarity`: compare frames, visual grammar, thumbnails, logos, recurring characters, distinctive sequences, and overall trade dress.
2. `factual_citations`: verify every material factual claim against primary or authoritative sources and record citation/timecode evidence.
3. `ai_disclosure`: check platform rules and audience transparency for synthetic voice, generated media, or material alteration.
4. `motion_quality`: verify independent subject/environment/depth motion, visible interaction beats, and the absence of camera-only slideshow treatment.
5. `technical_qa`: watch the full export for audio/video sync, captions, pronunciation, loudness, clipping, black frames, encoding, safe areas, and duration.

Require manual evidence before release regardless of automated status.
