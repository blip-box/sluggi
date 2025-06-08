# scripts/ — Benchmarking, Profiling, and Automation Utilities

This directory contains all utility scripts for benchmarking, profiling, mutation testing, and badge generation in the Sluggi project. All scripts are designed to be agent- and human-friendly, CI-compatible, and easy to extend.

---

## Unified Scripts

### 1. `run_benchmarks.py` and `run_profiler.py`
Modern, modular scripts for benchmarking and profiling Sluggi and competitor libraries.

**Features:**
- Benchmark `sluggi` and `python-slugify` with flexible pipeline step control (`run_benchmarks.py`)
- Output results as a pretty table or machine-readable JSON (`--json`)
- Profile with `cProfile`, memory profiling, or pipeline step timing (`run_profiler.py`)
- All scripts use argparse, type hints, and docstrings for clarity and automation

**Benchmarking notes:**
- By default, synthetic data is ASCII-only and may not trigger emoji or transliteration steps. For realistic benchmarks, use `--synthetic-mixed` or provide a real-world input file.
- "Batch" mode is implemented as a loop over single-item calls (not a vectorized batch), so batch and single timings are nearly identical.
- For long, mixed-content strings, both `sluggi` and `python-slugify` show similar performance, especially when transliteration is enabled.

**Example usage:**
```sh
# Benchmark with synthetic data, pretty table output
python scripts/run_benchmarks.py --n 1000 --length 40

# Benchmark with JSON output for automation
python scripts/run_benchmarks.py --n 1000 --length 40 --json

# Benchmark with long, mixed-content synthetic strings (realistic, heavy-load test)
python scripts/run_benchmarks.py --n 10000 --length 400 --synthetic-mixed

# Profile cProfile and save to file
python scripts/run_profiler.py --profile cprofile --outfile profile.prof --library sluggi

# Profile memory usage
python scripts/run_profiler.py --profile memory --library sluggi

# Profile pipeline steps
python scripts/run_profiler.py --profile steps --library sluggi

# (Note: --library is required for all profiling modes. Use --profile and --outfile as shown above for run_profiler.py)
```

---

### 2. `generate_badge.py`
Unified badge generator for benchmarks and mutation testing. Fetches a Shields.io badge based on your results. Highly agent/automation friendly.

**New Features:**
- Custom thresholds/colors for badge coloring (e.g., `--benchmark-threshold-green`, `--mutation-color-red`)
- Custom badge label/message (e.g., `--benchmark-label`, `--mutation-message`)
- `--dry-run` mode for CI debugging (prints badge URL and params, does not fetch/write)

**Example usage:**
```sh
# Generate a benchmark badge (default colors/labels)
python scripts/generate_badge.py --type benchmark --input benchmark.log --output benchmark-badge.svg

# Generate a mutation badge with custom label and color thresholds
python scripts/generate_badge.py --type mutation --input mutmut_cache --output mutmut-badge.svg \
  --mutation-label "Mutation Score" --mutation-threshold-green 95 --mutation-color-green "#4c1"

# Dry run (CI/automation): print badge info only
python scripts/generate_badge.py --type benchmark --input benchmark.log --output badge.svg --dry-run
```

---

### 3. `check_mutmut_threshold.py`
Checks mutation testing results and fails CI if the mutation score is below your threshold. Modern argparse CLI, agent/automation friendly.

**Example usage:**
```sh
python scripts/check_mutmut_threshold.py --threshold 90 --cache mutmut_cache
```

---

### 4. `debug_pipeline_steps.py`
Prints the output after each step in the Sluggi pipeline for a given input string. Useful for debugging and understanding transformations.

**Example usage:**
```sh
python scripts/debug_pipeline_steps.py
```

---

## Notes
- All scripts are designed for both autonomous agents and human contributors.
- Scripts are intended to be run directly, but can be imported as modules for further automation.
- For advanced usage, see inline docstrings and CLI help (`--help`).

---

For any questions, see the main project README or open an issue/PR!
