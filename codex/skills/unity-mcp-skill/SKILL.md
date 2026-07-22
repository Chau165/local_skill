---
name: unity-mcp-orchestrator
description: Orchestrate Unity Editor work through MCP for Unity. Use when working on Unity projects with MCP tools such as scenes, GameObjects, scripts, assets, screenshots, tests, and editor automation.
---

# Unity MCP Operator Guide

This skill helps Codex use MCP for Unity effectively and safely.

## What This Skill Is For

Use this skill when a Unity project is connected through MCP and the task involves:

- creating or editing scenes
- finding or modifying GameObjects and components
- editing C# scripts and waiting for Unity compilation
- managing assets, prefabs, materials, UI, or build settings
- taking screenshots to verify visual results
- checking console errors after changes

This skill is not the Unity MCP server itself. It is a working guide for the AI client so it uses Unity MCP in a disciplined way.

## Core Workflow

Prefer a resource-first loop:

1. Read editor state first
2. Inspect the scene or target objects
3. Make the smallest necessary change
4. Check compilation or console state
5. Verify the result with screenshots or object inspection

## Rules

### 1. Check editor readiness before doing complex work

Read `mcpforunity://editor/state` and wait if Unity is:

- compiling
- reloading domain
- reconnecting

### 2. Verify before editing

Before changing a scene or object:

- inspect the target object first
- confirm names, paths, and hierarchy
- do not assume a prefab or component exists without checking

### 3. After script edits, always verify compile state

After writing or changing scripts:

- wait for compilation to finish
- check console for errors and warnings
- only continue once the edited types are usable

### 4. Use screenshots for visual work

For scene, UI, camera, prefab, or placement work:

- capture screenshots after changes
- prefer lower-resolution verification shots unless detail is needed
- use scene-view capture when editor framing matters

### 5. Use batching when many similar operations are needed

When creating or updating many Unity objects, prefer batched MCP operations to reduce latency and token usage.

### 6. Prefer minimal edits

Do not rebuild or rewrite whole scenes or systems when the task only needs:

- one component fix
- one prefab reference fix
- one missing asset assignment
- one transform correction

## Common Task Patterns

### Script fix loop

1. Edit the script
2. Wait for compile
3. Read console
4. Re-open the target scene or object if needed
5. Validate in play mode or with object inspection

### Scene repair loop

1. Find scene objects
2. Inspect hierarchy/components
3. Apply the smallest fix
4. Check console
5. Capture screenshot

### Visual verification loop

1. Frame the object or scene
2. Capture screenshot
3. Inspect for missing mesh, wrong material, wrong scale, wrong position
4. Fix and re-capture

## Best Practices

- Treat example payloads as templates, not guaranteed exact values
- Names and properties may differ by Unity version or project setup
- Prefer direct evidence from MCP tools over assumptions
- For runtime-only bugs, inspect in play mode
- For editor-time issues, inspect prefabs and scene data in edit mode

## References

Read these when useful:

- `references/workflows.md`
- `references/tools-reference.md`
- `references/troubleshooting.md`
