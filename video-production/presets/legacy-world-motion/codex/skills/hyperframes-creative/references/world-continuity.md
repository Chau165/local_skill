# World-continuity motion-explainer direction

Use this direction by default when a user provides an article, document, notes, or script and asks for an explainer video, unless they explicitly ask for a presentation, slide deck, infographic, dashboard, or UI-first treatment.

The output is a motion-explainer: a continuous visual world in which environments, characters, objects, and camera space carry the teaching. HyperFrames is still the renderer and timeline system; this document defines the creative default that the storyboard and frame workers must follow.

## Domain neutrality is mandatory

The world is **not** a preset. Do not seed an AI, robot, code, developer, corporate, sci-fi, economic, political, medical, or any other default setting. Derive the setting, subject roster, props, visual metaphors, and interaction verbs from the user's topic, source document, and script. Examples in this document are semantic categories only; they are never required assets. A finance story may need traders, shops, ledgers, factories, or markets; a history story may need people, places, documents, or events; another topic must produce its own visual vocabulary.

## Build a world before building frames

Derive a small world bible from the user's source material:

- **World:** persistent setting, visual language, lighting, palette roles, depth layers, and the camera's coordinate space.
- **Subject roster:** concrete nouns from the script become characters, props, machines, buildings, locations, or interface-like objects. Give each a stable visual identity and role.
- **Action verbs:** for every beat, identify what a subject does: enters, searches, connects, opens, travels, transforms, reacts, delivers, or fails.
- **Continuity anchors:** keep at least one environment, character, prop, camera direction, or state from the previous beat so the video feels like one film rather than unrelated slides.
- **Asset plan:** prefer a real visual subject (illustration, PNG/SVG cutout, Lottie, 3D object, photograph, or video) when the source names a concrete entity. Generate or resolve assets when the project needs them. Use abstract shapes only when the idea is genuinely abstract or no concrete metaphor is clearer.

Never copy the surface nouns of a reference channel into a new topic. Transfer motion grammar and interaction principles; re-author the world and assets for the current content.

Do not invent a new storyboard schema for this. Record the world bible and its invariants in the existing `## Video direction` block, then express each frame's concrete subject and action in its existing `focal`, `roles`, and time-coded `Scene` lines.

## Shot grammar

Shape each beat as a shot, not a slide:

1. **Establish:** reveal the current place or camera space with a background and depth layers.
2. **Enter:** bring in the subject that the narration is discussing.
3. **Act:** let the subject perform the verb from the script.
4. **Interact:** show a visible cause-and-effect relationship with another subject, prop, or environment state.
5. **Follow or reframe:** pan, push, pull back, or hand off the camera when the story moves.
6. **Resolve:** land the teaching point in the world; add only short supporting text or captions.

Not every shot needs all six phases, but every shot must have a readable subject and an action or state change. A camera move is useful only when it follows the story or reveals spatial relationships.

## Text is supporting evidence

Narration explains the idea; concrete visuals embody it. Keep text to labels, short callouts, captions, names, or a brief takeaway. A title or paragraph must not be the only reason a scene exists.

If a diagram is necessary, turn it into an in-world object: a machine panel, map, route, monitor, hologram, sign, or physical network that the subject can approach, activate, connect to, or change. Do not default to a grid of boxes floating on a blank canvas.

## Anti-presentation gate

Reject or redesign a frame when:

- the main visual is a full-screen card, title block, or paragraph;
- the scene is only boxes, arrows, nodes, and labels with no world, subject, or action;
- every element enters together and then stays frozen;
- adjacent frames could be reordered without changing visual continuity;
- a real concrete noun from the script was replaced by generic text or a decorative icon without a reason.

Explicit presentation, pitch-deck, infographic, dashboard, or UI requests are exceptions and may use slide/card grammar. Otherwise, the default is world-first motion-explainer.

## Review checklist

Before building HTML, verify that the storyboard can answer:

- What place are we in?
- Which character or object is the focal subject?
- What does it do during this shot?
- What or whom does it affect?
- What persists from the previous shot?
- Where does the camera move, if it moves?
- What small amount of text remains after the visual action is understood?
