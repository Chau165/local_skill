# Provider adapter contracts

Use this reference only after the script checkpoint is approved. Treat adapters as contracts, not implemented integrations.

## Discover and select

1. Inspect available Codex tools and installed local commands.
2. Select only an observed capability. Prefer an already available tool, then a local command, then an explicitly configured external provider.
3. Read the provider's current official documentation before relying on input limits, model names, output formats, prices, licenses, or safety rules.
4. Record a blocked provider-plan item when a capability cannot be verified. Do not guess an endpoint or silently substitute a provider.

## Environment contract

For an external provider, document names only:

```text
<PROVIDER>_API_KEY       required secret supplied by the runtime
<PROVIDER>_MODEL         optional verified model override
<PROVIDER>_BASE_URL      optional; accept only an official/user-supplied value
```

Never read, print, copy, or write secret values into production JSON. Do not define a base URL or endpoint in this skill.

## Capability request contract

Normalize a planned invocation to:

```json
{
  "request_id": "req-001",
  "capability": "image_generation",
  "adapter_id": "adapter-001",
  "model": "verified model identifier",
  "inputs": {
    "prompt": "original prompt",
    "negative_prompt": "optional constraints",
    "duration_seconds": 0,
    "aspect_ratio": "9:16",
    "language": "vi",
    "reference_asset_ids": []
  },
  "output_directory": "assets/generated",
  "permission_scope": "approved checkpoint scope"
}
```

Use only `image_generation`, `video_generation`, `tts`, `music_generation`, `sfx_generation`, `caption_generation`, or `render`. Omit unsupported input fields instead of translating them speculatively. Reject upload, publish, scheduling, or distribution capabilities; they are outside this skill.

For a verified local HyperFrames installation, use the `hyperframes-local` `local_command` render contract in [hyperframes-local-adapter.md](hyperframes-local-adapter.md). Local use has no external API or paid-call permission requirement, but its render must still pass the budget checkpoint, motion proof, rough, and final gates. Treat any HyperFrames cloud, authentication, feedback, catalog, or remote-generation feature as a separate external adapter.

For animation-forward production, verify that the selected plan can create independently controlled local motion. Image generation alone is insufficient unless a verified render adapter can separate or rebuild layers, animate subjects and environments, and produce interaction beats. Record the animation implementation in storyboard `motion_design`; do not claim that FFmpeg zoom/pan over one flattened image satisfies the motion contract.

## Capability result contract

Normalize an observed result to:

```json
{
  "request_id": "req-001",
  "status": "succeeded",
  "provider_job_id": "observed identifier",
  "files": ["assets/generated/asset-001.png"],
  "usage": {"units": 1, "unit_name": "image"},
  "cost": {"currency": "USD", "amount": 0.0, "basis": "provider response"},
  "warnings": []
}
```

Accept only `planned`, `succeeded`, `failed`, or `blocked` status. Derive asset metadata from the actual result and verified provider terms. Hash each saved file. Never treat an estimated cost as an actual charge.

## Permission boundary

- Before a paid call, require `permissions.paid_calls.approved`, list every allowed adapter ID in the comma-separated `scope`, set a numeric cumulative cost `limit`, and approve `checkpoints.budget`.
- Before an external API call, require `permissions.external_api_calls.approved` and list every allowed adapter ID in its comma-separated `scope`.
- Stop when the estimated cumulative charge could exceed the approved limit.
- Mark an adapter `executed` only after observing its result. A ready generated/rendered asset must reference an executed adapter.
- Keep publishing outside adapters. Never expose upload, scheduling, or publishing as an automatic fallback.
