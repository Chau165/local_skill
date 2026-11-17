# Codex Configuration Backup

This is the `Chau165/local_skill` backup repository for local Codex instructions, skills, prompts, agents, and ECC plugin workflows.

The snapshot was refreshed from the local installation on 2026-10-28.

This repository stores user-maintained Codex files from `C:\Users\Surface\.codex` and global Agent Skills from `C:\Users\Surface\.agents\skills`.

## Included

- `codex/AGENTS.md`: global Codex instructions.
- `codex/skills/`: complete snapshot of `C:\Users\Surface\.codex\skills`, including bundled `.system` skills and each skill's supporting references, scripts, tests, assets, and configuration files.
- `agents/skills/`: snapshot of `C:\Users\Surface\.agents\skills`, including complete supporting files and divergent same-named skills.
- `codex/agents/`: local agent profiles.
- `codex/prompts/`: local prompt workflows.
- `plugins/ecc/`: ECC Codex plugin manifest and source skills.
- `metadata/marketplace.json`: personal marketplace registration for ECC.

## Excluded

Runtime state, credentials, caches, logs, databases, session data, attachments, generated artifacts, Python bytecode (`__pycache__`/`.pyc`), and bundled plugin caches are intentionally excluded. `config.toml` and MCP registrations are not included because they contain machine-specific runtime paths and should be configured per machine.

## Restore

Copy `agents/skills/` to `%USERPROFILE%/.agents/skills` after reviewing existing files. Merge instead of replacing; this preserves copies that differ from same-named skills under `.codex`.

Copy the contents of `codex/` into `%USERPROFILE%\\.codex`, and copy `plugins/ecc/` plus `metadata/marketplace.json` to the corresponding local locations after reviewing the current files. Merge instead of replacing existing configuration. The bundled `.system` snapshot is included for archival completeness; Codex may provide its own matching system skills.

## Video production add-on (2026-11-17)

The separately audited, portable 19-skill video snapshot is in [video-production/](video-production/README.md). It includes an install/rollback script, upstream commit and checksum manifest, optional legacy presets and a video-only workspace template. Existing application/backend instructions and snapshots are preserved. Run this add-on after any full restore of the older snapshot.

```powershell
python video-production/install.py --verify-only
python video-production/install.py --dry-run
python video-production/install.py
```
