#!/usr/bin/env node

import { access, mkdir, readFile, writeFile } from "node:fs/promises";
import { constants } from "node:fs";
import { resolve, relative, dirname } from "node:path";

function valueAfter(flag, fallback) {
  const index = process.argv.indexOf(flag);
  return index === -1 ? fallback : process.argv[index + 1];
}

function requiredString(value, location, errors) {
  if (typeof value !== "string" || !value.trim()) errors.push(`${location} must be a non-empty string`);
}

async function exists(path) {
  try {
    await access(path, constants.F_OK);
    return true;
  } catch {
    return false;
  }
}

function escapeRegex(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function attributeValues(html, attribute) {
  const values = new Set();
  const matcher = new RegExp(`${attribute}\\s*=\\s*["']([^"']+)["']`, "gi");
  for (const match of html.matchAll(matcher)) values.add(match[1]);
  return values;
}

function hasMotionFor(html, worldId) {
  const id = escapeRegex(worldId);
  const selector = `(?:#${id}|\\[data-world-id=["']${id}["']\\])`;
  return new RegExp(`\\.(?:to|from|fromTo)\\s*\\(\\s*["'][^"']*${selector}`, "s").test(html);
}

async function audit(project) {
  const errors = [];
  const manifestPath = resolve(project, "world-motion.json");
  if (!(await exists(manifestPath))) return { errors: ["world-motion.json is required before render"], manifestPath };

  let manifest;
  try {
    manifest = JSON.parse(await readFile(manifestPath, "utf8"));
  } catch (error) {
    return { errors: [`world-motion.json must be valid JSON: ${error.message}`], manifestPath };
  }
  if (!manifest || typeof manifest !== "object" || Array.isArray(manifest)) return { errors: ["world-motion.json must contain an object"], manifestPath };
  if (manifest.visual_grammar !== "world_motion_explainer") errors.push("visual_grammar must be world_motion_explainer");
  if (manifest.presentation_allowed !== false) errors.push("presentation_allowed must be false");
  requiredString(manifest.script_path, "script_path", errors);
  if (typeof manifest.script_path === "string" && !(await exists(resolve(project, manifest.script_path)))) errors.push(`script_path does not exist: ${manifest.script_path}`);

  const world = manifest.world;
  if (!world || typeof world !== "object" || Array.isArray(world)) {
    errors.push("world must be an object");
  } else {
    requiredString(world.setting, "world.setting", errors);
    if (!Array.isArray(world.continuity_anchors) || world.continuity_anchors.length === 0) errors.push("world.continuity_anchors must contain at least one item");
  }

  if (!Array.isArray(manifest.shots) || manifest.shots.length === 0) {
    errors.push("shots must contain at least one world-motion shot");
    return { errors, manifestPath };
  }

  const seenCompositions = new Set();
  for (const [index, shot] of manifest.shots.entries()) {
    const prefix = `shots[${index}]`;
    if (!shot || typeof shot !== "object" || Array.isArray(shot)) {
      errors.push(`${prefix} must be an object`);
      continue;
    }
    requiredString(shot.composition, `${prefix}.composition`, errors);
    requiredString(shot.setting, `${prefix}.setting`, errors);
    requiredString(shot.continuity_anchor, `${prefix}.continuity_anchor`, errors);
    if (typeof shot.composition !== "string") continue;
    if (seenCompositions.has(shot.composition)) errors.push(`${prefix}.composition must be unique`);
    seenCompositions.add(shot.composition);

    const compositionPath = resolve(project, shot.composition);
    if (!relative(project, compositionPath) || relative(project, compositionPath).startsWith("..")) {
      errors.push(`${prefix}.composition must stay inside the project`);
      continue;
    }
    if (!(await exists(compositionPath))) {
      errors.push(`${prefix}.composition does not exist: ${shot.composition}`);
      continue;
    }
    const html = await readFile(compositionPath, "utf8");
    const roles = attributeValues(html, "data-world-role");
    const ids = attributeValues(html, "data-world-id");
    for (const requiredRole of ["background", "environment", "subject"]) {
      if (!roles.has(requiredRole)) errors.push(`${prefix}.composition is missing data-world-role=${requiredRole}`);
    }

    if (!Array.isArray(shot.interactions) || shot.interactions.length === 0) {
      errors.push(`${prefix}.interactions must contain an actor-to-target event`);
      continue;
    }
    for (const [interactionIndex, interaction] of shot.interactions.entries()) {
      const interactionPrefix = `${prefix}.interactions[${interactionIndex}]`;
      if (!interaction || typeof interaction !== "object" || Array.isArray(interaction)) {
        errors.push(`${interactionPrefix} must be an object`);
        continue;
      }
      for (const field of ["actor", "target", "event"]) requiredString(interaction[field], `${interactionPrefix}.${field}`, errors);
      if (interaction.actor === interaction.target) errors.push(`${interactionPrefix} actor and target must be distinct`);
      for (const field of ["actor", "target"]) {
        if (typeof interaction[field] !== "string") continue;
        if (!ids.has(interaction[field])) errors.push(`${interactionPrefix}.${field} has no matching data-world-id in ${shot.composition}`);
        else if (!hasMotionFor(html, interaction[field])) errors.push(`${interactionPrefix}.${field} has no subject-owned GSAP motion in ${shot.composition}`);
      }
    }
  }
  return { errors, manifestPath };
}

async function main() {
  const project = resolve(valueAfter("--project", "."));
  const reportPath = valueAfter("--report", ".hyperframes/world-motion-audit.json");
  const result = await audit(project);
  const report = { status: result.errors.length ? "BLOCK" : "PASS", project, manifest: result.manifestPath, errors: result.errors };
  const outputPath = resolve(project, reportPath);
  await mkdir(dirname(outputPath), { recursive: true });
  await writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
  process.stdout.write(`${JSON.stringify(report)}\n`);
  if (result.errors.length) process.exitCode = 2;
}

main().catch((error) => {
  process.stderr.write(`world-motion-audit: ${error.message}\n`);
  process.exitCode = 3;
});
