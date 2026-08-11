#!/usr/bin/env python3
"""Deterministic frame-change screen for slideshow-like faceless-video renders."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any


EXIT_CODES = {"PASS": 0, "REVIEW": 1, "INCOMPLETE": 3}
FRAME_WIDTH = 160
FRAME_HEIGHT = 90
PIXELS_PER_FRAME = FRAME_WIDTH * FRAME_HEIGHT
GRID_COLUMNS = 8
GRID_ROWS = 5

MEANINGFUL_MOTION_MINIMUM = 0.65
DISTRIBUTED_MOTION_MINIMUM = 0.50
STATIC_SCREEN_TIME_MAXIMUM = 0.25
STATIC_HOLD_MAXIMUM_SECONDS = 2.0

PIXEL_CHANGE_THRESHOLD = 8
STRONG_PIXEL_CHANGE_THRESHOLD = 24
MEANINGFUL_PAIR_RATIO = 0.08
STATIC_PAIR_RATIO = 0.02
ACTIVE_CELL_RATIO = 0.04
CUT_PIXEL_RATIO = 0.70
CUT_MEAN_DIFFERENCE = 24.0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Measure local and distributed frame change in a rendered video."
    )
    parser.add_argument("--video", required=True, help="Candidate video file")
    parser.add_argument("--output", required=True, help="New motion-audit JSON path")
    parser.add_argument("--ffmpeg", help="Optional explicit FFmpeg executable")
    parser.add_argument("--sample-rate-fps", type=float, default=6.0)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def same_path(left: Path, right: Path) -> bool:
    return left.resolve(strict=False) == right.resolve(strict=False)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_ffmpeg(explicit: str | None) -> str:
    if explicit:
        candidate = Path(explicit)
        if not candidate.is_file():
            raise FileNotFoundError(f"FFmpeg executable does not exist: {candidate}")
        return str(candidate)
    executable = shutil.which("ffmpeg")
    if executable:
        return executable
    try:
        import imageio_ffmpeg  # type: ignore

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as exc:
        raise FileNotFoundError(
            "FFmpeg was not found. Install it, pass --ffmpeg, or install imageio-ffmpeg."
        ) from exc


def read_exact(stream: Any, byte_count: int) -> bytes:
    chunks: list[bytes] = []
    remaining = byte_count
    while remaining:
        chunk = stream.read(remaining)
        if not chunk:
            break
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def pair_metrics(previous: bytes, current: bytes) -> dict[str, float]:
    changed = 0
    strong = 0
    total_difference = 0
    cell_changed = [0] * (GRID_COLUMNS * GRID_ROWS)
    cell_total = [0] * (GRID_COLUMNS * GRID_ROWS)

    cell_width = FRAME_WIDTH // GRID_COLUMNS
    cell_height = FRAME_HEIGHT // GRID_ROWS
    for index, (left, right) in enumerate(zip(previous, current)):
        difference = abs(left - right)
        total_difference += difference
        if difference >= PIXEL_CHANGE_THRESHOLD:
            changed += 1
        if difference >= STRONG_PIXEL_CHANGE_THRESHOLD:
            strong += 1
        x = index % FRAME_WIDTH
        y = index // FRAME_WIDTH
        column = min(x // cell_width, GRID_COLUMNS - 1)
        row = min(y // cell_height, GRID_ROWS - 1)
        cell_index = row * GRID_COLUMNS + column
        cell_total[cell_index] += 1
        if difference >= PIXEL_CHANGE_THRESHOLD:
            cell_changed[cell_index] += 1

    moving_ratio = changed / PIXELS_PER_FRAME
    active_cells = sum(
        changed_count / total_count >= ACTIVE_CELL_RATIO
        for changed_count, total_count in zip(cell_changed, cell_total)
        if total_count
    )
    return {
        "mean_absolute_difference": total_difference / PIXELS_PER_FRAME,
        "moving_pixel_ratio": moving_ratio,
        "strong_motion_pixel_ratio": strong / PIXELS_PER_FRAME,
        "active_grid_cell_ratio": active_cells / (GRID_COLUMNS * GRID_ROWS),
    }


def analyze_video(video: Path, ffmpeg: str, sample_rate_fps: float) -> dict[str, Any]:
    if sample_rate_fps <= 0 or sample_rate_fps > 30:
        raise ValueError("--sample-rate-fps must be greater than 0 and at most 30")
    command = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(video),
        "-vf",
        f"fps={sample_rate_fps},scale={FRAME_WIDTH}:{FRAME_HEIGHT},format=gray",
        "-an",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "gray",
        "pipe:1",
    ]
    creation_flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=creation_flags,
    )
    assert process.stdout is not None
    assert process.stderr is not None

    frame_count = 0
    previous: bytes | None = None
    analyzed_pairs = 0
    meaningful_pairs = 0
    distributed_pairs = 0
    static_pairs = 0
    scene_cuts = 0
    current_static_run = 0
    longest_static_run = 0
    moving_ratios: list[float] = []
    strong_ratios: list[float] = []
    active_grid_ratios: list[float] = []

    while True:
        frame = read_exact(process.stdout, PIXELS_PER_FRAME)
        if not frame:
            break
        if len(frame) != PIXELS_PER_FRAME:
            process.kill()
            raise RuntimeError("FFmpeg returned a truncated raw frame")
        frame_count += 1
        if previous is not None:
            metrics = pair_metrics(previous, frame)
            is_cut = (
                metrics["moving_pixel_ratio"] >= CUT_PIXEL_RATIO
                and metrics["mean_absolute_difference"] >= CUT_MEAN_DIFFERENCE
            )
            if is_cut:
                scene_cuts += 1
                current_static_run = 0
            else:
                analyzed_pairs += 1
                moving_ratios.append(metrics["moving_pixel_ratio"])
                strong_ratios.append(metrics["strong_motion_pixel_ratio"])
                active_grid_ratios.append(metrics["active_grid_cell_ratio"])
                if metrics["moving_pixel_ratio"] >= MEANINGFUL_PAIR_RATIO:
                    meaningful_pairs += 1
                if metrics["active_grid_cell_ratio"] >= 0.35:
                    distributed_pairs += 1
                if metrics["moving_pixel_ratio"] < STATIC_PAIR_RATIO:
                    static_pairs += 1
                    current_static_run += 1
                    longest_static_run = max(longest_static_run, current_static_run)
                else:
                    current_static_run = 0
        previous = frame

    stderr_text = process.stderr.read().decode("utf-8", errors="replace").strip()
    return_code = process.wait()
    if return_code != 0:
        raise RuntimeError(stderr_text or f"FFmpeg exited with code {return_code}")
    if frame_count < 2 or analyzed_pairs == 0:
        raise ValueError("Video yielded too few analyzable frames")

    def average(values: list[float]) -> float:
        return round(sum(values) / len(values), 6) if values else 0.0

    return {
        "sample_rate_fps": sample_rate_fps,
        "sampled_frame_count": frame_count,
        "analyzed_frame_pair_count": analyzed_pairs,
        "approximate_sampled_duration_seconds": round((frame_count - 1) / sample_rate_fps, 3),
        "probable_scene_cut_count": scene_cuts,
        "meaningful_motion_screen_time_ratio": round(meaningful_pairs / analyzed_pairs, 6),
        "distributed_motion_screen_time_ratio": round(distributed_pairs / analyzed_pairs, 6),
        "static_screen_time_ratio": round(static_pairs / analyzed_pairs, 6),
        "max_static_hold_seconds": round(longest_static_run / sample_rate_fps, 3),
        "mean_moving_pixel_ratio": average(moving_ratios),
        "mean_strong_motion_pixel_ratio": average(strong_ratios),
        "mean_active_grid_cell_ratio": average(active_grid_ratios),
    }


def evaluate(metrics: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    checks = [
        (
            "meaningful_motion_screen_time_ratio",
            metrics["meaningful_motion_screen_time_ratio"] >= MEANINGFUL_MOTION_MINIMUM,
            f">= {MEANINGFUL_MOTION_MINIMUM:.2f}",
        ),
        (
            "distributed_motion_screen_time_ratio",
            metrics["distributed_motion_screen_time_ratio"] >= DISTRIBUTED_MOTION_MINIMUM,
            f">= {DISTRIBUTED_MOTION_MINIMUM:.2f}",
        ),
        (
            "static_screen_time_ratio",
            metrics["static_screen_time_ratio"] <= STATIC_SCREEN_TIME_MAXIMUM,
            f"<= {STATIC_SCREEN_TIME_MAXIMUM:.2f}",
        ),
        (
            "max_static_hold_seconds",
            metrics["max_static_hold_seconds"] <= STATIC_HOLD_MAXIMUM_SECONDS,
            f"<= {STATIC_HOLD_MAXIMUM_SECONDS:.2f}",
        ),
    ]
    results = [
        {"metric": metric, "value": metrics[metric], "requirement": requirement, "passed": passed}
        for metric, passed, requirement in checks
    ]
    return ("PASS" if all(item[1] for item in checks) else "REVIEW"), results


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


def main() -> int:
    args = parse_args()
    video = Path(args.video)
    output = Path(args.output)
    if same_path(video, output):
        print("Refusing to write: --output resolves to the video input.", file=sys.stderr)
        return EXIT_CODES["INCOMPLETE"]

    base_result: dict[str, Any] = {
        "schema_version": "audit-motion/1.0",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "status": "INCOMPLETE",
        "exit_code": EXIT_CODES["INCOMPLETE"],
        "video": {"path": str(video)},
        "thresholds": {
            "meaningful_motion_screen_time_ratio_minimum": MEANINGFUL_MOTION_MINIMUM,
            "distributed_motion_screen_time_ratio_minimum": DISTRIBUTED_MOTION_MINIMUM,
            "static_screen_time_ratio_maximum": STATIC_SCREEN_TIME_MAXIMUM,
            "max_static_hold_seconds": STATIC_HOLD_MAXIMUM_SECONDS,
        },
        "manual_checks": [
            {
                "id": "camera_only_vs_local_motion",
                "status": "NOT_EVALUATED",
                "required": True,
                "instruction": "Reject camera movement over one flattened still as a substitute for local animation.",
            },
            {
                "id": "independent_layers",
                "status": "NOT_EVALUATED",
                "required": True,
                "instruction": "Confirm that subject, environment, effects, and depth layers move independently.",
            },
            {
                "id": "interaction_events",
                "status": "NOT_EVALUATED",
                "required": True,
                "instruction": "Confirm visible cause-and-effect interaction in explanatory shots.",
            },
        ],
        "limitations": [
            "Frame differences cannot prove that motion comes from independently controlled layers.",
            "A full-frame pan or zoom may look active numerically and still fail manual review.",
            "Compression noise and flicker can inflate measured motion.",
        ],
    }

    try:
        if not video.is_file():
            raise FileNotFoundError(f"video does not exist: {video}")
        base_result["video"].update(
            {"bytes": video.stat().st_size, "sha256": sha256_file(video)}
        )
        ffmpeg = find_ffmpeg(args.ffmpeg)
        metrics = analyze_video(video, ffmpeg, args.sample_rate_fps)
        status, checks = evaluate(metrics)
        base_result.update(
            {
                "status": status,
                "exit_code": EXIT_CODES[status],
                "analysis_method": "grayscale-frame-difference-grid-v1",
                "ffmpeg": ffmpeg,
                "metrics": metrics,
                "automated_checks": checks,
            }
        )
    except Exception as exc:
        base_result["error"] = str(exc)

    try:
        write_json_atomic(output, base_result, args.overwrite)
    except Exception as exc:
        print(f"Could not write motion report: {exc}", file=sys.stderr)
        return EXIT_CODES["INCOMPLETE"]

    print(f"{base_result['status']}: wrote {output}")
    return int(base_result["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
