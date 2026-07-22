# Unity MCP Troubleshooting

## If Unity is connected but tools fail

- re-check editor state
- confirm Unity is not compiling
- retry after reconnect if the session was reloaded

## If screenshots look wrong

- verify the active camera
- try scene-view capture
- inspect object renderers and materials directly

## If a skill sync failed previously

- make sure `SKILL.md` exists locally
- make sure the `references` folder exists
- restart the AI client if it cached the old broken skill state

## If Unity MCP reports session or authorization problems

- reconnect the Unity client
- restart the local server if needed
- avoid repeated rapid retries when a remote download service is rate-limiting
