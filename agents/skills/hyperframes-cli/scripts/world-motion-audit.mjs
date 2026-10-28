#!/usr/bin/env node

import { spawnSync } from "node:child_process";

const source = "C:/Users/Surface/.codex/skills/hyperframes-cli/scripts/world-motion-audit.mjs";
const result = spawnSync(process.execPath, [source, ...process.argv.slice(2)], { stdio: "inherit" });
if (result.error) throw result.error;
process.exitCode = result.status ?? 3;
