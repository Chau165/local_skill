# AI Video Production workspace

Open this folder as a separate Codex project and start a new chat. AGENTS.md here applies only below this folder; never copy it to the global Codex home or an application/backend project.

The 19 video skills are installed into the user's .agents/skills by video-production/install.py. The Windows launcher uses this default path; for a custom skills root run its hyperframes/scripts/plugin-cli.mjs with Node directly. Source footage, locked scripts and original voice are authoritative. Cartoon/world-motion and Three.js are optional.

Start with templates/brief.md and scripts/sample-video-workflow.md. Keep original footage under input/, captions/transcripts under transcripts/, source code under src/, final MP4 under output/ and QA under reports/. Do not upload private footage/audio without explicit authorization. Do not replace the original voice with AI speech.

Runtime binaries are intentionally not in this backup. Install Node >=22, a supported browser and FFmpeg/FFprobe from their official sources when needed. For local speech recognition provision an official Whisper.cpp engine and multilingual model, verify its checksum and validate Vietnamese speech/timing. The original machine used FFmpeg 9.0.2 and Whisper.cpp v1.9.2; that is provenance, not a claim that these binaries were installed here.

For a verified project-local FFmpeg pair, set HYPERFRAMES_FFMPEG_PATH and HYPERFRAMES_FFPROBE_PATH to their absolute paths for the current process. HyperFrames deliberately ignores project-local binaries during ordinary PATH discovery. No global PATH or execution policy change is required.

The historical 6-second neutral smoke test rendered successfully on the source machine. This workspace template contains no private footage, audio, model weights or rendered media. Re-run a smoke test on a new machine rather than assuming the former render validates it.
