---
name: media-use
description: Agent Media OS for HyperFrames. Resolve BGM, SFX, images, icons, brand logos, voice, color grades, or LUTs into frozen local files or paste-ready blocks with ledger records; generate when the catalog misses; operate on media; and reuse assets across projects. Use whenever a video needs actual media files rather than primitive HTML/SVG placeholders.
---

# media-use

The media OS for HyperFrames: resolve · generate · operate · remember — every media type, one skill, zero context noise.

First run: install and sign in to the `heygen` CLI (the free-usage path), then verify with `node <SKILL_DIR>/scripts/resolve.mjs --doctor`. Setup and providers: `references/setup-providers.md`.

## Resolve — the one verb

```bash
node <SKILL_DIR>/scripts/resolve.mjs --type <type> --intent "<description>" --project <dir>
```

Returns one line: `resolved <id> → <path> (<type>, <metadata>)`. All search noise stays on disk.

| Type    | One-line intent                                                                     |
| ------- | ----------------------------------------------------------------------------------- |
| `bgm`   | background music (HeyGen catalog, 10k+ tracks)                                      |
| `sfx`   | sound effects (bundled 19-file library + catalog)                                   |
| `image` | photos, backgrounds (HeyGen asset search, 75k+ vectors)                             |
| `icon`  | icons, symbols (transparent)                                                        |
| `logo`  | official brand marks (svgl → simple-icons → GitHub avatar → favicon; never redrawn) |
| `voice` | TTS voiceover (HeyGen free-usage path; optional local Kokoro)                       |
| `grade` | measured correction candidate; broad polish/stylization follows Media Treatments    |
| `lut`   | user-provided or explicitly chosen reusable validated `.cube` file                  |

## Image-based cartoon production

When the brief requests cartoon, illustrated, cutout, cel-animation, painted-background, or image-based visuals, read `../hyperframes-creative/references/image-based-cartoon-assets.md` and run media resolution as an asset-production pass before composition HTML. For polished flat/cel cutout, a recurring animated guide, or subject-adaptive multi-topic production, also read `../hyperframes-creative/references/subject-adaptive-cutout-world.md` and require `STYLE_BIBLE.md` plus `WORLD_ASSET_MATRIX.md` before generation.

1. Resolve/adopt suitable licensed project assets first.
2. If catalog assets do not fit the original world, use an available image-generation or sprite-generation capability to create the missing asset as a local PNG/WebP/layered SVG/sprite/Lottie file, then adopt it into the project ledger.
3. Generate in style-locked batches: guide and pose family, topic actors, environment planes, buildings and props, vehicles or machines, interaction states, then FX. Reuse the same style prompt and scale/perspective rules from `STYLE_BIBLE.md` while changing nouns through `WORLD_ASSET_MATRIX.md`.
4. Generate separate background, midground, foreground, atmosphere, character, prop, vehicle, and interaction-part assets required by `ASSET_PLAN.md`; do not bake the entire scene into one image when local motion or parallax is required.
5. Preserve transparent backgrounds for cutout subjects and record prompt/reference summary, provider/model when known, usage rights, dimensions, pivot, pose/state, and SHA-256 in `asset-manifest.json`.
6. Build and inspect the contact sheet after each major batch. Reject inconsistent silhouette, outline weight, perspective, ground line, shadow direction, palette role, character proportion, or asset scale before composition.
7. Never satisfy a missing illustrated subject with an emoji, generic icon, CSS box, or raw rectangle/circle/polygon. Report the missing asset instead.

Reference images are style/context evidence only. Do not reproduce their protected characters, logos, or distinctive compositions.

Before resolving fresh, list reusable candidates with `--candidates` and judge fit yourself — reuse rules, all flags, ingest (`--from`), and adopt are in `references/resolve.md`.

## Treat broad visual feedback as media intent

When a user explicitly asks to fix, polish, stylize, obscure, emphasize, or
reveal photographic media, read `references/media-treatments.md` even if they
do not name color grading or an effect. Inspect the real `<img>`/`<video>`,
choose one primary intent, then use deterministic persistence and verification.
Use a matching recipe as an optional tested seed, or inspect
`hyperframes media-treatment --capabilities --json`, then request one relevant
family/effect with `--capability <id>` and assemble a custom treatment from
canonical controls. Never load `--all` for ordinary authoring. A treatment may
compose correction, a preset, finishing, compatible shader effects, supported
keyframes, and optional Registry overlays. Add only source-justified bounded
tuning and compatible parts, never effects merely to make the result look more
sophisticated. Persist the final combined payload with
`hyperframes media-treatment`.

Use one progressively escalating workflow. For video, inspect one labeled
early/middle/late contact sheet rather than reading frames separately. Apply one
candidate and inspect one after-sheet for ordinary correction or polish.
Escalate to individual frames or moving draft evidence only when the result is
ambiguous, temporal, stylized, LUT-based, HDR/LOG-sensitive, private, or
brand-critical.

For ordinary correction or polish, persist the final treatment's
preset/adjustment JSON.
Do not generate a `.cube` LUT merely to encode exposure, shadows, contrast, or
warmth. Use a LUT only when the user supplies one or the selected treatment
explicitly owns one. `resolve --type grade --for ... --analyze` is measurement
evidence, not permission to replace the chosen treatment with a generated LUT.
Do not recreate supported vignette, grain, blur, pixelate, color, or treatment
effects with CSS/SVG overlays; that bypasses Studio controls and the canonical
preview/render shader path.

## Be proactive — run a media opportunity pass

The human usually can't tell which media would lift the piece. You can. When you build or review a composition, do **one** grounded scan and then **ask once** — don't silently add, and don't nag per asset.

Surface an opportunity only when a concrete signal is present:

| Signal detected                                          | Offer                                                                                                  |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| On-screen text / a script with no voiceover              | TTS voiceover (audio engine)                                                                           |
| Emoji or a `<div>` styled as an icon                     | resolve real `icon`s                                                                                   |
| Image that is a placeholder, tiny, or upscaled-looking   | a better `image` (and/or upscale — see `references/operations.md`)                                     |
| Hard scene cuts / transitions with no sound              | transition `sfx`                                                                                       |
| A piece over ~10s with no music bed                      | `bgm`                                                                                                  |
| Footage that reads under/over-exposed or color-cast      | a corrective grade (inspect it with `hyperframes media-treatment --selector '#hero' --analyze --json`) |
| Photographic media that feels visually flat or off-topic | one specific source-appropriate preset or custom treatment, with the intended target named             |
| A meaningful media entrance/reveal that feels static     | one supported seek-safe treatment animation; preserve color unless the request also justifies a preset |

Rules that keep this a help, not nagware: **grounded, not generic** (no signal → no suggestion); **opinionated + concrete** (propose the specific fix with defaults chosen — the human approves **all / some / none**); **once per project** (one consolidated ask; respect "leave it"); **surface, never silently mutate** (color grades especially: propose and preview — a gray-world "correction" ruins an intentional sunset or neon look).

## Where to look — read only the file your task needs

| Task                                                                      | Read                             |
| ------------------------------------------------------------------------- | -------------------------------- |
| resolve / reuse / adopt / ingest, flags, cascade, inventory               | `references/resolve.md`          |
| image-based cartoon asset generation, adoption, and layered asset gate     | `../hyperframes-creative/references/image-based-cartoon-assets.md` |
| subject-adaptive flat/cel cutout batches, guide rigs, and topic world kits | `../hyperframes-creative/references/subject-adaptive-cutout-world.md` |
| color grading, LUTs, smart grade (`--for`), grade-compare                 | `references/grading.md`          |
| voiceover / TTS, music, SFX, captions, transcription (audio engine)       | `references/audio.md`            |
| cut / reframe / transform existing media, exact error diffusion, HEVC     | `references/operations.md`       |
| source-aware creative treatments, realtime effects, overlays, reveals     | `references/media-treatments.md` |
| install + auth, provider table, RAM ladders, `--local-only`, `--provider` | `references/setup-providers.md`  |
| remembered preferences + frozen recipes (user memory)                     | `references/memory.md`           |
| ownership matrix, usage stats, telemetry, privacy (maintainer-facing)     | `references/meta.md`             |
