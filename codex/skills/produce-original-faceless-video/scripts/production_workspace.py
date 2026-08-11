#!/usr/bin/env python3
"""Initialize and validate an approval-gated faceless-video workspace."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1.0"
STAGES = ("structure", "concept", "script", "rough", "final")
MODES = ("image_only", "image_video")
CHECKPOINTS = ("concept", "script", "budget", "rough", "final")
STATUS_VALUES = {"draft", "pending_review", "approved", "rejected"}
ID_PATTERN = re.compile(r"^[a-z][a-z0-9-]*$")
HASH_PATTERN = re.compile(r"^[0-9a-f]{64}$")
ENV_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]*$")
ASPECT_PATTERN = re.compile(r"^(\d+(?:\.\d+)?):(\d+(?:\.\d+)?)$")
ANALYZER_STATUSES = {"observed", "inferred", "unknown"}
REQUIRED_PROHIBITED_COPYING = {
    "channel_name_or_handle",
    "logo",
    "banner",
    "thumbnail",
    "script_or_transcript",
    "voice_or_voiceprint",
}
REQUIRED_ORIGINALITY_ACTIONS = {
    "create_original_brand_identity",
    "create_original_visual_assets",
    "write_original_script",
    "use_non-impersonating_voice",
}
FORBIDDEN_PROFILE_FIELDS = {
    "channel_name",
    "channel_handle",
    "logo",
    "logo_url",
    "banner",
    "banner_url",
    "thumbnail",
    "thumbnail_url",
    "thumbnail_image",
    "script",
    "transcript",
    "voice_sample",
    "voiceprint",
    "voice_clone",
    "narrator_identity",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")
    return (slug[:40].rstrip("-") or "faceless-video") + "-" + uuid.uuid4().hex[:8]


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def parse_aspect_ratio(value: str) -> str:
    match = ASPECT_PATTERN.fullmatch(value.strip())
    if not match or float(match.group(1)) <= 0 or float(match.group(2)) <= 0:
        raise argparse.ArgumentTypeError("aspect ratio must be positive W:H, for example 9:16")
    return value.strip()


def positive_duration(value: str) -> int:
    try:
        duration = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("duration must be a whole number of seconds") from exc
    if duration <= 0:
        raise argparse.ArgumentTypeError("duration must be greater than zero")
    return duration


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def channel_profile_contract_errors(profile: Any, prefix: str = "channel-profile.json") -> list[str]:
    """Return analyzer-to-producer handoff violations without mutating the profile."""
    errors: list[str] = []

    def add(location: str, message: str) -> None:
        errors.append(f"{prefix}.{location}: {message}")

    def require_text(value: Any, location: str) -> bool:
        if not isinstance(value, str) or not value.strip():
            add(location, "must be a non-empty string")
            return False
        return True

    def reject_copy_payloads(value: Any, location: str = "$") -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                child_location = f"{location}.{key}"
                normalized = str(key).lower().replace("-", "_")
                if normalized in FORBIDDEN_PROFILE_FIELDS:
                    add(child_location, "copying-unsafe payload field is prohibited")
                reject_copy_payloads(child, child_location)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                reject_copy_payloads(child, f"{location}[{index}]")

    if not isinstance(profile, dict):
        return [f"{prefix}: must be a JSON object"]
    reject_copy_payloads(profile)

    if profile.get("schema_version") != SCHEMA_VERSION:
        add("schema_version", f"must equal {SCHEMA_VERSION!r}")
    require_text(profile.get("job_id"), "job_id")
    require_text(profile.get("language"), "language")
    if profile.get("analysis_status") != "complete":
        add("analysis_status", "must be 'complete'; draft analysis cannot enter production")

    summary = profile.get("summary")
    if not isinstance(summary, dict):
        add("summary", "must be an object")
    else:
        if summary.get("status") not in ANALYZER_STATUSES:
            add("summary.status", "must be observed, inferred, or unknown")
        require_text(summary.get("claim"), "summary.claim")
        summary_evidence = summary.get("evidence_ids")
        if not isinstance(summary_evidence, list) or any(
            not isinstance(item, str) or not item.strip() for item in summary_evidence
        ):
            add("summary.evidence_ids", "must be an array of non-empty evidence IDs")

    coverage = profile.get("source_coverage")
    coverage_ids: set[str] = set()
    if not isinstance(coverage, list) or not coverage:
        add("source_coverage", "must contain at least one reviewed source")
    else:
        for index, item in enumerate(coverage):
            location = f"source_coverage[{index}]"
            if not isinstance(item, dict):
                add(location, "must be an object")
                continue
            source_id = item.get("source_id")
            if require_text(source_id, f"{location}.source_id"):
                if source_id in coverage_ids:
                    add(f"{location}.source_id", "must be unique")
                coverage_ids.add(source_id)
            if item.get("status") != "observed":
                add(f"{location}.status", "must be 'observed' for a complete analysis")
            require_text(item.get("notes"), f"{location}.notes")

    patterns = profile.get("patterns")
    pattern_ids: set[str] = set()
    if not isinstance(patterns, list) or not patterns:
        add("patterns", "must contain at least one evidence-linked pattern")
    else:
        for index, pattern in enumerate(patterns):
            location = f"patterns[{index}]"
            if not isinstance(pattern, dict):
                add(location, "must be an object")
                continue
            pattern_id = pattern.get("id")
            if require_text(pattern_id, f"{location}.id"):
                if pattern_id in pattern_ids:
                    add(f"{location}.id", "must be unique")
                pattern_ids.add(pattern_id)
            for field in ("category", "label", "claim", "adaptation_principle"):
                require_text(pattern.get(field), f"{location}.{field}")
            if pattern.get("status") not in ANALYZER_STATUSES:
                add(f"{location}.status", "must be observed, inferred, or unknown")
            if pattern.get("confidence") not in {"low", "medium", "high"}:
                add(f"{location}.confidence", "must be low, medium, or high")
            evidence_ids = pattern.get("evidence_ids")
            if not isinstance(evidence_ids, list) or not evidence_ids:
                add(f"{location}.evidence_ids", "must contain at least one evidence ID")
            elif any(not isinstance(item, str) or not item.strip() for item in evidence_ids):
                add(f"{location}.evidence_ids", "must contain only non-empty evidence IDs")

    unknowns = profile.get("unknowns")
    if not isinstance(unknowns, list):
        add("unknowns", "must be an array")

    motion = profile.get("motion_profile")
    if not isinstance(motion, dict):
        add("motion_profile", "must be an object produced by the analyzer")
    else:
        if motion.get("status") not in ANALYZER_STATUSES:
            add("motion_profile.status", "must be observed, inferred, or unknown")
        evidence_ids = motion.get("evidence_ids")
        if not isinstance(evidence_ids, list) or any(
            not isinstance(item, str) or not item.strip() for item in evidence_ids
        ):
            add("motion_profile.evidence_ids", "must be an array of non-empty evidence IDs")
        if motion.get("motion_density") not in {"continuous", "frequent", "selective", "sparse", "unknown"}:
            add("motion_profile.motion_density", "is invalid")
        for field in (
            "camera_motion_patterns",
            "subject_motion_patterns",
            "environment_motion_patterns",
            "interaction_patterns",
            "depth_patterns",
        ):
            values = motion.get(field)
            if not isinstance(values, list) or any(not isinstance(item, str) or not item.strip() for item in values):
                add(f"motion_profile.{field}", "must be an array of non-empty strings")
        require_text(motion.get("static_hold_behavior"), "motion_profile.static_hold_behavior")
        require_text(motion.get("adaptation_principle"), "motion_profile.adaptation_principle")

    guardrails = profile.get("originality_guardrails")
    if not isinstance(guardrails, dict):
        add("originality_guardrails", "must be an object")
    else:
        if guardrails.get("mode") != "pattern-transfer-only":
            add("originality_guardrails.mode", "must be 'pattern-transfer-only'")
        prohibited = guardrails.get("prohibited_copying")
        if not isinstance(prohibited, list) or any(not isinstance(item, str) for item in prohibited):
            add("originality_guardrails.prohibited_copying", "must be an array of strings")
        else:
            missing = sorted(REQUIRED_PROHIBITED_COPYING.difference(prohibited))
            if missing:
                add("originality_guardrails.prohibited_copying", f"missing required values: {', '.join(missing)}")
        requirements = guardrails.get("requirements")
        if not isinstance(requirements, list) or any(not isinstance(item, str) for item in requirements):
            add("originality_guardrails.requirements", "must be an array of strings")
        else:
            missing = sorted(REQUIRED_ORIGINALITY_ACTIONS.difference(requirements))
            if missing:
                add("originality_guardrails.requirements", f"missing required values: {', '.join(missing)}")
    return errors


def approval_template() -> dict[str, Any]:
    return {
        "approved": False,
        "approved_by": "",
        "approved_at": "",
        "scope": "",
        "limit": None,
    }


def checkpoint_template() -> dict[str, str]:
    return {"status": "pending", "approved_by": "", "approved_at": "", "notes": ""}


def init_workspace(args: argparse.Namespace) -> int:
    profile_path = Path(args.channel_profile).expanduser().resolve()
    if not profile_path.is_file():
        print(f"ERROR: channel profile does not exist: {profile_path}", file=sys.stderr)
        return 2
    try:
        profile = read_json(profile_path)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read channel profile: {exc}", file=sys.stderr)
        return 2
    if not isinstance(profile, dict):
        print("ERROR: channel profile must be a JSON object", file=sys.stderr)
        return 2
    profile_errors = channel_profile_contract_errors(profile, str(profile_path))
    if profile_errors:
        print("ERROR: channel profile failed the analyzer handoff contract:", file=sys.stderr)
        for error in profile_errors:
            print(f"- {error}", file=sys.stderr)
        return 2

    root = Path(args.output).expanduser().resolve()
    if root.exists() and (not root.is_dir() or any(root.iterdir())):
        print(f"ERROR: output must be a missing or empty directory: {root}", file=sys.stderr)
        return 2

    project_id = slugify(args.topic)
    created_at = utc_now()
    root.mkdir(parents=True, exist_ok=True)
    for directory in ("input", "assets/source", "assets/generated", "renders"):
        (root / directory).mkdir(parents=True, exist_ok=True)

    brief = {
        "schema_version": SCHEMA_VERSION,
        "project_id": project_id,
        "created_at": created_at,
        "channel_profile": "input/channel-profile.json",
        "topic": args.topic.strip(),
        "duration_seconds": args.duration_seconds,
        "language": args.language.strip(),
        "aspect_ratio": args.aspect_ratio,
        "mode": args.mode,
    }
    concept = {
        "schema_version": SCHEMA_VERSION,
        "status": "draft",
        "topic": args.topic.strip(),
        "audience": "",
        "premise": "",
        "viewer_promise": "",
        "angle": "",
        "hook_options": [],
        "selected_hook": "",
        "structure": [],
        "differentiation": [],
        "claim_ids": [],
        "notes": [],
    }
    script = {
        "schema_version": SCHEMA_VERSION,
        "status": "draft",
        "title": "",
        "language": args.language.strip(),
        "duration_seconds": args.duration_seconds,
        "segments": [],
    }
    storyboard = {
        "schema_version": SCHEMA_VERSION,
        "status": "draft",
        "mode": args.mode,
        "aspect_ratio": args.aspect_ratio,
        "duration_seconds": args.duration_seconds,
        "visual_grammar": "world_motion_explainer",
        "presentation_allowed": False,
        "world": {
            "setting": "",
            "visual_vocabulary": [],
            "subjects": [],
            "continuity_anchors": [],
        },
        "shots": [],
    }
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "project_id": project_id,
        "created_at": created_at,
        "mode": args.mode,
        "aspect_ratio": args.aspect_ratio,
        "duration_seconds": args.duration_seconds,
        "language": args.language.strip(),
        "sources": [],
        "claims": [],
        "claim_audit": {
            "status": "pending",
            "reviewed_by": "",
            "reviewed_at": "",
            "methodology": "",
            "limitations": "Semantic source relevance requires manual review",
        },
        "assets": [],
        "asset_inventory_complete": False,
        "original_assets_only": True,
        "motion_quality": {
            "status": "pending",
            "analysis_method": "",
            "sample_rate_fps": 0,
            "meaningful_motion_screen_time_ratio": 0.0,
            "distributed_motion_screen_time_ratio": 0.0,
            "independent_layer_motion_shot_ratio": 0.0,
            "interaction_shot_ratio": 0.0,
            "camera_only_screen_time_ratio": 1.0,
            "max_static_hold_seconds": None,
            "automated_report_path": "",
            "automated_report_sha256": "",
            "manual_reviewed_by": "",
            "manual_reviewed_at": "",
            "notes": [],
        },
        "provider_plan": [],
        "voice": {
            "mode": "none",
            "provider": "",
            "voice_id": "",
            "real_person_clone": False,
            "consent": {"confirmed": False, "evidence_locator": "", "confirmed_at": ""},
            "synthetic_voice_evidence": {
                "verified": False,
                "terms_locator": "",
                "checked_at": "",
                "notes": "",
            },
        },
        "budget": {
            "currency": "USD",
            "estimate_status": "not_estimated",
            "estimated_total": 0.0,
            "contingency_percent": 0.0,
            "line_items": [],
            "assumptions": [],
        },
        "permissions": {
            "paid_calls": approval_template(),
            "external_api_calls": approval_template(),
            "publishing": approval_template(),
        },
        "checkpoints": {name: checkpoint_template() for name in CHECKPOINTS},
        "renders": {
            "rough": {"asset_id": "", "status": "not_started"},
            "final": {"asset_id": "", "status": "not_started"},
        },
        "publish": {"automatic": False, "status": "not_requested"},
    }

    write_json(root / "input/channel-profile.json", profile)
    write_json(root / "input/brief.json", brief)
    write_json(root / "concept.json", concept)
    write_json(root / "script.json", script)
    write_json(root / "storyboard.json", storyboard)
    write_json(root / "production-manifest.json", manifest)
    print(f"Initialized production workspace: {root}")
    return 0


class WorkspaceValidator:
    def __init__(self, root: Path, stage: str) -> None:
        self.root = root.resolve()
        self.stage = stage
        self.errors: list[str] = []
        self.docs: dict[str, Any] = {}
        self.source_ids: set[str] = set()
        self.claim_ids: set[str] = set()
        self.asset_ids: set[str] = set()
        self.adapter_ids: set[str] = set()
        self.used_claim_ids: set[str] = set()
        self.used_asset_ids: set[str] = set()

    def error(self, location: str, message: str) -> None:
        self.errors.append(f"{location}: {message}")

    def nonempty_string(self, value: Any, location: str) -> bool:
        if not isinstance(value, str) or not value.strip():
            self.error(location, "must be a non-empty string")
            return False
        return True

    def load(self) -> bool:
        paths = {
            "profile": "input/channel-profile.json",
            "brief": "input/brief.json",
            "concept": "concept.json",
            "script": "script.json",
            "storyboard": "storyboard.json",
            "manifest": "production-manifest.json",
        }
        for name, relative in paths.items():
            path = self.root / relative
            if not path.is_file():
                self.error(relative, "required file is missing")
                continue
            try:
                value = read_json(path)
            except (OSError, json.JSONDecodeError) as exc:
                self.error(relative, f"cannot parse JSON: {exc}")
                continue
            if not isinstance(value, dict):
                self.error(relative, "top level must be a JSON object")
                continue
            self.docs[name] = value
        return len(self.docs) == len(paths)

    def validate(self) -> list[str]:
        if not self.root.is_dir():
            self.error(str(self.root), "workspace directory does not exist")
            return self.errors
        if not self.load():
            return self.errors
        self.errors.extend(
            channel_profile_contract_errors(self.docs["profile"], "input/channel-profile.json")
        )
        self.validate_versions()
        self.validate_brief()
        self.validate_consistency()
        self.validate_manifest()
        self.validate_concept()
        self.validate_script()
        self.validate_storyboard()
        self.validate_cross_references()
        self.validate_stage()
        return self.errors

    def validate_versions(self) -> None:
        for name in ("brief", "concept", "script", "storyboard", "manifest"):
            if self.docs[name].get("schema_version") != SCHEMA_VERSION:
                self.error(f"{name}.schema_version", f"must equal {SCHEMA_VERSION!r}")

    def validate_brief(self) -> None:
        brief = self.docs["brief"]
        self.nonempty_string(brief.get("project_id"), "brief.project_id")
        self.nonempty_string(brief.get("created_at"), "brief.created_at")
        self.nonempty_string(brief.get("topic"), "brief.topic")
        self.nonempty_string(brief.get("language"), "brief.language")
        if brief.get("channel_profile") != "input/channel-profile.json":
            self.error("brief.channel_profile", "must equal input/channel-profile.json")
        duration = brief.get("duration_seconds")
        if not isinstance(duration, int) or isinstance(duration, bool) or duration <= 0:
            self.error("brief.duration_seconds", "must be a positive integer")
        aspect = brief.get("aspect_ratio")
        if not isinstance(aspect, str) or not ASPECT_PATTERN.fullmatch(aspect):
            self.error("brief.aspect_ratio", "must use positive W:H syntax")
        else:
            left, right = aspect.split(":")
            if float(left) <= 0 or float(right) <= 0:
                self.error("brief.aspect_ratio", "components must be positive")
        if brief.get("mode") not in MODES:
            self.error("brief.mode", f"must be one of {', '.join(MODES)}")

    def validate_consistency(self) -> None:
        brief = self.docs["brief"]
        comparisons = (
            ("concept", "topic", "topic"),
            ("script", "language", "language"),
            ("script", "duration_seconds", "duration_seconds"),
            ("storyboard", "mode", "mode"),
            ("storyboard", "aspect_ratio", "aspect_ratio"),
            ("storyboard", "duration_seconds", "duration_seconds"),
            ("manifest", "project_id", "project_id"),
            ("manifest", "mode", "mode"),
            ("manifest", "aspect_ratio", "aspect_ratio"),
            ("manifest", "duration_seconds", "duration_seconds"),
            ("manifest", "language", "language"),
        )
        for document, field, brief_field in comparisons:
            if self.docs[document].get(field) != brief.get(brief_field):
                self.error(f"{document}.{field}", f"must match brief.{brief_field}")

    def object_list(self, document: dict[str, Any], field: str, location: str) -> list[dict[str, Any]]:
        value = document.get(field)
        if not isinstance(value, list):
            self.error(location, "must be an array")
            return []
        result: list[dict[str, Any]] = []
        for index, item in enumerate(value):
            if not isinstance(item, dict):
                self.error(f"{location}[{index}]", "must be an object")
            else:
                result.append(item)
        return result

    def unique_ids(self, items: list[dict[str, Any]], location: str) -> set[str]:
        result: set[str] = set()
        for index, item in enumerate(items):
            item_id = item.get("id")
            item_location = f"{location}[{index}].id"
            if not isinstance(item_id, str) or not ID_PATTERN.fullmatch(item_id):
                self.error(item_location, "must be a lowercase hyphenated ID")
                continue
            if item_id in result:
                self.error(item_location, f"duplicate ID {item_id!r}")
            result.add(item_id)
        return result

    def validate_manifest(self) -> None:
        manifest = self.docs["manifest"]
        sources = self.object_list(manifest, "sources", "manifest.sources")
        claims = self.object_list(manifest, "claims", "manifest.claims")
        assets = self.object_list(manifest, "assets", "manifest.assets")
        adapters = self.object_list(manifest, "provider_plan", "manifest.provider_plan")
        self.source_ids = self.unique_ids(sources, "manifest.sources")
        self.claim_ids = self.unique_ids(claims, "manifest.claims")
        self.asset_ids = self.unique_ids(assets, "manifest.assets")
        self.adapter_ids = self.unique_ids(adapters, "manifest.provider_plan")
        self.validate_sources(sources)
        self.validate_claims(claims)
        self.validate_claim_audit(manifest.get("claim_audit"))
        self.validate_assets(assets)
        if not isinstance(manifest.get("asset_inventory_complete"), bool):
            self.error("manifest.asset_inventory_complete", "must be a boolean")
        if manifest.get("original_assets_only") is not True:
            self.error(
                "manifest.original_assets_only",
                "must be true; do not reuse assets from the analyzed channel",
            )
        self.validate_adapters(adapters)
        self.validate_hyperframes_motion_proof(adapters)
        self.validate_voice(manifest.get("voice"))
        self.validate_motion_quality(manifest.get("motion_quality"))
        self.validate_budget(manifest.get("budget"))
        self.validate_permissions(manifest.get("permissions"))
        self.validate_checkpoints(manifest.get("checkpoints"))
        self.validate_publish(manifest.get("publish"))
        self.validate_secret_fields(manifest)

    def validate_hyperframes_motion_proof(self, adapters: list[dict[str, Any]]) -> None:
        if self.stage not in {"rough", "final"}:
            return
        uses_hyperframes = any(
            adapter.get("adapter_name") == "hyperframes" and adapter.get("status") == "executed"
            for adapter in adapters
        )
        if not uses_hyperframes:
            return
        location = "hyperframes/world-motion-proof.json"
        path = self.root / location
        if not path.is_file():
            self.error(location, "is required for an executed HyperFrames render")
            return
        try:
            proof = read_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            self.error(location, f"must be readable JSON: {exc}")
            return
        if not isinstance(proof, dict):
            self.error(location, "must contain an object")
            return
        if proof.get("visual_grammar") != "world_motion_explainer":
            self.error(f"{location}.visual_grammar", "must be world_motion_explainer")
        if proof.get("presentation_allowed") is not False:
            self.error(f"{location}.presentation_allowed", "must be false")
        entries = proof.get("shots")
        if not isinstance(entries, list):
            self.error(f"{location}.shots", "must be an array")
            return
        storyboard_shot_ids = {
            shot.get("id") for shot in self.docs["storyboard"].get("shots", [])
            if isinstance(shot, dict) and isinstance(shot.get("id"), str)
        }
        proof_shot_ids: set[str] = set()
        for index, entry in enumerate(entries):
            prefix = f"{location}.shots[{index}]"
            if not isinstance(entry, dict):
                self.error(prefix, "must be an object")
                continue
            shot_id = entry.get("shot_id")
            self.nonempty_string(shot_id, f"{prefix}.shot_id")
            if isinstance(shot_id, str) and shot_id in proof_shot_ids:
                self.error(f"{prefix}.shot_id", "must be unique")
            if isinstance(shot_id, str):
                proof_shot_ids.add(shot_id)
            self.nonempty_string(entry.get("composition_id"), f"{prefix}.composition_id")
            for field, minimum in (("environment_layers", 2), ("subject_layers", 1), ("proof_times_seconds", 2)):
                values = entry.get(field)
                if not isinstance(values, list) or len(values) < minimum:
                    self.error(f"{prefix}.{field}", f"must contain at least {minimum} item(s)")
                    continue
                if field == "proof_times_seconds":
                    if any(not is_number(value) or value < 0 for value in values):
                        self.error(f"{prefix}.{field}", "must contain non-negative numbers")
                elif any(not isinstance(value, str) or not value.strip() for value in values):
                    self.error(f"{prefix}.{field}", "must contain non-empty strings")
            interaction = entry.get("interaction")
            if not isinstance(interaction, dict):
                self.error(f"{prefix}.interaction", "must be an object")
            else:
                for field in ("actor", "target", "event"):
                    self.nonempty_string(interaction.get(field), f"{prefix}.interaction.{field}")
        missing = sorted(storyboard_shot_ids - proof_shot_ids)
        extra = sorted(proof_shot_ids - storyboard_shot_ids)
        if missing:
            self.error(f"{location}.shots", f"missing storyboard shot IDs: {', '.join(missing)}")
        if extra:
            self.error(f"{location}.shots", f"contains unknown storyboard shot IDs: {', '.join(extra)}")

    def validate_sources(self, sources: list[dict[str, Any]]) -> None:
        allowed_types = {"official_primary", "primary", "secondary", "user_provided"}
        for index, source in enumerate(sources):
            prefix = f"manifest.sources[{index}]"
            for field in ("title", "locator", "publisher", "accessed_at"):
                self.nonempty_string(source.get(field), f"{prefix}.{field}")
            if source.get("source_type") not in allowed_types:
                self.error(f"{prefix}.source_type", f"must be one of {', '.join(sorted(allowed_types))}")
            if "published_at" not in source or not isinstance(source.get("published_at"), str):
                self.error(f"{prefix}.published_at", "must be a string; use an empty string when unknown")

    def validate_claims(self, claims: list[dict[str, Any]]) -> None:
        allowed_status = {"verified", "unverified", "disputed"}
        for index, claim in enumerate(claims):
            prefix = f"manifest.claims[{index}]"
            self.nonempty_string(claim.get("text"), f"{prefix}.text")
            source_ids = claim.get("source_ids")
            if not isinstance(source_ids, list) or not source_ids:
                self.error(f"{prefix}.source_ids", "must contain at least one source ID")
            else:
                for source_id in source_ids:
                    if source_id not in self.source_ids:
                        self.error(f"{prefix}.source_ids", f"unknown source ID {source_id!r}")
            if claim.get("verification_status") not in allowed_status:
                self.error(f"{prefix}.verification_status", "must be verified, unverified, or disputed")
            if "notes" not in claim or not isinstance(claim.get("notes"), str):
                self.error(f"{prefix}.notes", "must be a string")
            evidence = claim.get("evidence")
            if not isinstance(evidence, list) or not evidence:
                self.error(f"{prefix}.evidence", "must contain source-specific support evidence")
            else:
                claim_source_ids = source_ids if isinstance(source_ids, list) else []
                for evidence_index, item in enumerate(evidence):
                    item_prefix = f"{prefix}.evidence[{evidence_index}]"
                    if not isinstance(item, dict):
                        self.error(item_prefix, "must be an object")
                        continue
                    if item.get("source_id") not in claim_source_ids:
                        self.error(f"{item_prefix}.source_id", "must reference one of the claim's source IDs")
                    for field in ("support_locator", "support_summary", "checked_at"):
                        self.nonempty_string(item.get(field), f"{item_prefix}.{field}")

    def validate_claim_audit(self, audit: Any) -> None:
        if not isinstance(audit, dict):
            self.error("manifest.claim_audit", "must be an object")
            return
        if audit.get("status") not in {"pending", "manual_reviewed", "rejected"}:
            self.error("manifest.claim_audit.status", "must be pending, manual_reviewed, or rejected")
        for field in ("reviewed_by", "reviewed_at", "methodology", "limitations"):
            if field not in audit or not isinstance(audit.get(field), str):
                self.error(f"manifest.claim_audit.{field}", "must be a string")
        if audit.get("status") == "manual_reviewed":
            for field in ("reviewed_by", "reviewed_at", "methodology", "limitations"):
                self.nonempty_string(audit.get(field), f"manifest.claim_audit.{field}")

    def safe_local_path(self, value: Any, location: str, require_file: bool) -> Path | None:
        if not isinstance(value, str) or not value.strip():
            self.error(location, "must be a non-empty workspace-relative path")
            return None
        candidate_text = value.replace("\\", "/")
        candidate = Path(candidate_text)
        if candidate.is_absolute():
            self.error(location, "must be relative to the workspace")
            return None
        resolved = (self.root / candidate).resolve()
        try:
            resolved.relative_to(self.root)
        except ValueError:
            self.error(location, "must not escape the workspace")
            return None
        if require_file and not resolved.is_file():
            self.error(location, f"ready asset file does not exist: {value}")
        return resolved

    def validate_assets(self, assets: list[dict[str, Any]]) -> None:
        allowed_types = {"image", "video", "voice", "music", "sfx", "font", "render", "other"}
        allowed_status = {"planned", "ready", "rejected"}
        allowed_origins = {"generated", "licensed", "public_domain", "user_owned", "rendered"}
        adapter_refs: list[tuple[str, str]] = []
        asset_refs: list[tuple[str, str]] = []
        for index, asset in enumerate(assets):
            prefix = f"manifest.assets[{index}]"
            if asset.get("type") not in allowed_types:
                self.error(f"{prefix}.type", f"must be one of {', '.join(sorted(allowed_types))}")
            self.nonempty_string(asset.get("role"), f"{prefix}.role")
            status = asset.get("status")
            if status not in allowed_status:
                self.error(f"{prefix}.status", "must be planned, ready, or rejected")
            local_path = asset.get("local_path")
            resolved: Path | None = None
            if status == "ready":
                resolved = self.safe_local_path(local_path, f"{prefix}.local_path", True)
                digest = asset.get("sha256")
                if not isinstance(digest, str) or not HASH_PATTERN.fullmatch(digest):
                    self.error(f"{prefix}.sha256", "must be a lowercase SHA-256 for a ready asset")
                elif resolved and resolved.is_file():
                    actual = sha256_file(resolved)
                    if actual != digest:
                        self.error(f"{prefix}.sha256", "does not match the ready asset file")
            else:
                if local_path:
                    self.safe_local_path(local_path, f"{prefix}.local_path", False)
                if "sha256" not in asset or not isinstance(asset.get("sha256"), str):
                    self.error(f"{prefix}.sha256", "must be a string")

            provenance = asset.get("provenance")
            if not isinstance(provenance, dict):
                self.error(f"{prefix}.provenance", "must be an object")
                continue
            origin = provenance.get("origin")
            if origin not in allowed_origins:
                self.error(f"{prefix}.provenance.origin", f"must be one of {', '.join(sorted(allowed_origins))}")
            for field in ("creator", "source_locator", "retrieved_at"):
                if status == "ready":
                    self.nonempty_string(provenance.get(field), f"{prefix}.provenance.{field}")
                elif field not in provenance or not isinstance(provenance.get(field), str):
                    self.error(f"{prefix}.provenance.{field}", "must be a string")

            license_data = provenance.get("license")
            if not isinstance(license_data, dict):
                self.error(f"{prefix}.provenance.license", "must be an object")
            else:
                for field in ("name", "terms_locator", "checked_at"):
                    if status == "ready":
                        self.nonempty_string(license_data.get(field), f"{prefix}.provenance.license.{field}")
                    elif field not in license_data or not isinstance(license_data.get(field), str):
                        self.error(f"{prefix}.provenance.license.{field}", "must be a string")
                if not isinstance(license_data.get("commercial_use_allowed"), (bool, type(None))):
                    self.error(
                        f"{prefix}.provenance.license.commercial_use_allowed",
                        "must be true, false, or null while planned",
                    )
                if status == "ready" and license_data.get("commercial_use_allowed") is not True:
                    self.error(
                        f"{prefix}.provenance.license.commercial_use_allowed",
                        "must be true for a ready production asset",
                    )

            if "generation" not in provenance:
                self.error(f"{prefix}.provenance.generation", "must be present; use null for source assets")
                continue
            generation = provenance.get("generation")
            if origin in {"generated", "rendered"} and status == "ready":
                if not isinstance(generation, dict):
                    self.error(f"{prefix}.provenance.generation", "must be an object for generated/rendered assets")
                    continue
                for field in ("adapter_id", "provider", "model", "prompt", "generated_at"):
                    if self.nonempty_string(generation.get(field), f"{prefix}.provenance.generation.{field}"):
                        if field == "adapter_id":
                            adapter_refs.append((generation[field], f"{prefix}.provenance.generation.adapter_id"))
                reference_ids = generation.get("reference_asset_ids")
                if not isinstance(reference_ids, list):
                    self.error(f"{prefix}.provenance.generation.reference_asset_ids", "must be an array")
                else:
                    asset_refs.extend(
                        (asset_id, f"{prefix}.provenance.generation.reference_asset_ids")
                        for asset_id in reference_ids
                    )
            elif generation is not None and not isinstance(generation, dict):
                self.error(f"{prefix}.provenance.generation", "must be an object or null")

        for adapter_id, location in adapter_refs:
            if adapter_id not in self.adapter_ids:
                self.error(location, f"unknown adapter ID {adapter_id!r}")
        adapter_map = {
            item.get("id"): item
            for item in self.docs["manifest"].get("provider_plan", [])
            if isinstance(item, dict)
        }
        for adapter_id, location in adapter_refs:
            if adapter_id in adapter_map and adapter_map[adapter_id].get("status") != "executed":
                self.error(location, "ready generated/rendered asset requires an executed adapter")
        for asset_id, location in asset_refs:
            if asset_id not in self.asset_ids:
                self.error(location, f"unknown reference asset ID {asset_id!r}")

    def validate_adapters(self, adapters: list[dict[str, Any]]) -> None:
        manifest = self.docs["manifest"]
        permissions = manifest.get("permissions") if isinstance(manifest.get("permissions"), dict) else {}
        checkpoints = manifest.get("checkpoints") if isinstance(manifest.get("checkpoints"), dict) else {}
        allowed_capabilities = {
            "image_generation",
            "video_generation",
            "tts",
            "music_generation",
            "sfx_generation",
            "caption_generation",
            "render",
        }
        executed_paid_total = sum(
            float(item.get("estimated_cost", 0))
            for item in adapters
            if item.get("status") == "executed"
            and item.get("requires_paid_call") is True
            and is_number(item.get("estimated_cost"))
        )
        for index, adapter in enumerate(adapters):
            prefix = f"manifest.provider_plan[{index}]"
            capability = adapter.get("capability")
            if capability not in allowed_capabilities:
                self.error(
                    f"{prefix}.capability",
                    "must be an approved production capability; publishing/upload/scheduling is prohibited",
                )
            if adapter.get("adapter_kind") not in {"tool", "local_command", "external_api"}:
                self.error(f"{prefix}.adapter_kind", "must be tool, local_command, or external_api")
            self.nonempty_string(adapter.get("adapter_name"), f"{prefix}.adapter_name")
            if adapter.get("status") not in {"planned", "approved", "executed", "blocked"}:
                self.error(f"{prefix}.status", "must be planned, approved, executed, or blocked")
            for field in ("requires_external_api", "requires_paid_call"):
                if not isinstance(adapter.get(field), bool):
                    self.error(f"{prefix}.{field}", "must be a boolean")
            env_vars = adapter.get("env_vars")
            if not isinstance(env_vars, list):
                self.error(f"{prefix}.env_vars", "must be an array of environment-variable names")
            else:
                for env_var in env_vars:
                    if not isinstance(env_var, str) or not ENV_PATTERN.fullmatch(env_var):
                        self.error(f"{prefix}.env_vars", f"invalid environment-variable name {env_var!r}")
            for forbidden in ("endpoint", "base_url", "api_key", "token", "secret", "password"):
                if adapter.get(forbidden):
                    self.error(f"{prefix}.{forbidden}", "must not store endpoint or credential values")
            if not is_number(adapter.get("estimated_units")) or adapter.get("estimated_units", -1) < 0:
                self.error(f"{prefix}.estimated_units", "must be a non-negative number")
            if not is_number(adapter.get("estimated_cost")) or adapter.get("estimated_cost", -1) < 0:
                self.error(f"{prefix}.estimated_cost", "must be a non-negative number")
            self.nonempty_string(adapter.get("currency"), f"{prefix}.currency")
            if "model" not in adapter or not isinstance(adapter.get("model"), str):
                self.error(f"{prefix}.model", "must be a string; leave empty only when not applicable")
            if adapter.get("status") == "executed":
                adapter_id = adapter.get("id")
                if adapter.get("requires_external_api") and not self.permission_allows(
                    permissions, "external_api_calls", adapter_id
                ):
                    self.error(prefix, "executed external API call lacks approval scoped to this adapter ID")
                if adapter.get("requires_paid_call"):
                    if not self.permission_allows(permissions, "paid_calls", adapter_id):
                        self.error(prefix, "executed paid call lacks approval scoped to this adapter ID")
                    paid_approval = permissions.get("paid_calls") if isinstance(permissions, dict) else None
                    approved_limit = paid_approval.get("limit") if isinstance(paid_approval, dict) else None
                    if not is_number(approved_limit) or approved_limit < executed_paid_total:
                        self.error(
                            "manifest.permissions.paid_calls.limit",
                            "must cover the cumulative estimated cost of executed paid adapters",
                        )
                budget_gate = checkpoints.get("budget") if isinstance(checkpoints, dict) else None
                if not isinstance(budget_gate, dict) or budget_gate.get("status") != "approved":
                    self.error(prefix, "executed provider call lacks approved budget checkpoint")

    def permission_allows(self, permissions: Any, name: str, adapter_id: Any) -> bool:
        if not isinstance(permissions, dict) or not isinstance(permissions.get(name), dict):
            return False
        permission = permissions[name]
        if permission.get("approved") is not True or not isinstance(adapter_id, str):
            return False
        scope = permission.get("scope")
        if not isinstance(scope, str):
            return False
        allowed_adapter_ids = {item.strip() for item in scope.split(",") if item.strip()}
        return adapter_id in allowed_adapter_ids

    def validate_voice(self, voice: Any) -> None:
        if not isinstance(voice, dict):
            self.error("manifest.voice", "must be an object")
            return
        mode = voice.get("mode")
        if mode not in {"tts_synthetic", "original_recording", "none"}:
            self.error("manifest.voice.mode", "must be tts_synthetic, original_recording, or none")
        if voice.get("real_person_clone") is not False:
            self.error("manifest.voice.real_person_clone", "must be false; real-person voice cloning is prohibited")
        for field in ("provider", "voice_id"):
            if field not in voice or not isinstance(voice.get(field), str):
                self.error(f"manifest.voice.{field}", "must be a string")
        consent = voice.get("consent")
        if not isinstance(consent, dict):
            self.error("manifest.voice.consent", "must be an object")
            return
        if not isinstance(consent.get("confirmed"), bool):
            self.error("manifest.voice.consent.confirmed", "must be a boolean")
        for field in ("evidence_locator", "confirmed_at"):
            if field not in consent or not isinstance(consent.get(field), str):
                self.error(f"manifest.voice.consent.{field}", "must be a string")
        if mode == "original_recording" and self.stage in {"rough", "final"}:
            if consent.get("confirmed") is not True:
                self.error("manifest.voice.consent.confirmed", "must be true for an original recording")
            self.nonempty_string(consent.get("evidence_locator"), "manifest.voice.consent.evidence_locator")
            self.nonempty_string(consent.get("confirmed_at"), "manifest.voice.consent.confirmed_at")
        if mode == "tts_synthetic" and self.stage in {"rough", "final"}:
            self.nonempty_string(voice.get("provider"), "manifest.voice.provider")
            self.nonempty_string(voice.get("voice_id"), "manifest.voice.voice_id")
            evidence = voice.get("synthetic_voice_evidence")
            if not isinstance(evidence, dict):
                self.error("manifest.voice.synthetic_voice_evidence", "must be an object")
            else:
                if evidence.get("verified") is not True:
                    self.error(
                        "manifest.voice.synthetic_voice_evidence.verified",
                        "must be true after checking that the voice is synthetic and independently licensed",
                    )
                for field in ("terms_locator", "checked_at", "notes"):
                    self.nonempty_string(evidence.get(field), f"manifest.voice.synthetic_voice_evidence.{field}")
        elif "synthetic_voice_evidence" not in voice or not isinstance(voice.get("synthetic_voice_evidence"), dict):
            self.error("manifest.voice.synthetic_voice_evidence", "must be an object")

    def validate_motion_quality(self, motion: Any) -> None:
        location = "manifest.motion_quality"
        if not isinstance(motion, dict):
            self.error(location, "must be an object")
            return
        if motion.get("status") not in {"pending", "passed", "failed"}:
            self.error(f"{location}.status", "must be pending, passed, or failed")
        for field in (
            "analysis_method",
            "automated_report_path",
            "automated_report_sha256",
            "manual_reviewed_by",
            "manual_reviewed_at",
        ):
            if field not in motion or not isinstance(motion.get(field), str):
                self.error(f"{location}.{field}", "must be a string")
        for field in (
            "sample_rate_fps",
            "meaningful_motion_screen_time_ratio",
            "distributed_motion_screen_time_ratio",
            "independent_layer_motion_shot_ratio",
            "interaction_shot_ratio",
            "camera_only_screen_time_ratio",
        ):
            value = motion.get(field)
            if not is_number(value) or value < 0:
                self.error(f"{location}.{field}", "must be a non-negative number")
        for field in (
            "meaningful_motion_screen_time_ratio",
            "distributed_motion_screen_time_ratio",
            "independent_layer_motion_shot_ratio",
            "interaction_shot_ratio",
            "camera_only_screen_time_ratio",
        ):
            value = motion.get(field)
            if is_number(value) and value > 1:
                self.error(f"{location}.{field}", "must not exceed 1.0")
        static_hold = motion.get("max_static_hold_seconds")
        if static_hold is not None and (not is_number(static_hold) or static_hold < 0):
            self.error(f"{location}.max_static_hold_seconds", "must be null or a non-negative number")
        if not isinstance(motion.get("notes"), list) or any(
            not isinstance(item, str) or not item.strip() for item in motion.get("notes", [])
        ):
            self.error(f"{location}.notes", "must be an array of non-empty strings")

        if self.stage not in {"rough", "final"}:
            return
        if motion.get("status") != "passed":
            self.error(f"{location}.status", "must be passed after automated and manual motion review")
        self.nonempty_string(motion.get("analysis_method"), f"{location}.analysis_method")
        if not is_number(motion.get("sample_rate_fps")) or motion.get("sample_rate_fps", 0) <= 0:
            self.error(f"{location}.sample_rate_fps", "must be positive after motion analysis")
        thresholds = {
            "meaningful_motion_screen_time_ratio": (0.65, "at least"),
            "distributed_motion_screen_time_ratio": (0.50, "at least"),
            "independent_layer_motion_shot_ratio": (0.80, "at least"),
            "interaction_shot_ratio": (0.60, "at least"),
        }
        for field, (minimum, wording) in thresholds.items():
            value = motion.get(field)
            if not is_number(value) or value < minimum:
                self.error(f"{location}.{field}", f"must be {wording} {minimum:.2f}")
        camera_only = motion.get("camera_only_screen_time_ratio")
        if not is_number(camera_only) or camera_only > 0.15:
            self.error(f"{location}.camera_only_screen_time_ratio", "must be at most 0.15")
        if not is_number(static_hold) or static_hold > 2.0:
            self.error(f"{location}.max_static_hold_seconds", "must be at most 2.0 seconds")
        report = self.safe_local_path(
            motion.get("automated_report_path"), f"{location}.automated_report_path", True
        )
        digest = motion.get("automated_report_sha256")
        if not isinstance(digest, str) or not HASH_PATTERN.fullmatch(digest):
            self.error(f"{location}.automated_report_sha256", "must be a lowercase SHA-256")
        elif report and report.is_file() and sha256_file(report) != digest:
            self.error(f"{location}.automated_report_sha256", "does not match the motion report")
        self.nonempty_string(motion.get("manual_reviewed_by"), f"{location}.manual_reviewed_by")
        self.nonempty_string(motion.get("manual_reviewed_at"), f"{location}.manual_reviewed_at")

    def validate_budget(self, budget: Any) -> None:
        if not isinstance(budget, dict):
            self.error("manifest.budget", "must be an object")
            return
        self.nonempty_string(budget.get("currency"), "manifest.budget.currency")
        if budget.get("estimate_status") not in {"not_estimated", "estimated", "approved"}:
            self.error("manifest.budget.estimate_status", "must be not_estimated, estimated, or approved")
        for field in ("estimated_total", "contingency_percent"):
            if not is_number(budget.get(field)) or budget.get(field, -1) < 0:
                self.error(f"manifest.budget.{field}", "must be a non-negative number")
        if not isinstance(budget.get("line_items"), list):
            self.error("manifest.budget.line_items", "must be an array")
        if not isinstance(budget.get("assumptions"), list):
            self.error("manifest.budget.assumptions", "must be an array")

    def validate_permissions(self, permissions: Any) -> None:
        if not isinstance(permissions, dict):
            self.error("manifest.permissions", "must be an object")
            return
        for name in ("paid_calls", "external_api_calls", "publishing"):
            item = permissions.get(name)
            prefix = f"manifest.permissions.{name}"
            if not isinstance(item, dict):
                self.error(prefix, "must be an object")
                continue
            if not isinstance(item.get("approved"), bool):
                self.error(f"{prefix}.approved", "must be a boolean")
            for field in ("approved_by", "approved_at", "scope"):
                if field not in item or not isinstance(item.get(field), str):
                    self.error(f"{prefix}.{field}", "must be a string")
            if item.get("approved") is True:
                for field in ("approved_by", "approved_at", "scope"):
                    self.nonempty_string(item.get(field), f"{prefix}.{field}")

    def validate_checkpoints(self, checkpoints: Any) -> None:
        if not isinstance(checkpoints, dict):
            self.error("manifest.checkpoints", "must be an object")
            return
        prior_approved = True
        for name in CHECKPOINTS:
            checkpoint = checkpoints.get(name)
            prefix = f"manifest.checkpoints.{name}"
            if not isinstance(checkpoint, dict):
                self.error(prefix, "must be an object")
                prior_approved = False
                continue
            if checkpoint.get("status") not in {"pending", "approved", "rejected"}:
                self.error(f"{prefix}.status", "must be pending, approved, or rejected")
            for field in ("approved_by", "approved_at", "notes"):
                if field not in checkpoint or not isinstance(checkpoint.get(field), str):
                    self.error(f"{prefix}.{field}", "must be a string")
            if checkpoint.get("status") == "approved":
                self.nonempty_string(checkpoint.get("approved_by"), f"{prefix}.approved_by")
                self.nonempty_string(checkpoint.get("approved_at"), f"{prefix}.approved_at")
                if not prior_approved:
                    self.error(prefix, "cannot be approved before all earlier checkpoints")
            else:
                prior_approved = False

    def validate_publish(self, publish: Any) -> None:
        if not isinstance(publish, dict):
            self.error("manifest.publish", "must be an object")
            return
        if publish.get("automatic") is not False:
            self.error("manifest.publish.automatic", "must remain false")
        if publish.get("status") not in {"not_requested", "blocked", "manual_handoff"}:
            self.error("manifest.publish.status", "must be not_requested, blocked, or manual_handoff")

    def validate_secret_fields(self, value: Any, location: str = "manifest") -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                lowered = key.lower()
                if lowered in {"api_key", "access_token", "refresh_token", "password", "secret"} and child:
                    self.error(f"{location}.{key}", "credential values must not be stored")
                self.validate_secret_fields(child, f"{location}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                self.validate_secret_fields(child, f"{location}[{index}]")

    def collect_references(self, value: Any, location: str, known: set[str], used: set[str]) -> None:
        if not isinstance(value, list):
            self.error(location, "must be an array")
            return
        for item in value:
            if not isinstance(item, str) or item not in known:
                self.error(location, f"unknown ID {item!r}")
            else:
                used.add(item)

    def validate_concept(self) -> None:
        concept = self.docs["concept"]
        if concept.get("status") not in STATUS_VALUES:
            self.error("concept.status", f"must be one of {', '.join(sorted(STATUS_VALUES))}")
        for field in ("audience", "premise", "viewer_promise", "angle", "selected_hook"):
            if field not in concept or not isinstance(concept.get(field), str):
                self.error(f"concept.{field}", "must be a string")
        for field in ("hook_options", "structure", "differentiation", "notes"):
            if not isinstance(concept.get(field), list):
                self.error(f"concept.{field}", "must be an array")
        self.collect_references(concept.get("claim_ids"), "concept.claim_ids", self.claim_ids, self.used_claim_ids)

    def validate_script(self) -> None:
        script = self.docs["script"]
        if script.get("status") not in STATUS_VALUES:
            self.error("script.status", f"must be one of {', '.join(sorted(STATUS_VALUES))}")
        if "title" not in script or not isinstance(script.get("title"), str):
            self.error("script.title", "must be a string")
        segments = self.object_list(script, "segments", "script.segments")
        segment_ids = self.unique_ids(segments, "script.segments")
        script["_validated_segment_ids"] = segment_ids
        previous_end = 0.0
        duration = self.docs["brief"].get("duration_seconds")
        for index, segment in enumerate(segments):
            prefix = f"script.segments[{index}]"
            start = segment.get("start_seconds")
            end = segment.get("end_seconds")
            if not is_number(start) or not is_number(end) or start < 0 or end <= start:
                self.error(prefix, "start/end must be non-negative numbers with end greater than start")
            else:
                if start < previous_end:
                    self.error(prefix, "segments must not overlap")
                previous_end = end
                if is_number(duration) and end > duration:
                    self.error(f"{prefix}.end_seconds", "must not exceed brief duration")
            content_type = segment.get("content_type")
            if content_type not in {"factual", "creative", "opinion"}:
                self.error(f"{prefix}.content_type", "must be factual, creative, or opinion")
            narration = segment.get("narration")
            onscreen = segment.get("on_screen_text")
            if not isinstance(narration, str) or not isinstance(onscreen, str) or not (narration.strip() or onscreen.strip()):
                self.error(prefix, "must contain narration or on-screen text")
            if "delivery_notes" not in segment or not isinstance(segment.get("delivery_notes"), str):
                self.error(f"{prefix}.delivery_notes", "must be a string")
            segment_claim_ids = segment.get("claim_ids")
            self.collect_references(segment_claim_ids, f"{prefix}.claim_ids", self.claim_ids, self.used_claim_ids)
            if content_type == "factual" and (not isinstance(segment_claim_ids, list) or not segment_claim_ids):
                self.error(f"{prefix}.claim_ids", "factual segment must reference at least one claim")

    def validate_storyboard(self) -> None:
        storyboard = self.docs["storyboard"]
        if storyboard.get("status") not in STATUS_VALUES:
            self.error("storyboard.status", f"must be one of {', '.join(sorted(STATUS_VALUES))}")
        shots = self.object_list(storyboard, "shots", "storyboard.shots")
        self.unique_ids(shots, "storyboard.shots")
        segment_ids = self.docs["script"].get("_validated_segment_ids", set())
        previous_end = 0.0
        duration = self.docs["brief"].get("duration_seconds")
        mode = self.docs["brief"].get("mode")
        enforce_world_contract = self.stage in {"script", "rough", "final"}
        world_subject_ids: set[str] = set()
        if enforce_world_contract:
            if storyboard.get("visual_grammar") != "world_motion_explainer":
                self.error("storyboard.visual_grammar", "must be world_motion_explainer for a faceless production")
            if storyboard.get("presentation_allowed") is not False:
                self.error("storyboard.presentation_allowed", "must be false; presentation grammar is not a faceless motion-explainer")
            world = storyboard.get("world")
            if not isinstance(world, dict):
                self.error("storyboard.world", "must be an object")
            else:
                self.nonempty_string(world.get("setting"), "storyboard.world.setting")
                for field, minimum in (("visual_vocabulary", 3), ("continuity_anchors", 1)):
                    values = world.get(field)
                    if not isinstance(values, list) or len(values) < minimum or any(not isinstance(item, str) or not item.strip() for item in values):
                        self.error(f"storyboard.world.{field}", f"must contain at least {minimum} non-empty string(s)")
                subjects = self.object_list(world, "subjects", "storyboard.world.subjects")
                for subject_index, subject in enumerate(subjects):
                    subject_prefix = f"storyboard.world.subjects[{subject_index}]"
                    subject_id = subject.get("id")
                    self.nonempty_string(subject_id, f"{subject_prefix}.id")
                    self.nonempty_string(subject.get("role"), f"{subject_prefix}.role")
                    self.nonempty_string(subject.get("description"), f"{subject_prefix}.description")
                    if isinstance(subject_id, str) and subject_id.strip():
                        if subject_id in world_subject_ids:
                            self.error(f"{subject_prefix}.id", "must be unique")
                        world_subject_ids.add(subject_id)
                if not subjects:
                    self.error("storyboard.world.subjects", "must contain at least one context-specific subject")
        for index, shot in enumerate(shots):
            prefix = f"storyboard.shots[{index}]"
            start = shot.get("start_seconds")
            end = shot.get("end_seconds")
            if not is_number(start) or not is_number(end) or start < 0 or end <= start:
                self.error(prefix, "start/end must be non-negative numbers with end greater than start")
            else:
                if start < previous_end:
                    self.error(prefix, "shots must not overlap")
                previous_end = end
                if is_number(duration) and end > duration:
                    self.error(f"{prefix}.end_seconds", "must not exceed brief duration")
            media_type = shot.get("media_type")
            allowed_media = {"image", "graphic", "text"} if mode == "image_only" else {"image", "graphic", "text", "video"}
            if media_type not in allowed_media:
                self.error(f"{prefix}.media_type", f"must be one of {', '.join(sorted(allowed_media))}")
            for field in ("visual_description", "motion", "transition", "generation_prompt", "negative_prompt"):
                if field not in shot or not isinstance(shot.get(field), str):
                    self.error(f"{prefix}.{field}", "must be a string")
            if enforce_world_contract:
                for field in ("setting", "action", "interaction_target", "continuity_anchor"):
                    self.nonempty_string(shot.get(field), f"{prefix}.{field}")
                shot_subject_ids = shot.get("world_subject_ids")
                if not isinstance(shot_subject_ids, list) or not shot_subject_ids or any(not isinstance(item, str) or not item.strip() for item in shot_subject_ids):
                    self.error(f"{prefix}.world_subject_ids", "must contain at least one world subject ID")
                elif not world_subject_ids:
                    self.error(f"{prefix}.world_subject_ids", "cannot be validated because storyboard.world.subjects is invalid")
                else:
                    for subject_id in shot_subject_ids:
                        if subject_id not in world_subject_ids:
                            self.error(f"{prefix}.world_subject_ids", f"unknown world subject ID {subject_id!r}")
            motion_design = shot.get("motion_design")
            motion_prefix = f"{prefix}.motion_design"
            if not isinstance(motion_design, dict):
                self.error(motion_prefix, "must be an object")
            else:
                implementations = {
                    "layered_2d",
                    "vector_animation",
                    "rigged_character",
                    "generated_video",
                    "composited_particles",
                    "hybrid",
                }
                if motion_design.get("implementation") not in implementations:
                    self.error(
                        f"{motion_prefix}.implementation",
                        f"must be one of {', '.join(sorted(implementations))}",
                    )
                for field in ("camera_motion", "subject_motion", "interaction_event", "loop_strategy"):
                    self.nonempty_string(motion_design.get(field), f"{motion_prefix}.{field}")
                for field, minimum in (("environment_motion", 2), ("animated_layers", 2), ("timing_beats", 1)):
                    values = motion_design.get(field)
                    if (
                        not isinstance(values, list)
                        or len(values) < minimum
                        or any(not isinstance(item, str) or not item.strip() for item in values)
                    ):
                        self.error(
                            f"{motion_prefix}.{field}",
                            f"must contain at least {minimum} non-empty string(s)",
                        )
                    elif field == "animated_layers" and len(set(values)) != len(values):
                        self.error(f"{motion_prefix}.{field}", "must identify distinct layers")
                if motion_design.get("camera_only") is not False:
                    self.error(
                        f"{motion_prefix}.camera_only",
                        "must be false; camera motion over one flattened still is not sufficient",
                    )
            self.collect_references(shot.get("segment_ids"), f"{prefix}.segment_ids", segment_ids, set())
            shot_asset_ids = shot.get("asset_ids")
            self.collect_references(shot_asset_ids, f"{prefix}.asset_ids", self.asset_ids, self.used_asset_ids)
            if self.stage in {"rough", "final"} and (not isinstance(shot_asset_ids, list) or not shot_asset_ids):
                self.error(f"{prefix}.asset_ids", "must contain at least one production asset")
            self.collect_references(shot.get("claim_ids"), f"{prefix}.claim_ids", self.claim_ids, self.used_claim_ids)

    def validate_cross_references(self) -> None:
        claims = self.docs["manifest"].get("claims", [])
        claim_map = {claim.get("id"): claim for claim in claims if isinstance(claim, dict)}
        if self.stage in {"script", "rough", "final"}:
            for claim_id in sorted(self.used_claim_ids):
                claim = claim_map.get(claim_id)
                if isinstance(claim, dict) and claim.get("verification_status") != "verified":
                    self.error(f"manifest.claims[{claim_id}]", "referenced claim must be verified before script approval")
            if self.used_claim_ids:
                audit = self.docs["manifest"].get("claim_audit")
                if not isinstance(audit, dict) or audit.get("status") != "manual_reviewed":
                    self.error(
                        "manifest.claim_audit.status",
                        "must be manual_reviewed; structural validation cannot prove semantic source relevance",
                    )

    def checkpoint_is_approved(self, name: str) -> bool:
        checkpoints = self.docs["manifest"].get("checkpoints")
        return (
            isinstance(checkpoints, dict)
            and isinstance(checkpoints.get(name), dict)
            and checkpoints[name].get("status") == "approved"
        )

    def require_checkpoint(self, name: str) -> None:
        if not self.checkpoint_is_approved(name):
            self.error(f"manifest.checkpoints.{name}", "must be approved for this validation stage")

    def require_ready_render(self, name: str) -> None:
        renders = self.docs["manifest"].get("renders")
        prefix = f"manifest.renders.{name}"
        if not isinstance(renders, dict) or not isinstance(renders.get(name), dict):
            self.error(prefix, "must be an object")
            return
        render = renders[name]
        if render.get("status") != "ready":
            self.error(f"{prefix}.status", "must be ready")
        asset_id = render.get("asset_id")
        if asset_id not in self.asset_ids:
            self.error(f"{prefix}.asset_id", "must reference a manifest asset")
            return
        asset_map = {
            item.get("id"): item
            for item in self.docs["manifest"].get("assets", [])
            if isinstance(item, dict)
        }
        if asset_map.get(asset_id, {}).get("status") != "ready":
            self.error(f"{prefix}.asset_id", "must reference a ready asset")

    def validate_stage(self) -> None:
        stage_rank = STAGES.index(self.stage)
        concept = self.docs["concept"]
        script = self.docs["script"]
        storyboard = self.docs["storyboard"]
        manifest = self.docs["manifest"]

        if stage_rank >= STAGES.index("concept"):
            if concept.get("status") != "approved":
                self.error("concept.status", "must be approved")
            for field in ("audience", "premise", "viewer_promise", "angle", "selected_hook"):
                self.nonempty_string(concept.get(field), f"concept.{field}")
            for field in ("hook_options", "structure", "differentiation"):
                if not isinstance(concept.get(field), list) or not concept.get(field):
                    self.error(f"concept.{field}", "must contain at least one item")
            self.require_checkpoint("concept")

        if stage_rank >= STAGES.index("script"):
            if script.get("status") != "approved":
                self.error("script.status", "must be approved")
            self.nonempty_string(script.get("title"), "script.title")
            if not isinstance(script.get("segments"), list) or not script.get("segments"):
                self.error("script.segments", "must contain at least one segment")
            if storyboard.get("status") != "approved":
                self.error("storyboard.status", "must be approved with the script")
            if not isinstance(storyboard.get("shots"), list) or not storyboard.get("shots"):
                self.error("storyboard.shots", "must contain at least one shot")
            self.require_checkpoint("script")

        if stage_rank >= STAGES.index("rough"):
            self.require_checkpoint("budget")
            if manifest.get("asset_inventory_complete") is not True:
                self.error("manifest.asset_inventory_complete", "must be true before rough-cut approval")
            budget = manifest.get("budget")
            if not isinstance(budget, dict) or budget.get("estimate_status") != "approved":
                self.error("manifest.budget.estimate_status", "must be approved before production")
            asset_map = {
                item.get("id"): item
                for item in manifest.get("assets", [])
                if isinstance(item, dict)
            }
            for asset_id in sorted(self.used_asset_ids):
                if asset_map.get(asset_id, {}).get("status") != "ready":
                    self.error(f"manifest.assets[{asset_id}]", "storyboard-referenced asset must be ready")
            narration_exists = any(
                isinstance(segment, dict) and isinstance(segment.get("narration"), str) and segment["narration"].strip()
                for segment in script.get("segments", [])
            )
            voice = manifest.get("voice")
            if narration_exists and isinstance(voice, dict) and voice.get("mode") == "none":
                self.error("manifest.voice.mode", "must identify narration production when script narration is present")
            if narration_exists and isinstance(voice, dict) and voice.get("mode") in {"tts_synthetic", "original_recording"}:
                ready_voice_assets = [
                    item
                    for item in manifest.get("assets", [])
                    if isinstance(item, dict) and item.get("type") == "voice" and item.get("status") == "ready"
                ]
                if not ready_voice_assets:
                    self.error("manifest.assets", "must include a ready voice asset for narrated output")
                expected_origin = "generated" if voice.get("mode") == "tts_synthetic" else "user_owned"
                adapter_map = {
                    item.get("id"): item
                    for item in manifest.get("provider_plan", [])
                    if isinstance(item, dict)
                }
                for item in ready_voice_assets:
                    provenance = item.get("provenance") if isinstance(item.get("provenance"), dict) else {}
                    if provenance.get("origin") != expected_origin:
                        self.error(
                            f"manifest.assets[{item.get('id')}].provenance.origin",
                            f"must be {expected_origin} for voice mode {voice.get('mode')}",
                        )
                    if voice.get("mode") == "tts_synthetic":
                        generation = provenance.get("generation") if isinstance(provenance.get("generation"), dict) else {}
                        adapter = adapter_map.get(generation.get("adapter_id"), {})
                        if adapter.get("capability") != "tts":
                            self.error(
                                f"manifest.assets[{item.get('id')}].provenance.generation.adapter_id",
                                "must reference an executed tts adapter",
                            )
            self.require_ready_render("rough")
            self.require_checkpoint("rough")

        if stage_rank >= STAGES.index("final"):
            self.require_ready_render("final")
            self.require_checkpoint("final")


def validate_workspace(args: argparse.Namespace) -> int:
    validator = WorkspaceValidator(Path(args.workspace).expanduser(), args.stage)
    errors = validator.validate()
    if errors:
        print(f"Validation failed for stage {args.stage} ({len(errors)} error(s)):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Validation passed for stage {args.stage}: {validator.root}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="create a new production workspace")
    init_parser.add_argument("--output", required=True, help="missing or empty output directory")
    init_parser.add_argument("--channel-profile", required=True, help="input channel-profile.json")
    init_parser.add_argument("--topic", required=True, help="original video topic")
    init_parser.add_argument("--duration-seconds", required=True, type=positive_duration)
    init_parser.add_argument("--language", required=True, help="language tag or name")
    init_parser.add_argument("--aspect-ratio", required=True, type=parse_aspect_ratio, help="W:H, e.g. 9:16")
    init_parser.add_argument("--mode", required=True, choices=MODES)
    init_parser.set_defaults(handler=init_workspace)

    validate_parser = subparsers.add_parser("validate", help="validate a production workspace")
    validate_parser.add_argument("--workspace", required=True)
    validate_parser.add_argument("--stage", choices=STAGES, default="structure")
    validate_parser.set_defaults(handler=validate_workspace)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "init":
        if not args.topic.strip():
            parser.error("--topic must not be empty")
        if not args.language.strip():
            parser.error("--language must not be empty")
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
