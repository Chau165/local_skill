# Frame worker — faceless-explainer delta

> The shared law is the core contract above (the packet builder prepends `../hyperframes-core/references/frame-worker-core.md` to this file as `_role.md`) — read the two as one role. This file carries only what's specific to a faceless-explainer frame; you run N-up, **one frame each** — your dispatch carries exactly one packet. Tempted to add a generic GSAP / timeline rule here? Wrong home — it belongs in the core contract or `hyperframes-core`.

## Your `focal:` / `roles:` — invented elements

- `focal:` — which concrete **character, object, place, or world element** is the hero of the shot.
- `roles:` — each visual element's role: `foreground subject` / `background` full-bleed / `supporting`. In image-based cartoon mode, these roles must map to ready files in `asset-manifest.json`: illustrated characters, buildings, machines, rooms, vehicles, props, diagram-as-object assets, and layered environments. A hero word or card is supporting evidence, not the default subject.

The nouns in the preceding line are illustrative categories, not a default asset pack. Derive the actual focal subject and world from the current storyboard, source document, and script; a finance, history, health, education, or other topic must use its own domain vocabulary.

## Designing each element (faceless-explainer constraint)

**Design each element by its `roles`** (the `focal` is the hero): a `foreground subject` is the illustrated character/object/place that performs the shot's action; a `background` is the persistent world and full-bleed depth; `supporting` elements include props, interaction effects, labels, and ambient layers. Read `STYLE_BIBLE.md`, `WORLD_ASSET_MATRIX.md`, `ASSET_PLAN.md`, and `asset-manifest.json`, place the named local asset, and animate its wrapper or exposed cutout parts. Do not rebuild a manifest subject as SVG/CSS/HTML geometry. Do not replace it with a generic title, box, icon, emoji, or decorative bokeh. A `[video]` candidate renders as a muted `<video class="clip">`; an image asset renders as `<img>`; a prepared layered SVG or Lottie may be loaded when the manifest names it.

If a required asset or movable part is absent from the manifest, stop and return its stable asset ID to the orchestrator. Do not invent a primitive placeholder.

## World-first frame rules

- Establish the setting before or alongside the focal subject. Keep the world as a layered scene with background, midground, and foreground where the shot benefits from depth.
- In image-based cartoon mode, use separate approved image layers for that depth. Do not draw the environment from large rectangles, polygons, or generic silhouettes.
- Animate a clear verb from the storyboard: enter, walk, inspect, connect, activate, transform, react, deliver, or fail. Show at least one visible cause-and-effect relationship when the script describes one.
- Give the actor and the interaction target separate semantic IDs/classes, separate rendered layers, and separate timeline changes at the interaction proof time. A shared camera/world transform, an entrance of a text card, or a parent-layer tween does not satisfy this requirement.
- Put camera movement on a `.world`/viewport wrapper and subject motion on child layers. Reuse the same world/asset identity across adjacent frames when the storyboard names a continuity anchor.
- Keep text short and subordinate. A label may identify the subject or interaction; it must not replace the subject or action.
- Keep captions and fact labels as independent HTML layers when editability is required. Do not bake them into a generated image or attach them to a moving camera layer unless the storyboard explicitly makes them in-world signage.
- Pace the cutout scene across its duration: intent, anticipation, action, contact, target reaction, secondary consequence, settle. Change visual focus about every 3-5 seconds and preserve one semantic micro-motion during short holds.
- If the packet gives only a generic card/diagram for a concrete source concept, reinterpret it as an in-world prop or machine before writing HTML.
- Refuse to mark the frame complete when it is a slide/card/paragraph, lacks a visible setting or concrete focal layer, or lacks an actor-to-target interaction. Return the exact missing contract field to the orchestrator instead.
