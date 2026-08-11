---
name: lottie-motion
description: Route reusable Lottie and dotLottie asset motion into HyperFrames world-motion explainers without replacing scene choreography. Use when an object needs a self-contained, pre-baked internal animation such as a wheel, gauge, smoke, sparkle, flow, pulse, or character gesture.
---

# Lottie / dotLottie Motion Assets

Use Lottie for a reusable asset's internal motion. Use HyperFrames and GSAP for scene layout, camera travel, interaction timing, and final render.

## Decide first

Use ordinary SVG + GSAP when a subject simply travels, approaches, hands over, collides with, or affects another subject in the world.

Use Lottie/dotLottie when a reusable asset contains its own finite internal motion: a wheel turning, a pump cycling, smoke rising, money flowing, a gauge changing, or a character gesture.

Do not use Lottie to substitute a world, cause-and-effect interaction, or the required independent actor/target motion.

## Shared toolkit

The user-wide packages live at `C:\Users\Surface\.codex\tools\motion-toolkit`:

- `lottie-web`
- `@lottiefiles/dotlottie-web`
- `@lottiefiles/dotlottie-io`

Verify the installation with:

```powershell
npm --prefix C:\Users\Surface\.codex\tools\motion-toolkit run verify
```

Use `dotlottie-io` from this toolkit only to inspect, create, or modify a `.lottie` asset. Copy the resulting `.json` or `.lottie` file into the project's `assets/` folder; do not make the video project depend on the shared toolkit.

## HyperFrames runtime contract

Follow `hyperframes-animation/adapters/lottie.md` for implementation. In particular:

- load a local project asset;
- set `autoplay: false` and normally `loop: false`;
- create and register the player synchronously on `window.__hfLottie`;
- never call `play()` or use wall-clock, timers, or asynchronous registration for render-critical motion;
- let HyperFrames seek the asset and own the composition timeline.

For a world-motion explainer, keep the Lottie element semantically inside its owning subject layer. The scene actor and target must still have their own visible, seek-safe state changes, and `world-motion-audit.mjs` must pass before render.
