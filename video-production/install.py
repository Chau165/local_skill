#!/usr/bin/env python3
"""Install this audited video-skill snapshot without touching global configuration."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import uuid

PACKAGE = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def linked(path):
    return path.is_symlink() or getattr(path, 'is_junction', lambda: False)()


def files(root):
    result = {}
    if linked(root):
        raise ValueError('Refusing linked target: ' + str(root))
    for path in root.rglob('*'):
        if linked(path):
            raise ValueError('Refusing linked content: ' + str(path))
        if path.is_file():
            result[path.relative_to(root).as_posix()] = digest(path)
    return result


def tree_hash(root):
    return hashlib.sha256(json.dumps(files(root), sort_keys=True).encode()).hexdigest()


def verify():
    manifest = json.loads((PACKAGE / 'manifest.json').read_text(encoding='utf-8'))
    declared = {item['path'] for item in manifest['files']}
    actual = {p.relative_to(PACKAGE).as_posix() for p in PACKAGE.rglob('*')
              if p.is_file() and p != PACKAGE / 'manifest.json' and '__pycache__' not in p.parts}
    if declared != actual:
        raise ValueError('Package inventory changed; restore the snapshot or regenerate its manifest')
    for item in manifest['files']:
        path = PACKAGE / item['path']
        if PACKAGE not in path.resolve().parents or linked(path):
            raise ValueError('Invalid package path: ' + item['path'])
        if not path.is_file() or digest(path) != item['sha256']:
            raise ValueError('Package checksum mismatch: ' + item['path'])
    names = [item['name'] for item in manifest['skills']]
    if len(names) != len(set(names)):
        raise ValueError('Duplicate skill names in package')
    for name in names:
        if not name or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in name):
            raise ValueError('Invalid skill name')
        if not (PACKAGE / 'skills' / name / 'SKILL.md').is_file():
            raise ValueError('Missing SKILL.md: ' + name)
    return manifest


def rollback(receipt_path, dry_run):
    receipt_path = receipt_path.resolve()
    receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    backup_root = receipt_path.parent
    actions = [a for a in receipt['actions'] if a['state'] != 'prepared']
    # Validate every saved original before changing any current install.
    for action in actions:
        target = Path(action['target'])
        if target.parent.resolve() != Path(action['parent']).resolve() or linked(target):
            raise ValueError('Unsafe rollback target: ' + str(target))
        if action['backup']:
            saved = Path(action['backup'])
            if backup_root not in saved.resolve().parents:
                raise ValueError('Backup is outside receipt directory')
            if not saved.is_dir() or tree_hash(saved) != action['backup_hash']:
                raise ValueError('Backup checksum mismatch: ' + str(saved))
    quarantine = backup_root / ('rollback-current-' + uuid.uuid4().hex[:8])
    for index, action in enumerate(reversed(actions)):
        target = Path(action['target'])
        print(('WOULD RESTORE ' if dry_run else 'RESTORE ') + str(target))
        if dry_run:
            continue
        if target.exists():
            dest = quarantine / str(index) / target.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            target.rename(dest)
        if action['backup']:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(action['backup'], target)
    print('Rollback dry-run complete.' if dry_run else 'Rollback complete; current files retained in quarantine.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skills-root', type=Path, default=Path.home() / '.agents/skills')
    parser.add_argument('--codex-home', type=Path, default=Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))))
    parser.add_argument('--workspace', type=Path, help='Create a NEW dedicated video workspace; refuses existing AGENTS.md')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--verify-only', action='store_true')
    parser.add_argument('--rollback', type=Path, metavar='RECEIPT_JSON')
    args = parser.parse_args()
    if args.rollback:
        rollback(args.rollback, args.dry_run)
        return
    manifest = verify()
    if args.verify_only:
        print('Verified package hashes and %d skill entrypoints.' % len(manifest['skills']))
        return
    root = args.skills_root.expanduser().resolve()
    codex = args.codex_home.expanduser().resolve()
    old_root = codex / 'skills'
    workspace = args.workspace.expanduser().resolve() if args.workspace else None
    if root == (PACKAGE / 'skills').resolve():
        raise ValueError('Cannot install onto package source')
    if workspace and (workspace / 'AGENTS.md').exists():
        raise ValueError('Existing workspace AGENTS.md preserved; choose a new video workspace')
    plan = []
    def add(source, target, label):
        if target.exists() and (not target.is_dir() or linked(target)):
            raise ValueError('Target is not a normal directory: ' + str(target))
        if not target.exists() or files(source) != files(target):
            plan.append((source, target, label))
    for skill in manifest['skills']:
        name = skill['name']
        add(PACKAGE / 'skills' / name, root / name, 'skill-' + name)
        duplicate = old_root / name
        if old_root.resolve() != root and (duplicate / 'SKILL.md').exists():
            if linked(duplicate):
                raise ValueError('Review linked legacy skill before installing: ' + str(duplicate))
            plan.append((None, duplicate, 'duplicate-' + name))
    preset = codex / 'video-presets' / manifest['snapshot_id']
    add(PACKAGE / 'presets' / 'legacy-world-motion', preset, 'legacy-preset')
    if workspace:
        if workspace.exists() and any(workspace.iterdir()):
            raise ValueError('Workspace must be new or empty; existing contents preserved')
        add(PACKAGE / 'workspace', workspace, 'video-workspace')
    for source, target, label in plan:
        print(('ARCHIVE DUPLICATE ' if source is None else 'INSTALL ') + str(target))
    if args.dry_run:
        print('Dry-run: no files changed; %d planned operations.' % len(plan))
        return
    if not plan:
        print('Already installed: all 19 skills and optional preset match this snapshot.')
        return
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
    backup = codex / 'backups' / 'video-production' / stamp
    backup.mkdir(parents=True)
    receipt_path = backup / 'receipt.json'
    receipt = {'snapshot_id': manifest['snapshot_id'], 'actions': []}
    def save():
        receipt_path.write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    save()
    for source, target, label in plan:
        if source:
            stage = backup / 'staging' / label
            stage.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, stage)
        original = backup / 'originals' / label if target.exists() else None
        action = {'target': str(target), 'parent': str(target.parent), 'backup': str(original) if original else None,
                  'backup_hash': tree_hash(target) if original else None, 'state': 'prepared'}
        receipt['actions'].append(action)
        save()
        if original:
            original.parent.mkdir(parents=True, exist_ok=True)
            target.rename(original)
            action['state'] = 'archived'
            save()
        if source:
            target.parent.mkdir(parents=True, exist_ok=True)
            stage.rename(target)
            action['state'] = 'installed'
            save()
    # Preserve relative references from old faceless skills, without restoring duplicate entrypoints.
    if old_root.resolve() != root:
        for name in manifest['legacy_support_names']:
            source = PACKAGE / 'skills' / name
            target = old_root / name
            if target.exists():
                continue  # Never overwrite existing support-only guides.
            stage = backup / 'staging' / ('support-' + name)
            shutil.copytree(source, stage, ignore=shutil.ignore_patterns('SKILL.md'))
            action = {'target': str(target), 'parent': str(target.parent), 'backup': None, 'backup_hash': None, 'state': 'prepared'}
            receipt['actions'].append(action)
            save()
            target.parent.mkdir(parents=True, exist_ok=True)
            stage.rename(target)
            action['state'] = 'installed'
            save()
    if workspace:
        for name in ['input', 'references', 'scripts', 'transcripts', 'storyboard', 'assets', 'src', 'templates', 'output', 'reports', 'backups']:
            (workspace / name).mkdir(exist_ok=True)
    print('Installed %d video skills. Restart Codex or open a new chat.' % len(manifest['skills']))
    print('Backup/rollback receipt: ' + str(receipt_path))
    print('No global AGENTS.md, config.toml, credentials or runtime binaries were installed.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError) as error:
        print('ERROR: ' + str(error), file=sys.stderr)
        sys.exit(1)
