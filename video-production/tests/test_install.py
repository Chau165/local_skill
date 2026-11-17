"""Offline integration checks for the portable video-skill installer (stdlib only)."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import uuid

PACKAGE = Path(__file__).resolve().parents[1]
manifest = json.loads((PACKAGE / 'manifest.json').read_text(encoding='utf-8'))
base = Path(os.environ.get('VIDEO_SKILL_TEST_ROOT', tempfile.gettempdir())).resolve()
base.mkdir(parents=True, exist_ok=True)
fixture = base / ('video-install-test-' + uuid.uuid4().hex[:10])
fixture.mkdir()
root = fixture / 'agents/skills'
codex = fixture / 'codex'
workspace = fixture / 'video-workspace'
installer = PACKAGE / 'install.py'


def invoke(*args, expected=0):
    command = [sys.executable, '-X', 'utf8', str(installer), '--skills-root', str(root), '--codex-home', str(codex), *map(str, args)]
    result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', timeout=120)
    assert result.returncode == expected, (result.returncode, result.stdout[-500:], result.stderr[-500:])
    return result


def skill_hashes(directory):
    return {p.relative_to(directory).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.rglob('*') if p.is_file()}


invoke('--verify-only')
invoke('--dry-run', '--workspace', workspace)
assert not root.exists() and not codex.exists() and not workspace.exists(), 'Dry-run wrote data'
print('PASS verify + dry-run: no target data created')

# Seed both legacy roots, a customized skill, and unrelated application files.
for p, content in [(root / 'hyperframes/SKILL.md', 'old canonical customized skill'),
                   (codex / 'skills/hyperframes/SKILL.md', 'old duplicate customized skill'),
                   (root / 'unrelated-app/SKILL.md', 'preserve unrelated skill'),
                   (codex / 'AGENTS.md', 'preserve global backend instructions'),
                   (codex / 'config.toml', 'preserve global config')]:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding='utf-8')
before = skill_hashes(fixture)
invoke('--workspace', workspace)
assert (workspace / 'AGENTS.md').is_file()
assert len([p for p in root.iterdir() if (p / 'SKILL.md').is_file()]) == 20  # 19 managed + unrelated
assert not (codex / 'skills/hyperframes/SKILL.md').exists(), 'Duplicate entrypoint still active'
assert (codex / 'skills/hyperframes/references').is_dir(), 'Legacy support guides missing'
for item in manifest['skills']:
    assert skill_hashes(root / item['name']) == skill_hashes(PACKAGE / 'skills' / item['name']), item['name']
for rel, expected in before.items():
    if rel.endswith('hyperframes/SKILL.md'):
        continue
    assert hashlib.sha256((fixture / rel).read_bytes()).hexdigest() == expected, rel
print('PASS install: 19 exact skill trees; duplicate archived; unrelated config/AGENTS/skill preserved')

receipts = list((codex / 'backups/video-production').glob('*/receipt.json'))
assert len(receipts) == 1
receipt = receipts[0]
invoke()
assert len(list((codex / 'backups/video-production').glob('*/receipt.json'))) == 1, 'Identical reinstall was not a no-op'
print('PASS idempotent reinstall')

invoke('--workspace', workspace, expected=1)
print('PASS existing workspace AGENTS.md refused without changes')

after = skill_hashes(root)
invoke('--rollback', receipt, '--dry-run')
assert skill_hashes(root) == after
invoke('--rollback', receipt)
assert (root / 'hyperframes/SKILL.md').read_text() == 'old canonical customized skill'
assert (codex / 'skills/hyperframes/SKILL.md').read_text() == 'old duplicate customized skill'
assert (codex / 'AGENTS.md').read_text() == 'preserve global backend instructions'
assert (codex / 'config.toml').read_text() == 'preserve global config'
assert (root / 'unrelated-app/SKILL.md').read_text() == 'preserve unrelated skill'
assert not workspace.exists(), 'Created workspace should be quarantined on rollback'
for item in manifest['skills']:
    if item['name'] != 'hyperframes':
        assert not (root / item['name']).exists(), item['name']
print('PASS rollback dry-run + real rollback: original customizations restored; current install quarantined')
print('All installer checks passed. Fixture retained for review: ' + str(fixture))
