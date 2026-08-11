# Animation-forward motion standard

Use this standard for every produced video, including `image_only` projects. `image_only` describes source-asset type, not a static final render.

This is a domain-neutral motion standard. It requires a continuous world and meaningful relationships, but it does not prescribe robots, AI, code, developers, buildings, charts, or any other subject. Derive the world, subjects, environment, props, and interaction verbs from the approved topic and script.

## Shot contract

Every storyboard shot must include `motion_design` with:

- `implementation`: `layered_2d`, `vector_animation`, `rigged_character`, `generated_video`, `composited_particles`, or `hybrid`;
- `camera_motion`: a concise camera plan, including `none` when appropriate;
- `subject_motion`: visible local subject motion;
- `environment_motion[]`: at least two independently animated environmental or secondary elements;
- `animated_layers[]`: at least two independently controlled visual layers;
- `interaction_event`: a visible cause-and-effect beat;
- `timing_beats[]`: one or more timed actions relative to the shot;
- `loop_strategy`: how ambient motion continues without a visible reset;
- `camera_only`: always `false` for approved production shots.

For each shot, the environment and subject names must be context-specific. A generic preset object or repeated motif cannot stand in for the source's actual domain unless the script itself calls for it.

Do not satisfy multiple fields with the same global transform. A single flattened image undergoing scale, translate, rotate, crop, blur, or crossfade remains camera-only treatment.

## Production strategies

Choose the simplest verified strategy that creates real local motion:

1. Layered 2D: separate foreground, midground, background, subject, effects, and labels; animate transforms, masks, deformation, opacity, and particles independently.
2. Vector/procedural: animate paths, diagrams, icons, charts, routes, highlights, and state changes directly.
3. Rigged character: animate body parts, pose, face, mouth where needed, anticipation, reaction, and secondary motion.
4. Generated video: use only an observed motion-capable provider, preserve provenance, and reject temporal inconsistency or copied identity.
5. Hybrid: combine generated key art with original separated layers, particles, vector overlays, and character animation.

Do not upscale a static-image slideshow by adding only slow zooms and transitions.

## Motion proof

Before batch production, render an 8–15 second representative clip containing a character or subject, environment, explanatory event, and transition. Inspect consecutive frames and require:

- continuous local change inside the shot;
- at least two independently moving layers;
- a visible subject-environment or input-output interaction;
- readable text and stable character identity;
- no frozen background disguised by camera motion.

Revise the asset decomposition or provider plan when the proof fails.

The representative proof must contain a context-appropriate focal subject, its environment, an explanatory event, and a transition. The subject may be a person, object, place, system, event, or abstraction; choose it from the approved topic and script. Do not require a character when the topic does not call for one.

## Render QA contract

Record `motion_quality` in the manifest with:

- `status`: `pending`, `passed`, or `failed`;
- `analysis_method` and `sample_rate_fps`;
- `meaningful_motion_screen_time_ratio` at least `0.65`;
- `distributed_motion_screen_time_ratio` at least `0.50`;
- `independent_layer_motion_shot_ratio` at least `0.80` from manual review;
- `interaction_shot_ratio` at least `0.60` from manual review;
- `camera_only_screen_time_ratio` at most `0.15`;
- `max_static_hold_seconds` at most `2.0` outside an explicitly justified pause;
- `automated_report_path`, `automated_report_sha256`, `manual_reviewed_by`, `manual_reviewed_at`, and `notes[]`.

The automated motion screen detects frame change, distributed change, cuts, and long static runs. It cannot prove independent layer motion. Set `status: passed` only after both automated and manual review pass.
