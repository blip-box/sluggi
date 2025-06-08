# Command-Line Interface (CLI)

Use `sluggi` from your terminal for fast, flexible slug generation—single or batch, with full Unicode and emoji support.

!!! info
    - **Need help?** See the [FAQ & Troubleshooting](faq.md) for CLI errors, platform notes, and more.

---

## Installation

Install with CLI support:

```bash
pip install .[cli]
# Or from PyPI (if published):
# pip install "sluggi[cli]"
```

---

## Commands Overview

- `sluggi slug <text>`
  Slugify a single string (or use `--input` for file/stdin).
- `sluggi batch --input <file>`
  Batch slugify lines from a file or stdin, with parallel options.
- `sluggi bench`
  Benchmark sluggi vs. other slugifiers.
- `sluggi info`
  Show version, platform, and shell completion info.

---

## Common Options

- `--separator, -s` — Set word separator (default: `-`)
- `--custom-map` — Custom mapping as JSON (e.g. '{"ä": "ae"}')
- `--max-length, -m` — Truncate slug to max length
- `--stopwords` — Comma-separated words to exclude
- `--process-emoji/--no-process-emoji` — Emoji-to-name conversion (default: off)
- `--no-lowercase` — Preserve capitalization
- `--output, -o` — Write result(s) to file
- `--parallel` (batch) — Enable parallel processing
- `--mode` (batch) — 'thread', 'process', or 'serial'
- `--workers` (batch) — Number of worker threads/processes

For all options, run `sluggi <command> --help`.

---

## Examples

**Single string:**
```bash
sluggi slug "Café déjà vu!"
sluggi slug "Привет мир" --separator _
sluggi slug --input input.txt --output slug.txt
```

**Batch:**
```bash
sluggi batch --input names.txt --output slugs.txt
cat names.txt | sluggi batch --parallel --mode process
```

**Benchmark:**
```bash
sluggi bench
```

**Info:**
```bash
sluggi info
```

!!! info "Stdin, stdout, emoji, and shell completion"
    - Omit `<text>` or `--input` to read from stdin (e.g. `echo ... | sluggi slug`).
    - Use `--output` to write results to a file, or omit for stdout.
    - Emoji are converted to names with `--process-emoji`; disable for speed.
    - For shell completion, see `sluggi info` and Typer docs.

---

See the [Usage](usage.md) and [API Reference](api.md) for Python examples and advanced options.

For CLI-specific issues and limitations, check the [FAQ & Troubleshooting](faq.md).
