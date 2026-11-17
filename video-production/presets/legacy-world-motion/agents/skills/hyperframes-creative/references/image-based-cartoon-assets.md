# Image-Based Cartoon Asset Pipeline

Use this contract when the user asks for a cartoon, illustrated, cutout, cel-animation, painted-background, or image-based world. Reference images define broad visual qualities only; never copy protected characters, logos, compositions, or distinctive shot sequences.

## Art contract

- Treat illustrated asset files as the primary visual medium. Generate or resolve actual PNG, WebP, layered SVG, sprite, or Lottie assets for named characters, buildings, vehicles, props, and environments.
- Do not use rectangles, circles, polygons, emoji, generic icons, CSS boxes, or raw SVG primitives as finished substitutes for a requested illustrated subject.
- Use SVG/Paper.js only for inherently graphic support: rails, pipelines, routes, gauges, chart lines, particles, masks, highlights, and editable text/UI.
- If a required illustrated asset cannot be generated or licensed, stop at the asset gate and report the missing asset. Do not silently fall back to primitive geometry.

## Asset-first gate

Complete these artifacts before authoring frame HTML:

1. `ASSET_PLAN.md`: list every environment, character, prop, vehicle, pose/state, and independently moving part required by each shot.
2. `asset-manifest.json`: record stable asset ID, local path, media type, dimensions, layer role, transparency, shot usage, generation/source provenance, license/usage status, prompt/reference summary, and SHA-256.
3. Local files under `public/assets/` or the workflow's declared asset directory.
4. A contact sheet or thumbnail board showing that the asset set shares one art direction.

The gate passes only when every storyboard subject and interaction target maps to a ready manifest asset or to an allowed graphic-support layer.

## Layering and animation preparation

- Split environments into background, midground, foreground, and optional atmospheric layers. A flattened background is acceptable only when no parallax or local environmental motion is required.
- Prepare cutout parts around real joints or mechanisms: body/head/arms, wheels/body/door, crane boom/trolley/hook, ship/hull/cargo, machine/body/lever/indicator, and equivalent topic-specific parts.
- Provide pose or state variants when a single rigid image cannot express the scripted action.
- Keep transparent padding tight and define a consistent ground line, scale, camera angle, palette, outline weight, and lighting direction.

## HyperFrames boundary

HyperFrames is the compositor and animation runtime in this mode. Place approved assets with `<img>`, inline a prepared layered SVG, or load Lottie; animate wrappers and exposed parts with one paused, deterministic, seek-safe GSAP timeline. HyperFrames may add camera motion, parallax, transforms, masks, particles, pipelines, diagrams, captions, and effects, but it must not redraw a missing primary asset from primitive shapes.

## Motion proof

Each explanatory beat must show:

- at least two independently moving layers;
- a subject action and a visible target/environment reaction;
- local asset motion in addition to camera movement;
- continuity of setting, subject, prop, or state across adjacent beats where the story requires it.

Reject a proof that is only a pan/zoom over one flattened illustration or that replaces illustrated subjects with infographic geometry.
