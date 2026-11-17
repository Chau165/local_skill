# Skill installation and freshness

Read this reference when installing or updating skills, diagnosing unexpected workflow behavior, or running HyperFrames setup in CI.

HyperFrames installs the core set eagerly and workflow skills lazily. This installation uses **local custom-skill mode**: installed skill files are authoritative and automatic refreshes are disabled.

- **Core set:** `/hyperframes`, the `hyperframes-*` domain skills, and `/media-use`.
- **Workflow skills:** normally installed when routing selects them, but this local installation must use an already-installed workflow unless the user explicitly approves an updater.

## What `init` does

`npx hyperframes init` can check GitHub and refresh the core set plus other skills already installed. In this local installation, set `HYPERFRAMES_SKIP_SKILLS=1` before `init` so it does not refresh custom skill files. It does not install workflows that have never been used.

The `--skip-skills` CLI flag is temporarily ignored. Use `HYPERFRAMES_SKIP_SKILLS=1` for local custom-skill mode as well as CI/tests.

## Diagnose and update

```bash
npx hyperframes skills check
npx hyperframes skills check --json
npx hyperframes skills update
npx hyperframes skills update <workflow-name>
npx hyperframes skills
```

- `skills check` exits non-zero when an installed skill is stale or the core set is incomplete. Workflows available on demand but not installed are not failures.
- Bare `skills update` refreshes the core set and everything already installed, prunes unpublished skills, and does not expand the workflow set. Do not run it automatically in local custom-skill mode.
- Named `skills update <name...>` also installs those named workflows or domain skills. Treat it as a manual, explicitly approved operation because it can overwrite local customizations.
- Bare `skills` installs the full published set explicitly.

If the HyperFrames CLI is unavailable, use `npx skills add heygen-com/hyperframes --skill <workflow-name>` for one workflow or `npx skills add heygen-com/hyperframes --all` for the full published set.

The CLI may print a one-line stale-skill reminder during `render`, `lint`, or `check`. Treat a failed update as a visible tool failure; do not continue from a remembered workflow contract.
