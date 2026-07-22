# Unity MCP Workflows

## Fast Scene Investigation

1. Check editor state
2. Open the active scene or target scene
3. Find relevant GameObjects
4. Inspect components
5. Change only the broken area
6. Verify with console plus screenshot

## Runtime Bug Workflow

1. Enter play mode only when needed
2. Inspect runtime objects directly
3. Compare asset prefab vs runtime instance
4. Fix source of truth
5. Re-run play mode and verify again

## Compile Error Workflow

1. Edit the smallest script set needed
2. Wait for Unity compile completion
3. Read console errors
4. Fix remaining errors one group at a time

## Asset Reference Workflow

1. Confirm target field is null, missing, or wrong
2. Find the intended asset
3. Reassign that exact asset
4. Re-check the object and console
