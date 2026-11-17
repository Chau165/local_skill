# Validation for the video skill backup

Performed on Windows with Python 3.13.14 and Node 22.20.0. Test directories are isolated fixtures; the source machine's installed skills and global configuration were not reinstalled or changed by these tests.

- `python video-production/install.py --verify-only`: all declared file hashes and 19 entrypoints checked.
- `python video-production/tests/test_install.py`: fresh-target dry-run writes nothing; installation produces 19 exact skill trees; customized prior copies are archived; duplicate legacy SKILL.md is retired while support references remain; unrelated global AGENTS.md, config.toml and application skill remain byte-identical.
- Identical reinstall is a no-op; a target workspace with existing AGENTS.md is refused.
- Rollback dry-run changes nothing; real rollback in the fixture restores both original custom skill copies and quarantines the new installation.
- `node --check` passed for the pinned HyperFrames launcher and full optional world-motion audit implementation.
- Staged Git blob hashes are compared with every local package file. `-text` attributes preserve manifest bytes on checkout. Text line endings are normalized to LF.
- Credential-shaped token/private-key scans found no matches. Personal ADMIN/Surface home paths were removed from this package. Auth/config files, user footage/voice, model weights and runtime executables are excluded.
- Bundled sound effects are skill assets, not private speech. Their blobs were matched to sound effects already present in the repository's previous public snapshot; credits remain alongside them.
- New installer/test/README/NOTICE files pass targeted `git diff --check`. Some archived upstream templates retain existing trailing whitespace or blank EOF lines; these are preserved as source material, not silently reformatted.

Historical source-machine verification: Codex discovered all 19 selected skills with no duplicate names in that set, and a neutral HyperFrames 0.9.59 MP4 smoke test rendered with Vietnamese subtitle and a hypothetical chart. This history does not certify dependencies, Vietnamese speech accuracy, optional paid providers, every legacy recipe or a fresh render on another machine.
