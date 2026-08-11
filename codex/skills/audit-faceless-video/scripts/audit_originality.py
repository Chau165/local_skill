#!/usr/bin/env python3
"""Read-only originality and rights-risk screen for faceless-video projects."""

from __future__ import annotations

import argparse
import datetime as dt
import difflib
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import unicodedata
from typing import Any, Iterable


POLICY_VERSION = "1.1"
SHINGLE_SIZE = 5
REVIEW_COVERAGE = 0.18
BLOCK_COVERAGE = 0.40
REPORT_PHRASE_WORDS = 12
REVIEW_PHRASE_WORDS = 18
BLOCK_PHRASE_WORDS = 40
MAX_PHRASES = 20
MAX_INPUT_BYTES = 10 * 1024 * 1024

EXIT_CODES = {"PASS": 0, "REVIEW": 1, "BLOCK": 2, "INCOMPLETE": 3}
STATUS_PRECEDENCE = ("BLOCK", "INCOMPLETE", "REVIEW", "PASS")

LEGAL_NOTICE = (
    "This automated audit is a risk screen, not a legal opinion or a determination "
    "of copyright infringement, license validity, consent, fair use, or permission "
    "to publish."
)

BLOCKED_RIGHTS = {
    "denied",
    "revoked",
    "prohibited",
    "unauthorized",
    "unlicensed",
    "commercial_use_denied",
}
REVIEW_RIGHTS = {
    "fair_use",
    "fair_use_claimed",
    "editorial_only",
    "restricted",
    "custom",
    "needs_review",
}
ALLOWED_RIGHTS = {
    "original",
    "owned",
    "licensed",
    "permission_granted",
    "public_domain",
    "cc0",
    "cc_by",
    "cc_by_sa",
    "royalty_free",
    "stock_license",
}
TEXT_KEYS = ("transcript", "script", "content", "text", "caption", "utterance")
CONTAINER_KEYS = ("captions", "segments", "utterances", "items", "entries", "results")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit script overlap, asset rights metadata, and voice consent without modifying inputs."
    )
    parser.add_argument("--candidate", required=True, help="Candidate script: UTF-8 text, Markdown, or JSON")
    parser.add_argument(
        "--reference",
        required=True,
        action="append",
        help="Reference transcript; repeat for multiple references",
    )
    parser.add_argument("--manifest", required=True, help="Production manifest JSON")
    parser.add_argument("--output", required=True, help="New audit-report JSON path")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace an existing audit report; input paths remain protected",
    )
    return parser.parse_args()


def normalize_enum(value: Any) -> str:
    if value is None:
        return ""
    text = unicodedata.normalize("NFKC", str(value)).casefold().strip()
    return re.sub(r"[^a-z0-9]+", "_", text).strip("_")


def tokenize(text: str) -> list[str]:
    normalized = unicodedata.normalize("NFKC", text).casefold()
    return re.findall(r"[^\W_]+(?:['’-][^\W_]+)*", normalized, flags=re.UNICODE)


def issue(
    issues: list[dict[str, Any]],
    severity: str,
    code: str,
    message: str,
    location: str | None = None,
) -> None:
    entry: dict[str, Any] = {"severity": severity, "code": code, "message": message}
    if location:
        entry["location"] = location
    issues.append(entry)


def read_limited(path: Path) -> bytes:
    size = path.stat().st_size
    if size > MAX_INPUT_BYTES:
        raise ValueError(f"input exceeds {MAX_INPUT_BYTES} bytes")
    return path.read_bytes()


def collect_text(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, list):
        parts: list[str] = []
        for item in value:
            parts.extend(collect_text(item))
        return parts
    if not isinstance(value, dict):
        return []

    lowered = {str(key).casefold(): item for key, item in value.items()}
    for key in TEXT_KEYS:
        if key in lowered:
            parts = collect_text(lowered[key])
            if parts:
                return parts

    parts = []
    for key in CONTAINER_KEYS:
        if key in lowered:
            parts.extend(collect_text(lowered[key]))
    return parts


def load_transcript(path_text: str) -> tuple[str, dict[str, Any]]:
    path = Path(path_text)
    raw = read_limited(path)
    digest = hashlib.sha256(raw).hexdigest()
    decoded = raw.decode("utf-8-sig")
    file_format = "text"
    if path.suffix.casefold() == ".json":
        file_format = "json"
        payload = json.loads(decoded)
        parts = collect_text(payload)
        if not parts:
            raise ValueError("JSON contains no recognized transcript text fields")
        decoded = "\n".join(parts)
    if not decoded.strip():
        raise ValueError("transcript is empty")
    return decoded, {
        "path": str(path),
        "sha256": digest,
        "bytes": len(raw),
        "format": file_format,
    }


def load_manifest(path_text: str) -> tuple[dict[str, Any], dict[str, Any]]:
    path = Path(path_text)
    raw = read_limited(path)
    digest = hashlib.sha256(raw).hexdigest()
    payload = json.loads(raw.decode("utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError("manifest root must be a JSON object")
    return payload, {"path": str(path), "sha256": digest, "bytes": len(raw), "format": "json"}


def first_value(mapping: dict[str, Any], keys: Iterable[str]) -> Any:
    for key in keys:
        if key in mapping:
            return mapping[key]
    return None


def nonempty(value: Any) -> bool:
    return value is not None and (not isinstance(value, str) or bool(value.strip()))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_ready_asset_file(
    asset: dict[str, Any],
    location: str,
    manifest_parent: Path,
    issues: list[dict[str, Any]],
) -> dict[str, Any]:
    result: dict[str, Any] = {"local_path": None, "resolved_path": None, "sha256_verified": False}
    local_path_value = asset.get("local_path")
    if not nonempty(local_path_value):
        issue(
            issues,
            "INCOMPLETE",
            "READY_ASSET_PATH_MISSING",
            "Every ready asset needs a workspace-relative local_path.",
            location,
        )
        return result
    if not isinstance(local_path_value, str):
        issue(
            issues,
            "INCOMPLETE",
            "READY_ASSET_PATH_INVALID",
            "Ready asset local_path must be a string.",
            location,
        )
        return result

    result["local_path"] = local_path_value
    relative_path = Path(local_path_value)
    if relative_path.is_absolute() or bool(relative_path.drive):
        issue(
            issues,
            "BLOCK",
            "READY_ASSET_PATH_ABSOLUTE",
            "Ready asset local_path must not be absolute or drive-qualified.",
            location,
        )
        return result

    base = manifest_parent.resolve(strict=False)
    resolved = (base / relative_path).resolve(strict=False)
    result["resolved_path"] = str(resolved)
    try:
        resolved.relative_to(base)
    except ValueError:
        issue(
            issues,
            "BLOCK",
            "READY_ASSET_PATH_ESCAPES_MANIFEST",
            "Ready asset local_path resolves outside the manifest directory.",
            location,
        )
        return result

    declared_hash = asset.get("sha256")
    if not isinstance(declared_hash, str) or re.fullmatch(r"[0-9a-fA-F]{64}", declared_hash) is None:
        issue(
            issues,
            "INCOMPLETE",
            "READY_ASSET_HASH_INVALID",
            "Ready asset needs a valid 64-character hexadecimal sha256 value.",
            location,
        )
        return result
    if not resolved.exists() or not resolved.is_file():
        issue(
            issues,
            "INCOMPLETE",
            "READY_ASSET_FILE_MISSING",
            "Ready asset local_path does not resolve to an existing file.",
            location,
        )
        return result

    try:
        actual_hash = sha256_file(resolved)
    except OSError as exc:
        issue(
            issues,
            "INCOMPLETE",
            "READY_ASSET_FILE_UNREADABLE",
            f"Ready asset could not be hashed: {exc}",
            location,
        )
        return result
    result["actual_sha256"] = actual_hash
    if not hmac.compare_digest(actual_hash, declared_hash.casefold()):
        issue(
            issues,
            "BLOCK",
            "READY_ASSET_HASH_MISMATCH",
            "Ready asset content does not match the manifest sha256 value.",
            location,
        )
        return result

    result["sha256_verified"] = True
    return result


def rights_label(license_data: Any) -> str:
    if isinstance(license_data, str):
        return normalize_enum(license_data)
    if not isinstance(license_data, dict):
        return ""
    return normalize_enum(first_value(license_data, ("status", "name", "type", "license")))


def classify_rights(label: str) -> str:
    if not label:
        return "missing"
    if label in BLOCKED_RIGHTS or any(term in label for term in ("denied", "revoked", "prohibited")):
        return "blocked"
    if label in REVIEW_RIGHTS or "fair_use" in label or "editorial" in label:
        return "review"
    if label in ALLOWED_RIGHTS:
        return "allowed"
    if label.startswith("cc_by_sa"):
        return "allowed"
    if label.startswith("cc_by") or label.startswith("creative_commons_attribution"):
        return "allowed"
    if label.startswith("cc0") or label.startswith("public_domain"):
        return "allowed"
    return "review"


def validate_asset(
    asset: Any,
    location: str,
    manifest_parent: Path,
    issues: list[dict[str, Any]],
) -> dict[str, Any]:
    result: dict[str, Any] = {"location": location, "rights_result": "INCOMPLETE"}
    if not isinstance(asset, dict):
        issue(issues, "INCOMPLETE", "ASSET_NOT_OBJECT", "Asset entry must be a JSON object.", location)
        return result

    if normalize_enum(asset.get("status")) == "ready":
        result["file_integrity"] = validate_ready_asset_file(
            asset,
            location,
            manifest_parent,
            issues,
        )

    asset_id = first_value(asset, ("id", "name", "local_path", "path", "url", "locator"))
    result["asset_id"] = str(asset_id) if nonempty(asset_id) else None
    if not nonempty(asset_id):
        issue(issues, "INCOMPLETE", "ASSET_ID_MISSING", "Asset needs an ID, path, URL, or locator.", location)

    provenance = asset.get("provenance")
    if not isinstance(provenance, dict):
        issue(
            issues,
            "INCOMPLETE",
            "PROVENANCE_MISSING",
            "Asset provenance must be a structured object.",
            location,
        )
        return result

    for key in ("origin", "creator", "source_locator"):
        if not nonempty(provenance.get(key)):
            issue(
                issues,
                "INCOMPLETE",
                f"PROVENANCE_{key.upper()}_MISSING",
                f"Asset provenance is missing {key}.",
                location,
            )
    if not nonempty(provenance.get("retrieved_at")):
        issue(
            issues,
            "INCOMPLETE",
            "PROVENANCE_DATE_MISSING",
            "Asset provenance is missing retrieved_at.",
            location,
        )

    license_data = provenance.get("license", asset.get("license"))
    if not isinstance(license_data, (dict, str)) or not license_data:
        issue(issues, "INCOMPLETE", "LICENSE_MISSING", "Asset license metadata is missing.", location)
        return result

    label = rights_label(license_data)
    result["license_label"] = label or None
    classification = classify_rights(label)
    if classification == "missing":
        issue(
            issues,
            "INCOMPLETE",
            "LICENSE_NAME_MISSING",
            "License metadata needs a name, status, or type.",
            location,
        )
    elif classification == "blocked":
        issue(
            issues,
            "BLOCK",
            "LICENSE_EXPLICITLY_DISALLOWED",
            f"License status '{label}' is a publication stop condition.",
            location,
        )
    elif classification == "review":
        issue(
            issues,
            "REVIEW",
            "LICENSE_NEEDS_REVIEW",
            f"License status '{label}' needs qualified human review.",
            location,
        )

    if isinstance(license_data, dict):
        evidence = first_value(
            license_data,
            ("terms_locator", "evidence_locator", "evidence", "license_url", "receipt", "source_url"),
        )
        if not nonempty(evidence):
            issue(
                issues,
                "INCOMPLETE",
                "LICENSE_EVIDENCE_MISSING",
                "License needs a terms or evidence locator.",
                location,
            )
        commercial = first_value(
            license_data,
            ("commercial_use_allowed", "commercial_use", "commercial_allowed"),
        )
        if commercial is False:
            issue(
                issues,
                "BLOCK",
                "COMMERCIAL_USE_DENIED",
                "Asset license explicitly disallows commercial use.",
                location,
            )
        elif commercial is not True:
            issue(
                issues,
                "INCOMPLETE",
                "COMMERCIAL_USE_UNRESOLVED",
                "License needs an explicit commercial_use_allowed boolean.",
                location,
            )
        if not nonempty(first_value(license_data, ("checked_at", "verified_at"))):
            issue(
                issues,
                "INCOMPLETE",
                "LICENSE_CHECK_DATE_MISSING",
                "License metadata needs checked_at or verified_at.",
                location,
            )
    else:
        issue(
            issues,
            "INCOMPLETE",
            "LICENSE_EVIDENCE_MISSING",
            "A license string alone does not document evidence or commercial-use permission.",
            location,
        )

    generation = provenance.get("generation")
    origin = normalize_enum(provenance.get("origin"))
    if origin in {"generated", "ai_generated", "synthetic"} or generation is not None:
        if not isinstance(generation, dict):
            issue(
                issues,
                "INCOMPLETE",
                "GENERATION_METADATA_MISSING",
                "Generated asset needs structured generation metadata.",
                location,
            )
        else:
            for key in ("provider", "model", "prompt", "generated_at"):
                if not nonempty(generation.get(key)):
                    issue(
                        issues,
                        "INCOMPLETE",
                        f"GENERATION_{key.upper()}_MISSING",
                        f"Generated asset metadata is missing {key}.",
                        location,
                    )
            if not isinstance(generation.get("reference_asset_ids"), list):
                issue(
                    issues,
                    "INCOMPLETE",
                    "GENERATION_REFERENCES_MISSING",
                    "Generated asset metadata needs a reference_asset_ids list, even when empty.",
                    location,
                )

    result["rights_result"] = (
        "BLOCK"
        if any(item["severity"] == "BLOCK" and item.get("location") == location for item in issues)
        else "INCOMPLETE"
        if any(item["severity"] == "INCOMPLETE" and item.get("location") == location for item in issues)
        else "REVIEW"
        if any(item["severity"] == "REVIEW" and item.get("location") == location for item in issues)
        else "PASS"
    )
    return result


def consent_values(voice: dict[str, Any]) -> tuple[bool | None, str, Any]:
    compact = voice.get("consent_verified")
    if isinstance(compact, bool):
        return compact, "verified" if compact else "not_verified", None

    consent = voice.get("consent")
    if isinstance(consent, bool):
        return consent, "confirmed" if consent else "denied", None
    if isinstance(consent, str):
        status = normalize_enum(consent)
        if status in {"confirmed", "verified", "granted", "permission_granted"}:
            return True, status, None
        if status in {"denied", "revoked", "refused"}:
            return False, status, None
        return None, status, None
    if not isinstance(consent, dict):
        return None, "", None

    confirmed = first_value(consent, ("confirmed", "verified", "granted"))
    status = normalize_enum(consent.get("status"))
    if not isinstance(confirmed, bool):
        if status in {"confirmed", "verified", "granted", "permission_granted"}:
            confirmed = True
        elif status in {"denied", "revoked", "refused"}:
            confirmed = False
        else:
            confirmed = None
    evidence = first_value(consent, ("evidence_locator", "evidence", "consent_record", "release_path"))
    return confirmed, status, evidence


def validate_voice(voice: Any, issues: list[dict[str, Any]]) -> dict[str, Any]:
    location = "voice"
    result: dict[str, Any] = {"result": "INCOMPLETE"}
    if not isinstance(voice, dict):
        issue(issues, "INCOMPLETE", "VOICE_MISSING", "Manifest needs a structured voice object.", location)
        return result

    mode = normalize_enum(voice.get("mode"))
    result["mode"] = mode or None
    if not mode:
        issue(issues, "INCOMPLETE", "VOICE_MODE_MISSING", "Voice mode is required.", location)

    clone = voice.get("real_person_clone")
    if not isinstance(clone, bool):
        issue(
            issues,
            "INCOMPLETE",
            "VOICE_CLONE_DECLARATION_MISSING",
            "Voice needs an explicit real_person_clone boolean.",
            location,
        )
        clone_value: bool | None = None
    else:
        clone_value = clone
    result["real_person_clone"] = clone_value

    mode_declares_clone = "clone" in mode or "imperson" in mode
    if mode_declares_clone and clone_value is False:
        issue(
            issues,
            "BLOCK",
            "VOICE_CLONE_CONFLICT",
            "Voice mode declares cloning while real_person_clone is false.",
            location,
        )

    confirmed, consent_status, evidence = consent_values(voice)
    result["consent_status"] = consent_status or None
    needs_person_consent = clone_value is True or mode in {
        "original_recording",
        "human_recording",
        "recorded_narrator",
    }

    if needs_person_consent:
        if confirmed is False:
            issue(
                issues,
                "BLOCK",
                "VOICE_CONSENT_DENIED",
                "Required voice consent is explicitly absent, denied, or revoked.",
                location,
            )
        elif confirmed is not True:
            issue(
                issues,
                "INCOMPLETE",
                "VOICE_CONSENT_MISSING",
                "Required voice consent is not confirmed.",
                location,
            )
        elif not nonempty(evidence):
            issue(
                issues,
                "INCOMPLETE",
                "VOICE_CONSENT_EVIDENCE_MISSING",
                "Confirmed voice consent needs an evidence locator.",
                location,
            )
        if clone_value is True and confirmed is True and nonempty(evidence):
            issue(
                issues,
                "REVIEW",
                "VOICE_CLONE_REQUIRES_REVIEW",
                "A consented real-person voice clone still needs identity, scope, provider, and disclosure review.",
                location,
            )

    known_modes = {
        "tts_synthetic",
        "synthetic_original",
        "stock_tts",
        "licensed_tts",
        "original_recording",
        "human_recording",
        "recorded_narrator",
        "voice_clone",
        "none",
    }
    if mode and mode not in known_modes and not mode_declares_clone:
        issue(
            issues,
            "REVIEW",
            "VOICE_MODE_UNKNOWN",
            f"Voice mode '{mode}' is not recognized by this policy.",
            location,
        )

    result["result"] = (
        "BLOCK"
        if any(item["severity"] == "BLOCK" and item.get("location") == location for item in issues)
        else "INCOMPLETE"
        if any(item["severity"] == "INCOMPLETE" and item.get("location") == location for item in issues)
        else "REVIEW"
        if any(item["severity"] == "REVIEW" and item.get("location") == location for item in issues)
        else "PASS"
    )
    return result


def validate_motion_quality(
    motion: Any,
    manifest_parent: Path,
    issues: list[dict[str, Any]],
) -> dict[str, Any]:
    result: dict[str, Any] = {"status": "INCOMPLETE", "report_sha256_verified": False}
    location = "motion_quality"
    if not isinstance(motion, dict):
        issue(
            issues,
            "INCOMPLETE",
            "MOTION_QUALITY_MISSING",
            "Manifest needs a motion_quality object backed by automated analysis and manual playback review.",
            location,
        )
        return result

    declared_status = normalize_enum(motion.get("status"))
    result["declared_status"] = declared_status
    if declared_status in {"", "pending"}:
        issue(
            issues,
            "INCOMPLETE",
            "MOTION_QUALITY_PENDING",
            "Motion quality analysis and manual review are not complete.",
            f"{location}.status",
        )
    elif declared_status != "passed":
        issue(
            issues,
            "REVIEW",
            "MOTION_QUALITY_FAILED",
            "The render did not pass the motion-quality gate.",
            f"{location}.status",
        )

    minimums = {
        "meaningful_motion_screen_time_ratio": 0.65,
        "distributed_motion_screen_time_ratio": 0.50,
        "independent_layer_motion_shot_ratio": 0.80,
        "interaction_shot_ratio": 0.60,
    }
    maximums = {
        "camera_only_screen_time_ratio": 0.15,
        "max_static_hold_seconds": 2.0,
    }
    metrics: dict[str, Any] = {}
    for field, threshold in minimums.items():
        value = motion.get(field)
        metrics[field] = value
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            issue(
                issues,
                "INCOMPLETE",
                "MOTION_METRIC_MISSING",
                f"{field} must be a number.",
                f"{location}.{field}",
            )
        elif not 0 <= value <= 1:
            issue(
                issues,
                "INCOMPLETE",
                "MOTION_METRIC_INVALID",
                f"{field} must be between 0 and 1.",
                f"{location}.{field}",
            )
        elif value < threshold:
            issue(
                issues,
                "REVIEW",
                "MOTION_THRESHOLD_FAILED",
                f"{field} is {value:.3f}; required minimum is {threshold:.2f}.",
                f"{location}.{field}",
            )
    for field, threshold in maximums.items():
        value = motion.get(field)
        metrics[field] = value
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
            issue(
                issues,
                "INCOMPLETE",
                "MOTION_METRIC_MISSING",
                f"{field} must be a non-negative number.",
                f"{location}.{field}",
            )
        elif field.endswith("ratio") and value > 1:
            issue(
                issues,
                "INCOMPLETE",
                "MOTION_METRIC_INVALID",
                f"{field} must not exceed 1.",
                f"{location}.{field}",
            )
        elif value > threshold:
            issue(
                issues,
                "REVIEW",
                "MOTION_THRESHOLD_FAILED",
                f"{field} is {value:.3f}; allowed maximum is {threshold:.2f}.",
                f"{location}.{field}",
            )
    result["metrics"] = metrics

    for field in ("manual_reviewed_by", "manual_reviewed_at"):
        if not isinstance(motion.get(field), str) or not motion[field].strip():
            issue(
                issues,
                "INCOMPLETE",
                "MOTION_MANUAL_REVIEW_MISSING",
                f"{field} must record a completed human playback review.",
                f"{location}.{field}",
            )

    report_path_value = motion.get("automated_report_path")
    declared_hash = motion.get("automated_report_sha256")
    if not isinstance(report_path_value, str) or not report_path_value.strip():
        issue(
            issues,
            "INCOMPLETE",
            "MOTION_REPORT_MISSING",
            "automated_report_path must identify the workspace-relative motion report.",
            f"{location}.automated_report_path",
        )
        return result
    relative_path = Path(report_path_value)
    if relative_path.is_absolute() or bool(relative_path.drive):
        issue(
            issues,
            "BLOCK",
            "MOTION_REPORT_PATH_ABSOLUTE",
            "Motion report path must not be absolute or drive-qualified.",
            f"{location}.automated_report_path",
        )
        return result
    base = manifest_parent.resolve(strict=False)
    resolved = (base / relative_path).resolve(strict=False)
    try:
        resolved.relative_to(base)
    except ValueError:
        issue(
            issues,
            "BLOCK",
            "MOTION_REPORT_PATH_ESCAPES_MANIFEST",
            "Motion report path resolves outside the manifest directory.",
            f"{location}.automated_report_path",
        )
        return result
    result["report_path"] = str(resolved)
    if not resolved.is_file():
        issue(
            issues,
            "INCOMPLETE",
            "MOTION_REPORT_FILE_MISSING",
            "Motion report does not resolve to an existing file.",
            f"{location}.automated_report_path",
        )
        return result
    if not isinstance(declared_hash, str) or re.fullmatch(r"[0-9a-fA-F]{64}", declared_hash) is None:
        issue(
            issues,
            "INCOMPLETE",
            "MOTION_REPORT_HASH_INVALID",
            "automated_report_sha256 must be a 64-character hexadecimal hash.",
            f"{location}.automated_report_sha256",
        )
        return result
    actual_hash = sha256_file(resolved)
    if not hmac.compare_digest(actual_hash, declared_hash.casefold()):
        issue(
            issues,
            "BLOCK",
            "MOTION_REPORT_HASH_MISMATCH",
            "Motion report content does not match automated_report_sha256.",
            f"{location}.automated_report_sha256",
        )
        return result
    result["report_sha256_verified"] = True
    result["status"] = "PASS" if declared_status == "passed" else declared_status.upper() or "INCOMPLETE"
    return result


def validate_manifest(
    manifest: dict[str, Any],
    manifest_parent: Path,
    issues: list[dict[str, Any]],
) -> dict[str, Any]:
    inventory_key = None
    inventory_complete = None
    for key in ("asset_inventory_complete", "inventory_complete"):
        if key in manifest:
            inventory_key = key
            inventory_complete = manifest[key]
            break
    if inventory_complete is not True:
        issue(
            issues,
            "INCOMPLETE",
            "ASSET_INVENTORY_INCOMPLETE",
            "Manifest must explicitly declare asset_inventory_complete: true.",
            inventory_key or "manifest",
        )

    assets_value = manifest.get("assets")
    inventory_source = "assets"
    if isinstance(assets_value, list):
        assets = assets_value
    else:
        sources = manifest.get("sources")
        rights_sources = (
            sources
            if isinstance(sources, list)
            and any(isinstance(item, dict) and ("provenance" in item or "license" in item) for item in sources)
            else None
        )
        if rights_sources is not None:
            assets = rights_sources
            inventory_source = "sources"
        else:
            assets = []
            issue(
                issues,
                "INCOMPLETE",
                "ASSET_INVENTORY_MISSING",
                "Manifest needs assets[] or a rights-bearing legacy sources[] inventory.",
                "manifest",
            )

    if not assets:
        issue(
            issues,
            "INCOMPLETE",
            "ASSET_INVENTORY_EMPTY",
            "A pre-publication video audit requires at least one production asset; original_assets_only does not exempt an empty inventory.",
            inventory_source,
        )

    asset_results = [
        validate_asset(asset, f"{inventory_source}[{index}]", manifest_parent, issues)
        for index, asset in enumerate(assets)
    ]
    voice_result = validate_voice(manifest.get("voice"), issues)
    motion_result = validate_motion_quality(manifest.get("motion_quality"), manifest_parent, issues)
    return {
        "inventory_source": inventory_source,
        "inventory_complete": inventory_complete is True,
        "asset_count": len(assets),
        "assets": asset_results,
        "voice": voice_result,
        "motion_quality": motion_result,
    }


def shingle_stats_many(candidate: list[str], references: list[list[str]]) -> dict[str, Any]:
    candidate_windows = max(0, len(candidate) - SHINGLE_SIZE + 1)
    if candidate_windows == 0:
        return {"matched_shingle_ratio": 0.0, "covered_candidate_word_ratio": 0.0}
    reference_shingles: set[tuple[str, ...]] = set()
    for reference in references:
        reference_shingles.update(
            tuple(reference[index : index + SHINGLE_SIZE])
            for index in range(max(0, len(reference) - SHINGLE_SIZE + 1))
        )
    covered = [False] * len(candidate)
    matched_windows = 0
    for index in range(candidate_windows):
        if tuple(candidate[index : index + SHINGLE_SIZE]) in reference_shingles:
            matched_windows += 1
            for position in range(index, index + SHINGLE_SIZE):
                covered[position] = True
    return {
        "matched_shingle_ratio": round(matched_windows / candidate_windows, 6),
        "covered_candidate_word_ratio": round(sum(covered) / len(candidate), 6),
    }


def shingle_stats(candidate: list[str], reference: list[str]) -> dict[str, Any]:
    return shingle_stats_many(candidate, [reference])


def phrase_excerpt(words: list[str], start: int, length: int, limit: int = 240) -> str:
    phrase = " ".join(words[start : start + length])
    return phrase if len(phrase) <= limit else phrase[: limit - 1].rstrip() + "…"


def analyze_text(
    candidate_text: str,
    reference_texts: list[tuple[str, str]],
    issues: list[dict[str, Any]],
) -> dict[str, Any]:
    candidate = tokenize(candidate_text)
    per_reference: list[dict[str, Any]] = []
    reference_token_sets: list[list[str]] = []
    phrases: list[dict[str, Any]] = []

    for reference_path, reference_text in reference_texts:
        reference = tokenize(reference_text)
        reference_token_sets.append(reference)
        stats = shingle_stats(candidate, reference)
        matcher = difflib.SequenceMatcher(a=candidate, b=reference, autojunk=False)
        reference_phrases = []
        for block in matcher.get_matching_blocks():
            if block.size >= REPORT_PHRASE_WORDS:
                entry = {
                    "reference": reference_path,
                    "candidate_word_start": block.a,
                    "reference_word_start": block.b,
                    "word_count": block.size,
                    "excerpt": phrase_excerpt(candidate, block.a, block.size),
                }
                reference_phrases.append(entry)
                phrases.append(entry)
        per_reference.append(
            {
                "path": reference_path,
                "word_count": len(reference),
                **stats,
                "longest_exact_phrase_words": max(
                    (entry["word_count"] for entry in reference_phrases), default=0
                ),
            }
        )

    combined = shingle_stats_many(candidate, reference_token_sets)
    phrases.sort(key=lambda item: (-item["word_count"], item["reference"], item["candidate_word_start"]))
    phrases = phrases[:MAX_PHRASES]
    longest = max((entry["word_count"] for entry in phrases), default=0)
    coverage = combined["covered_candidate_word_ratio"]

    if coverage >= BLOCK_COVERAGE:
        issue(
            issues,
            "BLOCK",
            "TEXT_OVERLAP_BLOCK",
            f"{coverage:.1%} of candidate words are covered by matching {SHINGLE_SIZE}-word shingles.",
            "candidate",
        )
    elif coverage >= REVIEW_COVERAGE:
        issue(
            issues,
            "REVIEW",
            "TEXT_OVERLAP_REVIEW",
            f"{coverage:.1%} of candidate words are covered by matching {SHINGLE_SIZE}-word shingles.",
            "candidate",
        )

    if longest >= BLOCK_PHRASE_WORDS:
        issue(
            issues,
            "BLOCK",
            "LONG_PHRASE_BLOCK",
            f"Longest exact matching phrase is {longest} words.",
            "candidate",
        )
    elif longest >= REVIEW_PHRASE_WORDS:
        issue(
            issues,
            "REVIEW",
            "LONG_PHRASE_REVIEW",
            f"Longest exact matching phrase is {longest} words.",
            "candidate",
        )

    return {
        "candidate_word_count": len(candidate),
        "reference_count": len(reference_texts),
        "combined_reference_word_count": sum(len(words) for words in reference_token_sets),
        "shingle_size_words": SHINGLE_SIZE,
        "combined": {**combined, "longest_exact_phrase_words": longest},
        "per_reference": per_reference,
        "matching_phrases": phrases,
    }


def select_status(issues: list[dict[str, Any]]) -> str:
    severities = {item["severity"] for item in issues}
    for status in STATUS_PRECEDENCE:
        if status == "PASS" or status in severities:
            return status
    return "PASS"


def manual_checks() -> list[dict[str, Any]]:
    return [
        {
            "id": "visual_similarity",
            "status": "NOT_EVALUATED",
            "required": True,
            "instruction": "Compare frames, shot order, composition, thumbnails, characters, logos, colors, and distinctive transitions.",
        },
        {
            "id": "factual_citations",
            "status": "NOT_EVALUATED",
            "required": True,
            "instruction": "Verify each material claim against primary or authoritative sources and record citations or timecodes.",
        },
        {
            "id": "ai_disclosure",
            "status": "NOT_EVALUATED",
            "required": True,
            "instruction": "Check platform and audience disclosure requirements for synthetic voice and generated or altered media.",
        },
        {
            "id": "motion_quality",
            "status": "NOT_EVALUATED",
            "required": True,
            "instruction": "Watch representative shots and confirm independent subject, environment, and depth motion plus visible cause-and-effect interaction; camera motion over one flattened still does not qualify.",
        },
        {
            "id": "technical_qa",
            "status": "NOT_EVALUATED",
            "required": True,
            "instruction": "Watch the full export for sync, captions, pronunciation, clipping, loudness, black frames, encoding, safe areas, and duration.",
        },
    ]


def write_json_atomic(path: Path, payload: dict[str, Any], overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError("output exists; choose a new path or pass --overwrite")
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="\n",
        dir=str(path.parent),
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    )
    temporary = Path(handle.name)
    try:
        with handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def same_path(left: Path, right: Path) -> bool:
    return left.resolve(strict=False) == right.resolve(strict=False)


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    input_paths = [Path(args.candidate), *(Path(item) for item in args.reference), Path(args.manifest)]
    if any(same_path(output_path, input_path) for input_path in input_paths):
        print("Refusing to write: --output resolves to an input path.", file=sys.stderr)
        return EXIT_CODES["INCOMPLETE"]

    issues: list[dict[str, Any]] = []
    inputs: dict[str, Any] = {"candidate": None, "references": [], "manifest": None}
    candidate_text: str | None = None
    references: list[tuple[str, str]] = []
    manifest: dict[str, Any] | None = None

    try:
        candidate_text, inputs["candidate"] = load_transcript(args.candidate)
    except Exception as exc:
        inputs["candidate"] = {"path": args.candidate, "error": str(exc)}
        issue(issues, "INCOMPLETE", "CANDIDATE_UNREADABLE", str(exc), "candidate")

    for index, reference_path in enumerate(args.reference):
        try:
            text, metadata = load_transcript(reference_path)
            references.append((reference_path, text))
            inputs["references"].append(metadata)
        except Exception as exc:
            inputs["references"].append({"path": reference_path, "error": str(exc)})
            issue(
                issues,
                "INCOMPLETE",
                "REFERENCE_UNREADABLE",
                str(exc),
                f"references[{index}]",
            )

    try:
        manifest, inputs["manifest"] = load_manifest(args.manifest)
    except Exception as exc:
        inputs["manifest"] = {"path": args.manifest, "error": str(exc)}
        issue(issues, "INCOMPLETE", "MANIFEST_UNREADABLE", str(exc), "manifest")

    text_analysis: dict[str, Any] = {"result": "NOT_COMPUTED"}
    if candidate_text is not None and len(references) == len(args.reference):
        text_analysis = analyze_text(candidate_text, references, issues)

    manifest_analysis: dict[str, Any] = {"result": "NOT_COMPUTED"}
    if manifest is not None:
        manifest_analysis = validate_manifest(manifest, Path(args.manifest).parent, issues)

    status = select_status(issues)
    counts = {name: sum(item["severity"] == name for item in issues) for name in STATUS_PRECEDENCE[:-1]}
    result = {
        "schema_version": "audit-faceless-video/1.1",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "status": status,
        "exit_code": EXIT_CODES[status],
        "legal_notice": LEGAL_NOTICE,
        "publication_gate": {
            "automated_status": status,
            "manual_status": "OPEN",
            "ready_to_publish": False,
            "reason": "All mandatory manual checks remain NOT_EVALUATED.",
        },
        "policy": {
            "version": POLICY_VERSION,
            "shingle_size_words": SHINGLE_SIZE,
            "review_covered_word_ratio": REVIEW_COVERAGE,
            "block_covered_word_ratio": BLOCK_COVERAGE,
            "review_exact_phrase_words": REVIEW_PHRASE_WORDS,
            "block_exact_phrase_words": BLOCK_PHRASE_WORDS,
            "status_precedence": list(STATUS_PRECEDENCE),
        },
        "inputs": inputs,
        "text_analysis": text_analysis,
        "manifest_analysis": manifest_analysis,
        "issue_counts": counts,
        "issues": issues,
        "manual_checks": manual_checks(),
    }

    try:
        write_json_atomic(output_path, result, args.overwrite)
    except Exception as exc:
        print(f"Could not write audit report: {exc}", file=sys.stderr)
        return EXIT_CODES["INCOMPLETE"]

    print(f"{status}: wrote {output_path}")
    return EXIT_CODES[status]


if __name__ == "__main__":
    raise SystemExit(main())
