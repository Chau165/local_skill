#!/usr/bin/env python3
'Initialize and validate an evidence-grounded faceless-channel workspace.'

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


VERSION = '1.0'
JOB_FILE = 'job-spec.json'
EVIDENCE_FILE = 'evidence.jsonl'
PROFILE_FILE = 'channel-profile.json'
STATUSES = {'observed', 'inferred', 'unknown'}
CONFIDENCE = {'low', 'medium', 'high', 'not-applicable'}
SCREENSHOT_RESTRICTED = {'retention', 'revenue', 'spoken-words'}
TEMPORAL_TOPICS = {
    'motion-density',
    'camera-motion',
    'subject-motion',
    'environment-motion',
    'interaction-motion',
    'depth-motion',
    'static-hold',
}
PROHIBITED_COPYING = {
    'channel_name_or_handle',
    'logo',
    'banner',
    'thumbnail',
    'script_or_transcript',
    'voice_or_voiceprint',
}
ORIGINALITY_REQUIREMENTS = {
    'create_original_brand_identity',
    'create_original_visual_assets',
    'write_original_script',
    'use_non-impersonating_voice',
}
FORBIDDEN_PAYLOAD_FIELDS = {
    'channel_name',
    'channel_handle',
    'logo',
    'logo_url',
    'banner',
    'banner_url',
    'thumbnail',
    'thumbnail_url',
    'thumbnail_image',
    'script',
    'transcript',
    'voice_sample',
    'voiceprint',
    'voice_clone',
    'narrator_identity',
}
IMAGE_SUFFIXES = {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp', '.tif', '.tiff', '.svg'}
VIDEO_SUFFIXES = {'.mp4', '.mov', '.m4v', '.webm', '.mkv', '.avi'}
EVIDENCE_ID_RE = re.compile(r'^ev-[a-z0-9][a-z0-9-]*$')
SLUG_RE = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
LANGUAGE_RE = re.compile(r'^[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*$')


class WorkspaceError(ValueError):
    pass


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def as_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise WorkspaceError(f'{label} must be a JSON object')
    return value


def as_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise WorkspaceError(f'{label} must be a JSON array')
    return value


def as_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise WorkspaceError(f'{label} must be a non-empty string')
    return value


def reject_prohibited_payload_fields(value: Any, label: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).lower().replace('-', '_')
            if normalized in FORBIDDEN_PAYLOAD_FIELDS:
                raise WorkspaceError(f'{label} contains prohibited copied-material field: {key}')
            reject_prohibited_payload_fields(child, f'{label}.{key}')
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_prohibited_payload_fields(child, f'{label}[{index}]')


def checked_url(value: str, label: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {'http', 'https'} or not parsed.netloc:
        raise WorkspaceError(f'{label} must be an absolute HTTP(S) URL: {value!r}')
    return value


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def read_json(path: Path, label: str) -> Any:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except FileNotFoundError as exc:
        raise WorkspaceError(f'Missing {label}: {path}') from exc
    except json.JSONDecodeError as exc:
        raise WorkspaceError(f'Invalid JSON in {label} at line {exc.lineno}: {exc.msg}') from exc


def build_sources(
    channel_url: str | None, screenshots: list[str], video_urls: list[str], video_files: list[str]
) -> list[dict[str, Any]]:
    sources: list[dict[str, Any]] = []
    if channel_url:
        sources.append(
            {'id': 'src-channel-001', 'type': 'channel-page', 'url': checked_url(channel_url, 'channel URL')}
        )
    for index, value in enumerate(screenshots, start=1):
        path = Path(value).expanduser().resolve()
        if not path.is_file():
            raise WorkspaceError(f'Screenshot does not exist or is not a file: {value}')
        if path.suffix.lower() not in IMAGE_SUFFIXES:
            allowed = ', '.join(sorted(IMAGE_SUFFIXES))
            raise WorkspaceError(f'Screenshot must use a supported image suffix ({allowed}): {value}')
        sources.append(
            {
                'id': f'src-screenshot-{index:03d}',
                'type': 'screenshot',
                'path': str(path),
                'sha256': file_hash(path),
            }
        )
    for index, value in enumerate(video_urls, start=1):
        sources.append(
            {
                'id': f'src-video-{index:03d}',
                'type': 'video',
                'url': checked_url(value, 'sample-video URL'),
            }
        )
    for index, value in enumerate(video_files, start=1):
        path = Path(value).expanduser().resolve()
        if not path.is_file():
            raise WorkspaceError(f'Sample video does not exist or is not a file: {value}')
        if path.suffix.lower() not in VIDEO_SUFFIXES:
            allowed = ', '.join(sorted(VIDEO_SUFFIXES))
            raise WorkspaceError(f'Sample video must use a supported suffix ({allowed}): {value}')
        sources.append(
            {
                'id': f'src-video-file-{index:03d}',
                'type': 'video-file',
                'path': str(path),
                'sha256': file_hash(path),
            }
        )
    if not sources:
        raise WorkspaceError('Provide at least one --channel-url, --screenshot, or --sample-video-url input')
    return sources


def init_workspace(args: argparse.Namespace) -> None:
    workspace = Path(args.workspace).expanduser().resolve()
    outputs = [workspace / JOB_FILE, workspace / EVIDENCE_FILE, workspace / PROFILE_FILE]
    existing = [str(path) for path in outputs if path.exists()]
    if existing:
        raise WorkspaceError('Refusing to overwrite existing workspace files: ' + ', '.join(existing))
    if not LANGUAGE_RE.fullmatch(args.language):
        raise WorkspaceError("language must be a simple BCP 47 tag such as 'vi' or 'vi-VN'")

    sources = build_sources(args.channel_url, args.screenshot, args.sample_video_url, args.sample_video_file)
    created_at = now_utc()
    seed = '|'.join([created_at] + [source.get('url', source.get('path', '')) for source in sources])
    job_id = 'job-' + hashlib.sha256(seed.encode('utf-8')).hexdigest()[:12]
    screenshot_only = all(source['type'] == 'screenshot' for source in sources)
    temporal_video_available = any(source['type'] in {'video', 'video-file'} for source in sources)

    job = {
        'schema_version': VERSION,
        'job_id': job_id,
        'created_at': created_at,
        'inputs': {
            'channel_url': args.channel_url,
            'screenshot_source_ids': [source['id'] for source in sources if source['type'] == 'screenshot'],
            'sample_video_source_ids': [source['id'] for source in sources if source['type'] == 'video'],
            'sample_video_file_source_ids': [source['id'] for source in sources if source['type'] == 'video-file'],
            'language': args.language,
        },
        'sources': sources,
        'analysis_policy': {
            'allowed_access': 'public-or-user-supplied',
            'paid_apis_allowed': False,
            'bypass_access_controls_allowed': False,
            'claim_statuses': sorted(STATUSES),
            'single_screenshot_cannot_establish': sorted(SCREENSHOT_RESTRICTED),
            'screenshot_only_scope': 'visual-observations-and-explicit-unknowns',
            'temporal_motion_requires_video': True,
        },
        'originality_policy': {
            'mode': 'pattern-transfer-only',
            'prohibited_copying': sorted(PROHIBITED_COPYING),
        },
    }
    profile = {
        'schema_version': VERSION,
        'job_id': job_id,
        'analysis_status': 'draft',
        'language': args.language,
        'summary': {
            'status': 'unknown',
            'claim': 'Analysis has not been completed.',
            'evidence_ids': [],
        },
        'source_coverage': [
            {'source_id': source['id'], 'status': 'unknown', 'notes': 'Source has not been analyzed.'}
            for source in sources
        ],
        'motion_profile': {
            'status': 'unknown',
            'evidence_ids': [],
            'motion_density': 'unknown',
            'camera_motion_patterns': [],
            'subject_motion_patterns': [],
            'environment_motion_patterns': [],
            'interaction_patterns': [],
            'depth_patterns': [],
            'static_hold_behavior': (
                'Not analyzed yet.' if temporal_video_available else 'Unknown without temporal video evidence.'
            ),
            'adaptation_principle': 'Do not infer motion from still images.',
        },
        'patterns': [],
        'unknowns': [
            {
                'topic': 'content-analysis-scope' if screenshot_only else 'retention',
                'status': 'unknown',
                'reason': (
                    'Screenshot-only input supports visual observations, not full content analysis.'
                    if screenshot_only
                    else 'No first-party retention analytics were supplied.'
                ),
                'evidence_ids': [],
            },
            {
                'topic': 'revenue',
                'status': 'unknown',
                'reason': 'No first-party revenue records were supplied.',
                'evidence_ids': [],
            },
            {
                'topic': 'spoken-words',
                'status': 'unknown',
                'reason': 'No sample-video audio or legitimate captions have been inspected.',
                'evidence_ids': [],
            },
        ],
        'originality_guardrails': {
            'mode': 'pattern-transfer-only',
            'prohibited_copying': sorted(PROHIBITED_COPYING),
            'requirements': sorted(ORIGINALITY_REQUIREMENTS),
        },
    }

    workspace.mkdir(parents=True, exist_ok=True)
    write_json(workspace / JOB_FILE, job)
    (workspace / EVIDENCE_FILE).write_text('', encoding='utf-8')
    write_json(workspace / PROFILE_FILE, profile)
    print(f'Initialized {workspace}')
    for output in outputs:
        print(f'- {output.name}')


def validate_job(job: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if job.get('schema_version') != VERSION:
        raise WorkspaceError(f'{JOB_FILE}.schema_version must be {VERSION!r}')
    as_text(job.get('job_id'), f'{JOB_FILE}.job_id')
    inputs = as_dict(job.get('inputs'), f'{JOB_FILE}.inputs')
    channel_url = inputs.get('channel_url')
    if channel_url is not None:
        checked_url(as_text(channel_url, 'inputs.channel_url'), 'channel URL')
    language = as_text(inputs.get('language'), 'inputs.language')
    if not LANGUAGE_RE.fullmatch(language):
        raise WorkspaceError('inputs.language must be a simple BCP 47 tag')

    sources: dict[str, dict[str, Any]] = {}
    for index, raw in enumerate(as_list(job.get('sources'), f'{JOB_FILE}.sources')):
        source = as_dict(raw, f'sources[{index}]')
        source_id = as_text(source.get('id'), f'sources[{index}].id')
        if source_id in sources:
            raise WorkspaceError(f'Duplicate source ID: {source_id}')
        source_type = source.get('type')
        if source_type not in {'channel-page', 'screenshot', 'video', 'video-file'}:
            raise WorkspaceError(f'Unsupported source type for {source_id}: {source_type!r}')
        if source_type in {'screenshot', 'video-file'}:
            path = Path(as_text(source.get('path'), f'{source_id}.path'))
            digest = as_text(source.get('sha256'), f'{source_id}.sha256')
            if not path.is_file():
                raise WorkspaceError(f'Local source is missing or is not a file for {source_id}: {path}')
            allowed_suffixes = IMAGE_SUFFIXES if source_type == 'screenshot' else VIDEO_SUFFIXES
            if path.suffix.lower() not in allowed_suffixes:
                allowed = ', '.join(sorted(allowed_suffixes))
                raise WorkspaceError(f'Local source for {source_id} must use a supported suffix ({allowed}): {path}')
            if not re.fullmatch(r'[0-9a-f]{64}', digest):
                raise WorkspaceError(f'{source_id}.sha256 must be a lowercase SHA-256 digest')
            if file_hash(path) != digest:
                raise WorkspaceError(f'Screenshot hash changed for {source_id}: {path}')
        else:
            checked_url(as_text(source.get('url'), f'{source_id}.url'), f'{source_id} URL')
        sources[source_id] = source
    if not sources:
        raise WorkspaceError('At least one registered source is required')

    screenshot_ids = as_list(inputs.get('screenshot_source_ids'), 'inputs.screenshot_source_ids')
    video_ids = as_list(inputs.get('sample_video_source_ids'), 'inputs.sample_video_source_ids')
    video_file_ids = as_list(inputs.get('sample_video_file_source_ids'), 'inputs.sample_video_file_source_ids')
    expected_screenshots = {key for key, value in sources.items() if value['type'] == 'screenshot'}
    expected_videos = {key for key, value in sources.items() if value['type'] == 'video'}
    expected_video_files = {key for key, value in sources.items() if value['type'] == 'video-file'}
    if set(screenshot_ids) != expected_screenshots:
        raise WorkspaceError('inputs.screenshot_source_ids must match registered screenshots')
    if set(video_ids) != expected_videos:
        raise WorkspaceError('inputs.sample_video_source_ids must match registered videos')
    if set(video_file_ids) != expected_video_files:
        raise WorkspaceError('inputs.sample_video_file_source_ids must match registered local videos')
    if channel_url is None and any(value['type'] == 'channel-page' for value in sources.values()):
        raise WorkspaceError('inputs.channel_url must identify the registered channel-page source')

    policy = as_dict(job.get('analysis_policy'), 'analysis_policy')
    if policy.get('paid_apis_allowed') is not False:
        raise WorkspaceError('analysis_policy.paid_apis_allowed must be false')
    if policy.get('bypass_access_controls_allowed') is not False:
        raise WorkspaceError('analysis_policy.bypass_access_controls_allowed must be false')
    if set(as_list(policy.get('claim_statuses'), 'analysis_policy.claim_statuses')) != STATUSES:
        raise WorkspaceError('analysis_policy.claim_statuses must preserve observed/inferred/unknown')
    restricted = set(
        as_list(policy.get('single_screenshot_cannot_establish'), 'analysis_policy.single_screenshot_cannot_establish')
    )
    if not SCREENSHOT_RESTRICTED.issubset(restricted):
        raise WorkspaceError('analysis_policy must protect retention, revenue, and spoken-words')

    originality = as_dict(job.get('originality_policy'), 'originality_policy')
    if originality.get('mode') != 'pattern-transfer-only':
        raise WorkspaceError("originality_policy.mode must be 'pattern-transfer-only'")
    prohibited = set(as_list(originality.get('prohibited_copying'), 'originality_policy.prohibited_copying'))
    if not PROHIBITED_COPYING.issubset(prohibited):
        raise WorkspaceError('originality_policy.prohibited_copying is missing protections')
    return sources


def read_evidence(path: Path) -> list[dict[str, Any]]:
    try:
        text = path.read_text(encoding='utf-8')
    except FileNotFoundError as exc:
        raise WorkspaceError(f'Missing {EVIDENCE_FILE}: {path}') from exc
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            raise WorkspaceError(f'Blank line in {EVIDENCE_FILE} at line {line_number}')
        try:
            records.append(as_dict(json.loads(line), f'{EVIDENCE_FILE} line {line_number}'))
        except json.JSONDecodeError as exc:
            raise WorkspaceError(f'Invalid JSON in {EVIDENCE_FILE} at line {line_number}: {exc.msg}') from exc
    return records


def validate_evidence(
    records: list[dict[str, Any]], sources: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    evidence: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(records):
        label = f'evidence[{index}]'
        reject_prohibited_payload_fields(record, label)
        evidence_id = as_text(record.get('id'), f'{label}.id')
        if not EVIDENCE_ID_RE.fullmatch(evidence_id):
            raise WorkspaceError(f'{label}.id must match ev-[a-z0-9-]+')
        if evidence_id in evidence:
            raise WorkspaceError(f'Duplicate evidence ID: {evidence_id}')
        status = record.get('status')
        if status not in STATUSES:
            raise WorkspaceError(f'{evidence_id}.status must be observed, inferred, or unknown')
        topic = as_text(record.get('topic'), f'{evidence_id}.topic')
        if not SLUG_RE.fullmatch(topic):
            raise WorkspaceError(f'{evidence_id}.topic must be a lowercase hyphenated slug')
        as_text(record.get('claim'), f'{evidence_id}.claim')
        if record.get('confidence') not in CONFIDENCE:
            raise WorkspaceError(f'{evidence_id}.confidence is invalid')
        source_ids = as_list(record.get('source_ids'), f'{evidence_id}.source_ids')
        basis_ids = as_list(record.get('basis_evidence_ids'), f'{evidence_id}.basis_evidence_ids')
        for source_id in source_ids:
            if source_id not in sources:
                raise WorkspaceError(f'{evidence_id} references unknown source ID: {source_id}')
        if status == 'observed':
            if not source_ids:
                raise WorkspaceError(f'Observed evidence {evidence_id} requires source_ids')
            locator = as_dict(record.get('locator'), f'{evidence_id}.locator')
            as_text(locator.get('kind'), f'{evidence_id}.locator.kind')
            as_text(locator.get('value'), f'{evidence_id}.locator.value')
            if basis_ids:
                raise WorkspaceError(f'Observed evidence {evidence_id} cannot have basis_evidence_ids')
        elif status == 'inferred':
            if not basis_ids:
                raise WorkspaceError(f'Inferred evidence {evidence_id} requires basis_evidence_ids')
            if record.get('locator') is not None:
                raise WorkspaceError(f'Inferred evidence {evidence_id} must use a null locator')
        else:
            if record.get('confidence') != 'not-applicable':
                raise WorkspaceError(f'Unknown evidence {evidence_id} must use not-applicable confidence')
            as_text(record.get('reason'), f'{evidence_id}.reason')
            if basis_ids:
                raise WorkspaceError(f'Unknown evidence {evidence_id} cannot have basis_evidence_ids')
        evidence[evidence_id] = record

    for evidence_id, record in evidence.items():
        for basis_id in record.get('basis_evidence_ids', []):
            if basis_id not in evidence:
                raise WorkspaceError(f'{evidence_id} references unknown basis evidence ID: {basis_id}')

    active: set[str] = set()
    done: set[str] = set()

    def visit(evidence_id: str) -> None:
        if evidence_id in done:
            return
        if evidence_id in active:
            raise WorkspaceError(f'Evidence dependency cycle includes {evidence_id}')
        active.add(evidence_id)
        for basis_id in evidence[evidence_id].get('basis_evidence_ids', []):
            visit(basis_id)
        active.remove(evidence_id)
        done.add(evidence_id)

    for evidence_id in evidence:
        visit(evidence_id)

    def leaf_sources(evidence_id: str) -> set[str]:
        record = evidence[evidence_id]
        if record['status'] != 'inferred':
            return set(record.get('source_ids', []))
        leaves: set[str] = set()
        for basis_id in record['basis_evidence_ids']:
            leaves.update(leaf_sources(basis_id))
        return leaves

    for evidence_id, record in evidence.items():
        if record['topic'] in SCREENSHOT_RESTRICTED and record['status'] != 'unknown':
            leaves = leaf_sources(evidence_id)
            source_types = {sources[source_id]['type'] for source_id in leaves}
            if leaves and source_types == {'screenshot'}:
                raise WorkspaceError(
                    '{} infers {} from screenshot-only evidence; mark it unknown or add valid evidence'.format(
                        evidence_id, record['topic']
                    )
                )
        if record['topic'] in TEMPORAL_TOPICS and record['status'] != 'unknown':
            temporal_leaves = leaf_sources(evidence_id)
            temporal_types = {sources[source_id]['type'] for source_id in temporal_leaves}
            if not temporal_types.intersection({'video', 'video-file'}):
                raise WorkspaceError(
                    f'{evidence_id} claims temporal motion without a video or video-file evidence source'
                )
    return evidence


def linked_ids(value: Any, evidence: dict[str, dict[str, Any]], label: str) -> list[str]:
    ids = as_list(value, label)
    for evidence_id in ids:
        if evidence_id not in evidence:
            raise WorkspaceError(f'{label} references unknown evidence ID: {evidence_id}')
    return ids


def validate_profile(
    profile: dict[str, Any],
    job: dict[str, Any],
    sources: dict[str, dict[str, Any]],
    evidence: dict[str, dict[str, Any]],
) -> None:
    reject_prohibited_payload_fields(profile, PROFILE_FILE)
    if profile.get('schema_version') != VERSION:
        raise WorkspaceError(f'{PROFILE_FILE}.schema_version must be {VERSION!r}')
    if profile.get('job_id') != job.get('job_id'):
        raise WorkspaceError(f'{PROFILE_FILE}.job_id must match {JOB_FILE}.job_id')
    if profile.get('language') != job['inputs']['language']:
        raise WorkspaceError(f'{PROFILE_FILE}.language must match the job language')
    analysis_status = profile.get('analysis_status')
    if analysis_status not in {'draft', 'complete'}:
        raise WorkspaceError('analysis_status must be draft or complete')

    summary = as_dict(profile.get('summary'), 'summary')
    if summary.get('status') not in STATUSES:
        raise WorkspaceError('summary.status must be observed, inferred, or unknown')
    as_text(summary.get('claim'), 'summary.claim')
    linked_ids(summary.get('evidence_ids'), evidence, 'summary.evidence_ids')

    coverage_ids: set[str] = set()
    coverage = as_list(profile.get('source_coverage'), 'source_coverage')
    for index, raw in enumerate(coverage):
        item = as_dict(raw, f'source_coverage[{index}]')
        source_id = as_text(item.get('source_id'), f'source_coverage[{index}].source_id')
        if source_id not in sources or source_id in coverage_ids:
            raise WorkspaceError(f'Invalid or duplicate source_coverage ID: {source_id}')
        if item.get('status') not in {'observed', 'unknown'}:
            raise WorkspaceError(f'source_coverage[{index}].status must be observed or unknown')
        as_text(item.get('notes'), f'source_coverage[{index}].notes')
        coverage_ids.add(source_id)
    if coverage_ids != set(sources):
        raise WorkspaceError('source_coverage must contain every registered source exactly once')

    motion = as_dict(profile.get('motion_profile'), 'motion_profile')
    if motion.get('status') not in STATUSES:
        raise WorkspaceError('motion_profile.status must be observed, inferred, or unknown')
    motion_evidence_ids = linked_ids(motion.get('evidence_ids'), evidence, 'motion_profile.evidence_ids')
    if motion.get('motion_density') not in {'continuous', 'frequent', 'selective', 'sparse', 'unknown'}:
        raise WorkspaceError('motion_profile.motion_density is invalid')
    for field in (
        'camera_motion_patterns',
        'subject_motion_patterns',
        'environment_motion_patterns',
        'interaction_patterns',
        'depth_patterns',
    ):
        values = as_list(motion.get(field), f'motion_profile.{field}')
        if any(not isinstance(item, str) or not item.strip() for item in values):
            raise WorkspaceError(f'motion_profile.{field} must contain only non-empty strings')
    as_text(motion.get('static_hold_behavior'), 'motion_profile.static_hold_behavior')
    as_text(motion.get('adaptation_principle'), 'motion_profile.adaptation_principle')
    if motion.get('status') in {'observed', 'inferred'} and not motion_evidence_ids:
        raise WorkspaceError('observed/inferred motion_profile requires temporal evidence IDs')
    if motion.get('status') == 'unknown' and motion.get('motion_density') != 'unknown':
        raise WorkspaceError('unknown motion_profile must use motion_density unknown')

    patterns = as_list(profile.get('patterns'), 'patterns')
    pattern_ids: set[str] = set()
    for index, raw in enumerate(patterns):
        pattern = as_dict(raw, f'patterns[{index}]')
        pattern_id = as_text(pattern.get('id'), f'patterns[{index}].id')
        if pattern_id in pattern_ids:
            raise WorkspaceError(f'Duplicate pattern ID: {pattern_id}')
        pattern_ids.add(pattern_id)
        as_text(pattern.get('category'), f'{pattern_id}.category')
        as_text(pattern.get('label'), f'{pattern_id}.label')
        as_text(pattern.get('claim'), f'{pattern_id}.claim')
        if pattern.get('status') not in STATUSES:
            raise WorkspaceError(f'{pattern_id}.status must be observed, inferred, or unknown')
        if pattern.get('confidence') not in {'low', 'medium', 'high'}:
            raise WorkspaceError(f'{pattern_id}.confidence must be low, medium, or high')
        evidence_ids = linked_ids(pattern.get('evidence_ids'), evidence, f'{pattern_id}.evidence_ids')
        if not evidence_ids:
            raise WorkspaceError(f'Every pattern must trace to evidence; {pattern_id} is ungrounded')
        if pattern['status'] == 'unknown' and not any(evidence[item]['status'] == 'unknown' for item in evidence_ids):
            raise WorkspaceError(f'Unknown pattern {pattern_id} must reference unknown evidence')
        as_text(pattern.get('adaptation_principle'), f'{pattern_id}.adaptation_principle')

    for index, raw in enumerate(as_list(profile.get('unknowns'), 'unknowns')):
        item = as_dict(raw, f'unknowns[{index}]')
        as_text(item.get('topic'), f'unknowns[{index}].topic')
        if item.get('status') != 'unknown':
            raise WorkspaceError(f'unknowns[{index}].status must be unknown')
        as_text(item.get('reason'), f'unknowns[{index}].reason')
        linked_ids(item.get('evidence_ids'), evidence, f'unknowns[{index}].evidence_ids')

    guardrails = as_dict(profile.get('originality_guardrails'), 'originality_guardrails')
    if guardrails.get('mode') != 'pattern-transfer-only':
        raise WorkspaceError("originality_guardrails.mode must be 'pattern-transfer-only'")
    prohibited = set(as_list(guardrails.get('prohibited_copying'), 'originality_guardrails.prohibited_copying'))
    if not PROHIBITED_COPYING.issubset(prohibited):
        raise WorkspaceError('originality_guardrails.prohibited_copying is missing protections')
    requirements = set(as_list(guardrails.get('requirements'), 'originality_guardrails.requirements'))
    if not ORIGINALITY_REQUIREMENTS.issubset(requirements):
        raise WorkspaceError('originality_guardrails.requirements is missing originality actions')

    if analysis_status == 'complete':
        if not evidence or not patterns:
            raise WorkspaceError('A complete analysis requires evidence and at least one linked pattern')
        if any(item['status'] == 'unknown' for item in coverage):
            raise WorkspaceError('A complete analysis cannot leave a source unreviewed')
        has_temporal_source = any(source['type'] in {'video', 'video-file'} for source in sources.values())
        if has_temporal_source and motion.get('status') == 'unknown':
            raise WorkspaceError('A complete analysis with video evidence cannot leave motion_profile unknown')


def validate_workspace(args: argparse.Namespace) -> None:
    workspace = Path(args.workspace).expanduser().resolve()
    job = as_dict(read_json(workspace / JOB_FILE, JOB_FILE), JOB_FILE)
    sources = validate_job(job)
    evidence = validate_evidence(read_evidence(workspace / EVIDENCE_FILE), sources)
    profile = as_dict(read_json(workspace / PROFILE_FILE, PROFILE_FILE), PROFILE_FILE)
    validate_profile(profile, job, sources, evidence)
    print(
        f"Valid workspace: {workspace} ({len(sources)} sources, "
        f"{len(evidence)} evidence records, {len(profile['patterns'])} patterns)"
    )


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        description='Initialize or validate faceless-channel analysis files without external APIs.'
    )
    commands = root.add_subparsers(dest='command', required=True)
    init = commands.add_parser('init', help='Create job-spec.json, evidence.jsonl, and channel-profile.json')
    init.add_argument('workspace', help='Output workspace directory')
    init.add_argument('--channel-url', help='Public channel URL')
    init.add_argument('--screenshot', action='append', default=[], help='Local image path; repeat as needed')
    init.add_argument(
        '--sample-video-url', action='append', default=[], help='Public sample-video URL; repeat as needed'
    )
    init.add_argument(
        '--sample-video-file', action='append', default=[], help='Local sample-video path; repeat as needed'
    )
    init.add_argument('--language', required=True, help='BCP 47 language tag, for example vi or vi-VN')
    init.set_defaults(handler=init_workspace)
    validate = commands.add_parser('validate', help='Validate schemas, source links, and evidence links')
    validate.add_argument('workspace', help='Workspace directory to validate')
    validate.set_defaults(handler=validate_workspace)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        args.handler(args)
    except (WorkspaceError, OSError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
