# Subject-adaptive 2D cutout world

Use this reference when the approved direction calls for polished flat-cartoon, limited cel shading, cutout animation, illustrated environments, an animated guide, or image-based cartoon assets that must adapt across unrelated topics.

## Preserve the medium, not a reference identity

- Transfer broad relationships only: complete illustrated assets, clean silhouettes, selective outlines, restrained texture, readable layers, cutout-friendly parts, and visible action-reaction.
- Create an original guide, characters, locations, palette, typography, props, metaphors, and story structure.
- Do not copy a reference mascot, face, silhouette, color swatches, logo, composition, pose sequence, narration, voice, or extracted frame.
- Do not infer the reference's software, source asset format, or rigging method from a render.

## Build the topic-to-world matrix

Before image generation, map each narration beat through:

`narration -> concept -> physical metaphor -> setting -> actor -> prop -> target -> reaction -> camera handoff`

Create `WORLD_ASSET_MATRIX.md`. It must name the topic-specific environments, actors, props, buildings, vehicles or machines, target states, and handoff objects required by every beat. Do not reuse a generic city, technology, robot, classroom, or dashboard vocabulary across unrelated topics unless the script itself calls for it.

Start from `../templates/world-asset-matrix.md` when available.

## Write the style bible

Create `STYLE_BIBLE.md` before `ASSET_PLAN.md`. Define:

Start from `../templates/style-bible.md` when available.

- original palette roles: background field, environment, subject base, subject shadow, interaction accent, warning, ink, and text;
- outline hierarchy: strongest on focal characters and interactive props, lighter on environments;
- rendering: flat fills plus at most one or two shadow/highlight groups; low texture unless a material requires it;
- silhouette and proportion rules for guide, people, animals, objects, buildings, and vehicles;
- perspective, horizon, ground line, shadow direction, and scale references;
- background/midground/foreground separation and parallax eligibility;
- caption and fact-label safe areas.

## Generate complete illustrated assets

- A primary subject must be a complete illustrated PNG/WebP, finished layered SVG, sprite, or Lottie asset with a recognizable contour and internal detail.
- Raw rectangles, circles, triangles, polygons, emoji, generic icons, and CSS boxes are support graphics only; they may not substitute for a named character, object, building, vehicle, machine, or environment.
- Create environment plates separately: atmosphere or sky, far background, midground structures or terrain, foreground occluders, and optional effects.
- Preserve transparency for cutout subjects and record pivot points and intended scale.

## Character and guide system

- In faceless production, an original fictional guide may have a face; faceless means no real on-camera presenter or talking head.
- Prefer large readable eyes and hands, a strong silhouette, simplified anatomy, and pose families that remain clear at mobile size.
- For a recurring guide, prepare head, eyes or eyelids, mouth states, torso, upper and lower arms, hands, legs, shadow, and prop sockets when the chosen animation requires them.
- Create pose or state variants for neutral, explain, point, carry, push or pull, operate, react, and travel. Use only the variants required by the storyboard.

## Object, building, vehicle, and machine system

- Object: hero silhouette, functional detail, contact point, reaction state, and shadow.
- Building: finished exterior or interior art plus doors, windows, signage area, and interaction sockets.
- Vehicle: body, wheel groups, cabin or driver, lights, load, shadow, and optional dust or smoke.
- Machine: body, control, actuator, output, and status layer. The control action must visibly change actuator and output.
- Diagram support may use SVG/Paper.js for routes, rails, pipes, gauges, cutaway masks, labels, and highlights; the explained subject remains illustrated.

## Compose for mobile readability

- Give each beat one dominant subject and one readable interaction target.
- Keep the main action in the midground; use background for context and foreground for depth or transition.
- Reduce detail behind faces, hands, labels, and the action-to-target path.
- Use close-up for contact, medium shot for explanation, and wide shot for geography or consequence.

## Plan motion before HTML

Every explanatory beat follows:

`intent -> anticipation -> action -> contact or signal -> target reaction -> secondary consequence -> settle`

- Target frequent local motion, not nonstop full-frame motion.
- Change visual focus about every 3-5 seconds through pose, target, framing, reaction, or camera movement.
- During a hold, keep one semantically relevant micro-motion such as blink, mouth, hand, wheel, smoke, flow, light, leaves, water, or a status indicator.
- Use fixed or gentle push cameras for explanation; track a subject, vehicle, or consequence only when it leads to the next beat.
- Use parallax only during actual camera travel. A pan or zoom over one flattened image is not layered animation.
- For a continuous-world brief, connect locations with recurring landmarks, roads, routes, pipes, doors, vehicles, screens, follow-object handoffs, or foreground occluders.

## Keep text editable

- Keep subtitles and fact labels as independent HTML layers when the editor must drag or revise them.
- Put subtitles inside the lower safe area and fact labels in an upper or central safe area that does not cover faces, hands, targets, or interaction paths.
- Do not bake editable labels into generated backgrounds or character art.

## Asset gate

Do not authorize HyperFrames frame authoring until all of these exist and agree:

- `STYLE_BIBLE.md`
- `WORLD_ASSET_MATRIX.md`
- `ASSET_PLAN.md`
- `asset-manifest.json`
- asset contact sheet
- all required primary local assets and movable parts

HyperFrames owns placement, camera, compositing, masks, diagrams, text, effects, and GSAP choreography. It does not invent missing primary artwork from primitive geometry.
