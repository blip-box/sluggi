#!/usr/bin/env python3
"""Unified badge generator for benchmark and mutation testing.

Usage:
    python scripts/generate_badge.py --type benchmark \
        --input benchmark.log --output benchmark-badge.svg
    python scripts/generate_badge.py --type mutation \
        --input mutmut_cache --output mutmut-badge.svg
"""

import argparse
import json
import re
import sys
import urllib.parse

import requests


def generate_benchmark_badge(
    input_file: str,
    output_file: str,
    threshold_green: float = 0.05,
    threshold_yellow: float = 0.10,
    color_green: str = "brightgreen",
    color_yellow: str = "yellow",
    color_red: str = "red",
    label: str | None = None,
    message: str | None = None,
    dry_run: bool = False,
) -> None:
    """Generate a Shields.io badge for the fastest benchmark result.

    Supports both legacy plain-text and new JSON benchmark output.

    Args:
        input_file: Path to the benchmark log or JSON file.
        output_file: Path to output SVG badge file.
        threshold_green: Threshold (ms) for green badge color.
        threshold_yellow: Threshold (ms) for yellow badge color.
        color_green: Badge color for fastest (default: 'brightgreen').
        color_yellow: Badge color for medium (default: 'yellow').
        color_red: Badge color for slowest (default: 'red').
        label: Custom badge label (overrides default if set).
        message: Custom badge message (overrides default if set).
        dry_run: If True, print badge info instead of writing file.

    """
    is_json = input_file.endswith(".json")
    results = []
    if is_json:
        try:
            with open(input_file) as f:
                data = json.load(f)
            # Expect a list of dicts with keys: mode, method, total_ms, avg_ms_per_item
            for entry in data:
                # Defensive: skip if missing keys
                if not all(
                    k in entry
                    for k in ("mode", "method", "total_ms", "avg_ms_per_item")
                ):
                    continue
                results.append(
                    (
                        entry["mode"],
                        entry["method"],
                        entry["total_ms"],
                        entry["avg_ms_per_item"],
                    )
                )
        except Exception as e:
            print(
                f"[WARN] Failed to parse JSON benchmark file: {e}. "
                "Trying legacy plain-text parser..."
            )
            is_json = False

    if not is_json:
        # Fallback: legacy plain-text parsing
        with open(input_file) as f:
            text = f.read()
        pattern = re.compile(
            r"(Serial|Thread|Process): (\d+) items in ([\d.]+)s "
            r".*?avg: ([\d.]+) ms/item"
        )
        matches = pattern.findall(text)
        # matches: List[Tuple[mode, n, total, avg]]
        for m in matches:
            mode, n, total, avg = m
            results.append(
                (
                    mode,
                    None,
                    float(total) * 1000,
                    float(avg),
                )
            )

    if not results:
        print("No benchmark results found.")
        sys.exit(1)

    # Find the fastest (lowest avg_ms_per_item)
    fastest = min(results, key=lambda r: float(r[3]))
    mode, method, total_ms, avg = fastest
    label_val = (
        label if label is not None else (f"{mode.lower()}" if mode else "benchmark")
    )
    message_val = message if message is not None else f"{float(avg):.2f}ms"
    avg_val = float(avg)
    if avg_val < threshold_green:
        color = color_green
    elif avg_val < threshold_yellow:
        color = color_yellow
    else:
        color = color_red
    _write_badge(label_val, message_val, color, output_file, dry_run=dry_run)


def generate_mutation_badge(
    input_file: str,
    output_file: str,
    threshold_green: float = 90.0,
    threshold_yellow: float = 75.0,
    color_green: str = "brightgreen",
    color_yellow: str = "yellow",
    color_red: str = "red",
    label: str | None = None,
    message: str | None = None,
    dry_run: bool = False,
) -> None:
    """Generate a Shields.io badge for mutation testing score.

    Args:
        input_file: Path to mutmut_cache file.
        output_file: Path to output SVG badge file.
        threshold_green: Score (%) for green badge color.
        threshold_yellow: Score (%) for yellow badge color.
        color_green: Badge color for high score (default: 'brightgreen').
        color_yellow: Badge color for medium score (default: 'yellow').
        color_red: Badge color for low score (default: 'red').
        label: Custom badge label (overrides default if set).
        message: Custom badge message (overrides default if set).
        dry_run: If True, print badge info instead of writing file.

    """
    with open(input_file) as f:
        data = f.read()
    survived = 0
    killed = 0
    for line in data.splitlines():
        if line.startswith("SURVIVED:"):
            survived = int(line.split(":")[1].strip())
        elif line.startswith("KILLED:"):
            killed = int(line.split(":")[1].strip())
    if killed + survived == 0:
        score = 100.0
    else:
        score = 100.0 * killed / (killed + survived)
    label_val = label if label is not None else "mutation"
    if score >= threshold_green:
        color = color_green
    elif score >= threshold_yellow:
        color = color_yellow
    else:
        color = color_red
    message_val = message if message is not None else f"{score:.1f}%"
    _write_badge(label_val, message_val, color, output_file, dry_run=dry_run)


def _write_badge(
    label: str,
    message: str,
    color: str,
    output_file: str,
    dry_run: bool = False,
) -> None:
    """Fetch a Shields.io badge and write it to a file, or print info in dry-run mode.

    Args:
        label: Badge label (left side).
        message: Badge message (right side).
        color: Badge color (e.g., 'brightgreen', 'yellow', 'red').
        output_file: Path to output SVG badge file.
        dry_run: If True, print badge URL and params instead of fetching/writing.

    """
    url = f"https://img.shields.io/badge/{urllib.parse.quote(label)}-{urllib.parse.quote(message)}-{color}.svg"
    if dry_run:
        print("[DRY-RUN] Would fetch badge:")
        print(f"  Label:   {label}")
        print(f"  Message: {message}")
        print(f"  Color:   {color}")
        print(f"  Output:  {output_file}")
        print(f"  URL:     {url}")
        return
    resp = requests.get(url)
    if resp.status_code == 200:
        with open(output_file, "wb") as out:
            out.write(resp.content)
        print(f"Badge written to {output_file}")
    else:
        print(f"Failed to fetch badge from {url}")
        sys.exit(1)


def main() -> None:
    """Parse CLI arguments and generate the requested badge."""
    parser = argparse.ArgumentParser(
        description="Unified badge generator for benchmark and mutation testing."
    )
    parser.add_argument(
        "--type",
        required=True,
        choices=["benchmark", "mutation"],
        help="Type of badge to generate",
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input file (benchmark log or mutmut_cache)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output SVG badge file",
    )
    # Custom thresholds/colors for benchmark badges
    parser.add_argument(
        "--benchmark-threshold-green",
        type=float,
        default=0.05,
        help="Score (ms) for green badge color [benchmark]",
    )
    parser.add_argument(
        "--benchmark-threshold-yellow",
        type=float,
        default=0.10,
        help="Score (ms) for yellow badge color [benchmark]",
    )
    parser.add_argument(
        "--benchmark-color-green",
        type=str,
        default="brightgreen",
        help="Color for green badge [benchmark]",
    )
    parser.add_argument(
        "--benchmark-color-yellow",
        type=str,
        default="yellow",
        help="Color for yellow badge [benchmark]",
    )
    parser.add_argument(
        "--benchmark-color-red",
        type=str,
        default="red",
        help="Color for red badge [benchmark]",
    )
    parser.add_argument(
        "--benchmark-label",
        type=str,
        default=None,
        help="Custom badge label for benchmark badge",
    )
    parser.add_argument(
        "--benchmark-message",
        type=str,
        default=None,
        help="Custom badge message for benchmark badge",
    )
    # Custom thresholds/colors for mutation badges
    parser.add_argument(
        "--mutation-threshold-green",
        type=float,
        default=90.0,
        help="Score (%) for green badge color [mutation]",
    )
    parser.add_argument(
        "--mutation-threshold-yellow",
        type=float,
        default=75.0,
        help="Score (%) for yellow badge color [mutation]",
    )
    parser.add_argument(
        "--mutation-color-green",
        type=str,
        default="brightgreen",
        help="Color for green badge [mutation]",
    )
    parser.add_argument(
        "--mutation-color-yellow",
        type=str,
        default="yellow",
        help="Color for yellow badge [mutation]",
    )
    parser.add_argument(
        "--mutation-color-red",
        type=str,
        default="red",
        help="Color for red badge [mutation]",
    )
    parser.add_argument(
        "--mutation-label",
        type=str,
        default=None,
        help="Custom badge label for mutation badge",
    )
    parser.add_argument(
        "--mutation-message",
        type=str,
        default=None,
        help="Custom badge message for mutation badge",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print badge URL and parameters instead of writing badge file",
    )
    args = parser.parse_args()

    if args.type == "benchmark":
        generate_benchmark_badge(
            args.input,
            args.output,
            threshold_green=args.benchmark_threshold_green,
            threshold_yellow=args.benchmark_threshold_yellow,
            color_green=args.benchmark_color_green,
            color_yellow=args.benchmark_color_yellow,
            color_red=args.benchmark_color_red,
            label=args.benchmark_label,
            message=args.benchmark_message,
            dry_run=args.dry_run,
        )
    elif args.type == "mutation":
        generate_mutation_badge(
            args.input,
            args.output,
            threshold_green=args.mutation_threshold_green,
            threshold_yellow=args.mutation_threshold_yellow,
            color_green=args.mutation_color_green,
            color_yellow=args.mutation_color_yellow,
            color_red=args.mutation_color_red,
            label=args.mutation_label,
            message=args.mutation_message,
            dry_run=args.dry_run,
        )
    else:
        parser.error("Unknown badge type")


if __name__ == "__main__":
    main()
