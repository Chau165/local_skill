---
name: svg-paperjs
description: Create lightweight SVG/Paper.js support graphics for HyperFrames, especially rails, pipelines, routes, gauges, chart lines, particles, masks, and procedural effects. Use for inherently graphic layers. Do not use it to replace requested image-based cartoon characters, buildings, vehicles, props, or painted environments with primitive geometry.
---

# SVG / Paper.js for HyperFrames

Use this skill to create a vector support asset; use `hyperframes` and `hyperframes-animation` to compose and animate the world.

## Routing

1. When the brief asks for cartoon, illustrated, cutout, cel-animation, painted-background, or image-based visuals, read `../hyperframes-creative/references/image-based-cartoon-assets.md` and preserve its asset-first gate.
2. Reuse or generate a suitable illustrated project asset for primary subjects and environments.
3. Write raw SVG for inherently graphic support such as rails, routes, gauges, chart lines, particles, masks, and highlights.
4. Use Paper.js for procedural or path-heavy support geometry.
5. If a required primary asset is missing, stop and report it; never create a rectangle/circle/polygon placeholder and call it finished artwork.

Paper.js is an **asset-generation** tool. It must not replace HyperFrames' composition, camera, timeline, rendering, or world-motion audit.

## Shared toolkit

Use the user-wide installation at `C:\Users\Surface\.codex\tools\motion-toolkit`; do not add `paper` to an individual video project's dependencies.

Before first use on a machine, verify it:

```powershell
npm --prefix C:\Users\Surface\.codex\tools\motion-toolkit run verify
```

Run generation scripts from that toolkit and write only the resulting SVG into the current project's `assets/` directory. Keep the project self-contained for rendering.

## Asset contract

- Give independently moving parts stable SVG group IDs, such as `body`, `wheel-front`, `wheel-rear`, `door`, and `smoke`.
- Use a meaningful `viewBox`; do not bake project-specific screen coordinates into the asset.
- Keep assets lightweight: paths and basic SVG primitives before filters, Canvas, or 3D.
- Preserve an asset's source/license record where it was reused or derived.

Example structure:

```svg
<svg viewBox="0 0 240 160" xmlns="http://www.w3.org/2000/svg">
  <g id="body">...</g>
  <g id="wheel-front">...</g>
  <g id="wheel-rear">...</g>
</svg>
```

## World-motion guardrail

Generated SVG is not proof of animation. In the composition DOM, expose the scene's background, environment, actor, and target as separate world layers, then animate their interaction with the registered seek-safe HyperFrames runtime. Do not turn the asset into a card, diagram, or slide. Before a non-presentation render, the existing `world-motion-audit.mjs` must return `PASS`.

In image-based cartoon mode, SVG/Paper.js is subordinate to the illustrated asset manifest. It may connect or augment primary assets, but it must not become the visual medium for characters, buildings, vehicles, props, or environmental scenery unless the approved asset itself is a finished layered illustration.
