"""check_mutmut_threshold.py - Modern mutation score checker for CI/agents/humans.

Checks the mutation testing score from mutmut_cache and fails CI if below threshold.

Usage:
    python scripts/check_mutmut_threshold.py --threshold 90 --cache mutmut_cache
    (defaults: --threshold 90, --cache mutmut_cache)
"""

import argparse
import sys


def parse_mutmut_cache(cache_path: str) -> tuple[int, int]:
    """Parse mutmut_cache and return (killed, survived) mutant counts."""
    killed = survived = 0
    try:
        with open(cache_path) as f:
            for line in f:
                if line.startswith("SURVIVED:"):
                    survived = int(line.split(":")[1].strip())
                elif line.startswith("KILLED:"):
                    killed = int(line.split(":")[1].strip())
    except FileNotFoundError:
        print(f"::error::Cache file '{cache_path}' not found.")
        sys.exit(1)
    return killed, survived


def main():
    """Parse CLI arguments, check mutation score, and exit with error if below
    threshold.

    This function is intended for use in CI and automation to enforce mutation
    testing quality gates.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Check mutation score from mutmut_cache and fail if below " "threshold."
        )
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=90.0,
        help="Minimum mutation score required (default: 90)",
    )
    parser.add_argument(
        "--cache",
        type=str,
        default="mutmut_cache",
        help="Path to mutmut_cache file (default: mutmut_cache)",
    )
    args = parser.parse_args()

    killed, survived = parse_mutmut_cache(args.cache)
    total = killed + survived
    if total == 0:
        print("No mutants found. Skipping threshold check.")
        sys.exit(0)
    score = 100.0 * killed / total
    print(f"Mutation score: {score:.1f}% (Threshold: {args.threshold}%)")
    if score < args.threshold:
        print(
            f"::error::Mutation score {score:.1f}% is below threshold "
            f"{args.threshold}%!"
        )
        sys.exit(1)
    else:
        print("Mutation score threshold met.")
        sys.exit(0)


if __name__ == "__main__":
    main()
