# HyperFrames local render adapter

Use this adapter only when the local HyperFrames CLI and the installed `hyperframes-core`, `hyperframes-animation`, and `hyperframes-cli` skills are available. Read those skills before applying their project conventions.

## Manifest entry

Add this observed local-command adapter to `provider_plan` when it is usable:

```json
{
  "id": "hyperframes-local",
  "capability": "render",
  "adapter_kind": "local_command",
  "adapter_name": "hyperframes",
  "status": "planned",
  "requires_external_api": false,
  "requires_paid_call": false,
  "env_vars": [],
  "estimated_units": 0,
  "estimated_cost": 0,
  "currency": "USD",
  "model": "local-hyperframes"
}
```

Do not mark it `executed` until a local render result is observed. Keep all paid or remote HyperFrames features as separate adapters with their real cost and approval requirements.

## Project and render contract

- Create the project at `hyperframes/` inside the production workspace. `script.json`, `storyboard.json`, and `production-manifest.json` remain authoritative outside that directory.
- Map every composition ID to its storyboard shot ID. Keep a written shot-to-composition mapping in the project so an audit can trace the rendered export back to the approved storyboard.
- Use a deterministic, paused/seek-safe master timeline. A full-screen background belongs to a child composition, not the project root. Prefer GSAP; use Three.js only when the storyboard calls for genuine spatial behavior.
- Build the world from the approved topic and storyboard, not from a fixed asset pack. Preserve context-specific environment, subject, prop, and state continuity across shots when the storyboard requires it.
- Before a representative proof or a full render, use the locally available CLI to lint/check and capture a snapshot. Inspect the snapshot for layers, hierarchy, text safety, and unwanted static treatment.
- Before rendering, create `hyperframes/world-motion-proof.json` with `visual_grammar: "world_motion_explainer"`, `presentation_allowed: false`, and one entry per shot: storyboard shot ID, composition ID, environment layers, subject layers, interaction actor, interaction target, interaction event, and proof timestamps. A missing entry blocks the proof/rough/final render.
- After `check` passes, start the local editable Studio with `node <HYPERFRAMES_CLI_SKILL>/scripts/start-preview.mjs --project hyperframes --port <available-port>`. Give the emitted Studio URL to the user; retain `hyperframes/.hyperframes/preview.json` only as a relaunch record, not as evidence that a server will remain alive forever.
- Put the proof, rough, and final exports in `renders/`, then register each ready render as a `rendered` manifest asset with its actual local path, SHA-256, and `generation.adapter_id: "hyperframes-local"`.

## Hard boundaries

- Local rendering does not automatically approve the budget, rough, or final checkpoints.
- Never call `auth`, `cloud`, `publish`, `feedback`, remote TTS, or `media-use` catalog/generation commands as part of this adapter.
- Do not use a renderer label as evidence that background layers, characters, diagrams, or interactions really animate. The proof, rough, and final export must pass the producer motion standard and the independent audit.
