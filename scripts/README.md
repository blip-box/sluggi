# scripts/

Utility scripts that are not part of the package. Run them from the
repository root with `uv run python scripts/<name>.py`; they need the `dev`
and `cli` extras (`uv sync --all-extras`).

## `run_benchmarks.py`

Benchmarks `sluggi` against `python-slugify` on synthetic or real input, in
serial, thread and process modes. The figures in the README come from:

```sh
uv run python scripts/run_benchmarks.py --n 20000 --length 40 --mode all
```

- `--json` prints machine-readable results; `--json-summary` also writes
  `benchmark.json`.
- Synthetic input is ASCII by default, which never reaches the emoji or
  transliteration steps. Use `--synthetic-mixed`, or pass a real input file,
  for a realistic run.
- Batch mode loops over single calls rather than vectorising, so batch and
  single timings are close.

For a quick figure without the comparison, the CLI has `sluggi bench`.

## `run_profiler.py`

Profiles one library (`--library sluggi` or `--library python-slugify`) with
cProfile (`--profile cprofile --outfile profile.prof`), by memory
(`--profile memory`), or per pipeline step (`--profile steps`).

## `debug_pipeline_steps.py`

Prints the text after each step of the slugification pipeline for a given
input, which is the quickest way to see which step changed what.

## `release_notes.py`

Prints the `CHANGELOG.md` section for a tag, for the release workflow to use
as the GitHub release notes: `python3 scripts/release_notes.py v0.1.2`. It
fails when the tag has no section, which is what makes a release without a
changelog entry impossible. `tests/test_release_notes.py` covers it.
