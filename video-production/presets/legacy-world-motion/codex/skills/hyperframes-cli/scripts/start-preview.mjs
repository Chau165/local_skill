#!/usr/bin/env node

import { mkdir, open, writeFile } from "node:fs/promises";
import { spawn } from "node:child_process";
import { resolve, basename, join } from "node:path";
import http from "node:http";

function argumentValue(name, fallback) {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1];
}

function assertArgument(value, name) {
  if (typeof value !== "string" || !value.trim() || value.startsWith("--")) {
    throw new Error(`${name} requires a value`);
  }
  return value;
}

function serverResponds(port) {
  return new Promise((resolveResponse) => {
    const request = http.get({ host: "127.0.0.1", port, path: "/", timeout: 1000 }, (response) => {
      response.resume();
      resolveResponse(true);
    });
    request.on("timeout", () => request.destroy());
    request.on("error", () => resolveResponse(false));
  });
}

async function waitForServer(port, child) {
  const timeoutAt = Date.now() + 30_000;
  while (Date.now() < timeoutAt) {
    if (await serverResponds(port)) return;
    if (child.exitCode !== null) throw new Error(`HyperFrames preview exited with code ${child.exitCode}`);
    await new Promise((resolveDelay) => setTimeout(resolveDelay, 250));
  }
  throw new Error(`HyperFrames preview did not respond on localhost:${port} within 30 seconds`);
}

async function main() {
  const project = resolve(assertArgument(argumentValue("--project", "."), "--project"));
  const requestedPort = assertArgument(argumentValue("--port", "3002"), "--port");
  const port = Number(requestedPort);
  if (!Number.isInteger(port) || port < 1 || port > 65535) throw new Error("--port must be an integer from 1 to 65535");

  const stateDir = join(project, ".hyperframes");
  await mkdir(stateDir, { recursive: true });
  const url = `http://localhost:${port}/#project/${basename(project)}`;
  let pid = null;
  const reusedExistingServer = await serverResponds(port);

  if (!reusedExistingServer) {
    const logHandle = await open(join(stateDir, "preview.log"), "a");
    const command = process.platform === "win32" ? "npx.cmd" : "npx";
    const child = spawn(command, ["hyperframes", "preview", "--port", String(port)], {
      cwd: project,
      detached: true,
      stdio: ["ignore", logHandle.fd, logHandle.fd],
      windowsHide: true,
    });
    child.unref();
    pid = child.pid ?? null;
    await waitForServer(port, child);
    await logHandle.close();
  }

  const preview = {
    url,
    port,
    project,
    project_name: basename(project),
    pid,
    reused_existing_server: reusedExistingServer,
    relaunch_command: `npx hyperframes preview --port ${port}`,
  };
  await writeFile(join(stateDir, "preview.json"), `${JSON.stringify(preview, null, 2)}\n`, "utf8");
  process.stdout.write(`${JSON.stringify(preview)}\n`);
}

main().catch((error) => {
  process.stderr.write(`start-preview: ${error.message}\n`);
  process.exitCode = 1;
});
