# Example real-footage workflow

1. Open this directory as its own Codex project. Copy sources into input/ and constrained references into references/; retain original hashes. Start with templates/brief.md.
2. Probe streams and duration using .tools/ffmpeg/ffprobe.exe. Keep the source voice stream; a mono WAV for transcription is only a derived asset.
3. Use local transcription with Vietnamese language and word timestamps where the engine supports them. Verify uncertain words and export JSON/SRT/VTT. Do not upload audio without consent.
4. Fill storyboard.csv with exact quotes/times. Keep captions active over every illustration; choose overlay/PiP/fullscreen per meaning and brief.
5. Fill claims.csv with primary factual sources, as-of dates and discrepancies; hypothetical examples carry a visible label. Approval is required before changing an original substantive claim.
6. Select the actual renderer. For Remotion use remotion-best-practices and remotion-captions; install framework packages only in that video project. For HyperFrames use its current contract and scripts/Invoke-HyperFrames.ps1.
7. Run short render/visual QA, then full render and speech/caption verification. Deliver MP4, captions, transcript, storyboard, assets/source ledger, source code and QA report.
