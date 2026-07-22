# Codex Configuration Backup

This is the `Chau165/local_skill` backup repository for the local Codex `AGENTS.md`, skills, prompts, agents, and ECC plugin workflows.

This repository stores the user-maintained Codex configuration surface from `C:\Users\Surface\.codex`.

## Included

- `codex/AGENTS.md`: global Codex instructions.
- `codex/skills/`: installed local skills, excluding bundled `.system` skills.
- `codex/agents/`: local agent profiles.
- `codex/prompts/`: local prompt workflows.
- `plugins/ecc/`: ECC Codex plugin manifest and source skills.
- `metadata/marketplace.json`: personal marketplace registration for ECC.

## Excluded

Runtime state, credentials, caches, logs, databases, session data, attachments, generated artifacts, and bundled plugin caches are intentionally excluded.

## Restore

Copy the contents of `codex/` into `%USERPROFILE%\\.codex`, and copy `plugins/ecc/` plus `metadata/marketplace.json` to the corresponding local locations after reviewing the current files. Merge instead of replacing existing configuration.
