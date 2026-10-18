---
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up.
---

Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save outside the current workspace in the operating system's temporary directory (Windows: `$env:TEMP`; Unix-like systems: `$TMPDIR`, falling back to `/tmp`).

Include a "Suggested skills" section naming relevant skills available in the receiving Codex environment and briefly explaining why each applies. Do not assume skills are installed there.

Do not duplicate content already captured in other artifacts (PRDs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.
