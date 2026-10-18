---
name: context-budget
description: Checks live Codex context usage through the native meter, or audits installed context-related components when explicitly requested. Use for questions about remaining context or a bounded static context audit.
metadata:
  origin: ECC
---

# Context Budget

Use Codex's native meter for live session usage. Keep static installation audits separate and opt-in.

## Live Context (default)

Treat requests about current context usage, remaining capacity, headroom, or the live context breakdown as live-context requests unless the user explicitly asks to inspect installed files.

- Do not call tools, scan files, run shell commands, or estimate live usage.
- Tell the user to run `/status` in Codex to view current context usage.
- For a persistent footer meter, suggest `/statusline` and enabling **Context stats** and **Token counters**.
- A skill cannot invoke a slash command or read the live meter on the user's behalf. If slash commands are unavailable in the active surface, say the live value cannot be verified here.

See the [Codex slash-command reference](https://developers.openai.com/codex/cli/slash-commands).

## Explicit Static Audit

Inspect installed components only when the user explicitly asks to audit installed skills, instructions, agents, or context overhead. If the root or harness scope is unclear, ask before reading files. Keep the audit bounded and read-only:

1. Inspect only the named installation root and relevant configuration files.
2. Do not recursively scan the home directory, caches, transcripts, debug logs, workspace roots, or unrelated worktrees.
3. Cap detailed entries at 50 per component class; summarize the rest.
4. Separate eagerly discovered metadata (such as skill names and descriptions) from on-demand skill bodies. Report file size/line counts separately from any estimate of eager context.
5. Report token counts only when a tokenizer appropriate to the active model is available and its use is verified. Otherwise provide counts or sizes as proxies and label them clearly; never present a heuristic as live or exact token usage.

## Audit Output

Return a compact report with the harness, exact paths and scope inspected, component counts, the measurement method, key findings, and up to three prioritized optimizations. State omitted paths, uncertainty, and any unavailable measurements. An installation estimate is not the provider-reported live context or proof of realized savings. Direct the user to `/status` for current session usage.
