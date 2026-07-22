param(
    [string]$CodexHome = (Join-Path $env:USERPROFILE '.codex'),
    [string]$EccRoot = (Join-Path $env:USERPROFILE 'plugins\\ecc')
)

$ErrorActionPreference = 'Stop'
$backupRoot = $PSScriptRoot

function Copy-Merge([string]$Source, [string]$Destination) {
    New-Item -ItemType Directory -Path $Destination -Force | Out-Null
    Get-ChildItem -LiteralPath $Source -Force | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $Destination $_.Name) -Recurse -Force
    }
}

if (-not (Test-Path -LiteralPath (Join-Path $CodexHome 'AGENTS.md'))) {
    Copy-Item -LiteralPath (Join-Path $backupRoot 'codex\\AGENTS.md') -Destination (Join-Path $CodexHome 'AGENTS.md')
} else {
    Write-Host "Existing AGENTS.md preserved; review the snapshot at $backupRoot\\codex\\AGENTS.md before merging."
}
Copy-Merge (Join-Path $backupRoot 'codex\\skills') (Join-Path $CodexHome 'skills')
Copy-Merge (Join-Path $backupRoot 'codex\\agents') (Join-Path $CodexHome 'agents')
Copy-Merge (Join-Path $backupRoot 'codex\\prompts') (Join-Path $CodexHome 'prompts')
Copy-Merge (Join-Path $backupRoot 'plugins\\ecc') $EccRoot

$marketplace = Join-Path $backupRoot 'metadata\\marketplace.json'
if (Test-Path -LiteralPath $marketplace) {
    Write-Host "Review and merge marketplace metadata manually: $marketplace"
}

Write-Host "Codex configuration restored with merge semantics. Restart Codex to reload skills."
