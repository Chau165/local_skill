# Codex Configuration Backup

This is the `Chau165/local_skill` backup repository for the local Codex `AGENTS.md`, skills, prompts, agents, and ECC plugin workflows.

The snapshot was refreshed from the local installation on 2026-09-03.

This repository stores the user-maintained Codex configuration surface from `C:\Users\Surface\.codex`.

## Included

- `codex/AGENTS.md`: global Codex instructions.
- `codex/skills/`: complete snapshot of `C:\Users\Surface\.codex\skills`, including bundled `.system` skills and each skill's supporting references, scripts, tests, assets, and configuration files.
- `codex/agents/`: local agent profiles.
- `codex/prompts/`: local prompt workflows.
- `plugins/ecc/`: ECC Codex plugin manifest and source skills.
- `metadata/marketplace.json`: personal marketplace registration for ECC.

## Excluded

Runtime state, credentials, caches, logs, databases, session data, attachments, generated artifacts, Python bytecode (`__pycache__`/`.pyc`), and bundled plugin caches are intentionally excluded.

## Restore

Copy the contents of `codex/` into `%USERPROFILE%\\.codex`, and copy `plugins/ecc/` plus `metadata/marketplace.json` to the corresponding local locations after reviewing the current files. Merge instead of replacing existing configuration. The bundled `.system` snapshot is included for archival completeness; Codex may provide its own matching system skills.
