# sluggi

**sluggi** — The modern, blazing-fast Python library and CLI for turning any text into clean, URL-safe slugs.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/sluggi.svg?logo=pypi)](https://pypi.org/project/sluggi/)
[![CI](https://github.com/blip-box/sluggi/actions/workflows/ci.yml/badge.svg)](https://github.com/blip-box/sluggi/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/blip-box/sluggi/branch/main/graph/badge.svg)](https://codecov.io/gh/blip-box/sluggi)
[![Python Version](https://img.shields.io/pypi/pyversions/sluggi.svg)](https://pypi.org/project/sluggi/)
[![Changelog](https://img.shields.io/badge/changelog-md-blue)](https://github.com/blip-box/sluggi/releases)



> Inspired by slugify, reimagined for speed, Unicode, and robust parallel batch processing.

---

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Advanced Usage & Performance Tips](#advanced-usage--performance-tips)
- [Command-Line Interface (CLI)](#command-line-interface-cli)
- [Development & Contributing](#development--contributing)
- [Performance & Benchmarks](#performance--benchmarks)
- [License](#license)
- [See Also](#see-also)

---

## Features
- 🚀 **Fast:** Optimized for speed with minimal dependencies.
- 🌍 **Unicode & Emoji:** Handles dozens of scripts, emoji, and edge cases out of the box.
- 🔧 **Customizable:** Define your own character mappings and rules.
- 🧵 **Parallel Batch:** True multi-core batch slugification (thread/process/serial modes).
- ⚡ **Async Support:** Full asyncio-compatible API for modern Python apps.
- 🖥️ **CLI Tool:** Powerful, colorized CLI for quick slug generation and batch jobs.
- 🔒 **Safe Output:** Always generates URL-safe, predictable slugs.
- 🧩 **Extensible API:** Easy to use and extend.
- ✅ **CI & Pre-commit:** Linting, formatting, and tests run automatically.

## Modular Slugification Pipeline

sluggi processes text through a modular pipeline of single-responsibility functions, making the codebase more readable, maintainable, and extensible. Each step in the pipeline performs a distinct transformation, allowing for easy customization and extension.

**Pipeline Steps:**

1. **normalize_unicode(text)**
   Normalize Unicode characters to a canonical form (NFKC).
2. **decode_html_entities_and_refs(text)**
   Decode HTML entities and character references to their Unicode equivalents.
3. **convert_emojis(text)**
   Replace emojis with their textual representations.
4. **transliterate_text(text)**
   Transliterate non-ASCII characters to ASCII (where possible).
5. **apply_custom_replacements(text, custom_map)**
   Apply user-defined or staged character/string replacements.
6. **extract_words(text, word_regex)**
   Extract words using a customizable regex pattern.
7. **filter_stopwords(words, stopwords)**
   Remove unwanted words (e.g., stopwords) from the list.
8. **join_words(words, separator)**
   Join words using the specified separator.
9. **to_lowercase(text, lowercase)**
   Convert the result to lowercase if requested.
10. **strip_separators(text, separator)**
    Remove leading/trailing separators.
11. **smart_truncate(text, max_length, separator)**
    Optionally truncate the slug at a word boundary.

**Processing Flow:**

    Input Text
      ↓
    normalize_unicode
      ↓
    decode_html_entities_and_refs
      ↓
    convert_emojis
      ↓
    transliterate_text
      ↓
    apply_custom_replacements
      ↓
    extract_words
      ↓
    filter_stopwords
      ↓
    join_words
      ↓
    to_lowercase
      ↓
    strip_separators
      ↓
    smart_truncate
      ↓
    Final Slug

This modular approach makes it easy to add, remove, or modify steps in the pipeline. Each function is pure and well-documented. See the API docs and source for details on customizing or extending the pipeline.

## Installation
Install from PyPI:
```bash
pip install sluggi
```

For CLI and development:
```bash
pip install .[cli,dev]
```

## Usage
```python
from sluggi import slugify, batch_slugify

slug = slugify("Hello, world!")
print(slug)  # hello-world

# Batch processing (parallel by default)
slugs = batch_slugify(["Hello, world!", "Привет мир"])
print(slugs)  # ['hello-world', 'privet-mir']

# Advanced: Parallel processing
slugs = batch_slugify(["foo", "bar"], parallel=True, mode="process", workers=2)

# Stopwords (exclude common words from slugs)
slug = slugify("The quick brown fox jumps", stopwords=["the", "fox"])
print(slug)  # quick-brown-jumps

slugs = batch_slugify([
    "The quick brown fox jumps",
    "Jump over the lazy dog"
], stopwords=["the", "over", "dog"])
print(slugs)  # ['quick-brown-fox-jumps', 'jump-lazy']

# Custom regex pattern for word extraction (e.g., only extract capitalized words)
slug = slugify("The Quick Brown Fox", word_regex=r"[A-Z][a-z]+")
print(slug)  # The-Quick-Brown-Fox

# Use in batch_slugify
slugs = batch_slugify([
    "The Quick Brown Fox",
    "Jump Over The Lazy Dog"
], word_regex=r"[A-Z][a-z]+")
print(slugs)  # ['The-Quick-Brown-Fox', 'Jump-Over-The-Lazy-Dog']
```

### Async Usage
Requires Python 3.7+
```python
import asyncio
from sluggi import async_slugify, async_batch_slugify

async def main():
    slug = await async_slugify("Hello, world!")
    slugs = await async_batch_slugify(["Hello, world!", "Привет мир"], parallel=True)
    print(slug)   # hello-world
    print(slugs)  # ['hello-world', 'privet-mir']

asyncio.run(main())
```

### Custom Separator
```python
slug = slugify("Hello, world!", separator="_")
print(slug)  # hello_world
```

### Stopwords
```python
slug = slugify("The quick brown fox", stopwords=["the", "fox"])
print(slug)  # quick-brown
```

### Custom Mapping
```python
slug = slugify("ä ö ü", custom_map={"ä": "ae", "ö": "oe", "ü": "ue"})
print(slug)  # ae-oe-ue
```

---

## API Reference

### `slugify`

| Argument      | Type           | Default   | Description                                                                 |
|---------------|----------------|-----------|-----------------------------------------------------------------------------|
| text          | str            | —         | The input string to slugify.                                                |
| separator     | str            | "-"      | Word separator in the slug.                                                 |
| custom_map    | dict           | None      | Custom character mappings.                                                  |
| stopwords     | Iterable[str]  | None      | Words to exclude from the slug (case-insensitive if `lowercase=True`).      |
| lowercase     | bool           | True      | Convert result to lowercase.                                                |
| word_regex    | str            | None      | Custom regex pattern for word extraction (default: `r'\w+'`).              |
| process_emoji | bool           | True      | If `False`, disables emoji-to-name conversion for max performance.          |

**Returns:** `str` (slugified string)

**Example:**
```python
slug = slugify("The quick brown fox", stopwords=["the", "fox"])
print(slug)  # quick-brown
```

---

### `batch_slugify`

| Argument      | Type           | Default      | Description                                                         |
|---------------|----------------|--------------|---------------------------------------------------------------------|
| texts         | Iterable[str]  | —            | List of strings to slugify.                                         |
| separator     | str            | "-"         | Word separator in the slug.                                         |
| custom_map    | dict           | None         | Custom character mappings.                                          |
| stopwords     | Iterable[str]  | None         | Words to exclude from slugs.                                        |
| lowercase     | bool           | True         | Convert result to lowercase.                                        |
| word_regex    | str            | None         | Custom regex pattern for word extraction (default: `r'\w+'`).      |
| parallel      | bool           | False        | Enable parallel processing.                                         |
| workers       | int            | None         | Number of parallel workers.                                         |
| mode          | str            | "thread"    | "thread", "process", or "serial".                                 |
| chunk_size    | int            | 1000         | Number of items per worker chunk.                                   |
| cache_size    | int            | 2048         | Size of the internal cache.                                         |

**Returns:** `List[str]` (list of slugified strings)

**Example:**
```python
slugs = batch_slugify(["The quick brown fox", "Jumped over the lazy dog"])
print(slugs)  # ['quick-brown', 'jumped-over-the-lazy-dog']
```

### `async_slugify(text, separator="-", custom_map=None)`
- Same as `slugify`, but async.

### `async_batch_slugify(texts, ...)`
- Same as `batch_slugify`, but async.

---

## Advanced Usage & Performance Tips

### Skipping Emoji Handling for Maximum Speed
- By default, sluggi converts emoji to their textual names (e.g., 😎 → smiley-face) for maximum compatibility and searchability.
- **For maximum performance**, you can disable emoji handling entirely if you do not need emoji-to-name conversion. This avoids all emoji detection and replacement logic, providing a measurable speedup for emoji-heavy or large datasets.
- To disable emoji handling:
  - **Python API:** Pass `process_emoji=False` to `slugify`, `batch_slugify`, or any pipeline config.
  - **CLI:** Add the `--no-process-emoji` flag to your command.

**Example:**
```python
slug = slugify("emoji: 😎🤖🎉", process_emoji=False)
print(slug)  # emoji
```

```bash
sluggi slug "emoji: 😎🤖🎉" --no-process-emoji
# Output: emoji
```

### Batch and Async Performance
- **Parallel Processing:**
  - For large batches, use `parallel=True` and tune `workers` and `chunk_size`.
  - `mode="process"` enables true CPU parallelism for CPU-bound workloads.
  - `mode="thread"` is best for I/O-bound or repeated/cached inputs.
- **Caching:**
  - Threaded mode enables slugification result caching for repeated or overlapping inputs.
  - Process mode disables cache (each process is isolated).
- **Asyncio:**
  - Use `async_batch_slugify` for async web servers or event-driven apps.
  - The `parallel` option with async batch uses a semaphore to limit concurrency, avoiding event loop starvation.
  - For best throughput, set `workers` to your CPU count or the number of concurrent requests you expect.

#### Example: Tuning Batch Processing
```python
# Large batch, CPU-bound: use process pool
slugs = batch_slugify(my_list, parallel=True, mode="process", workers=8, chunk_size=500)

# Async batch in a web API (FastAPI, Starlette, etc.)
from sluggi import async_batch_slugify

@app.post("/bulk-slugify")
async def bulk_slugify(payload: list[str]):
    return await async_batch_slugify(payload, parallel=True, workers=8)
```

### When to Use Serial vs Parallel vs Async
- **Serial:** Small batches, low latency, or single-threaded environments.
- **Parallel (thread/process):** Large batches, heavy CPU work, or when maximizing throughput is critical.
- **Async:** Integrate with modern async web frameworks, handle many concurrent requests, or avoid blocking the event loop.

See the docstrings and API reference for more details on each option.

## Command-Line Interface (CLI)

Install CLI dependencies:
```bash
pip install .[cli]
```

### Quick Start
```bash
sluggi slug "Γειά σου Κόσμε"
# Output: geia-sou-kosme

sluggi slug "The quick brown fox jumps" --stopwords "the,fox"
# Output: quick-brown-jumps

sluggi slug "The Quick Brown Fox" --word-regex "[A-Z][a-z]+"
# Output: The-Quick-Brown-Fox

sluggi slug "The Quick Brown Fox" --no-lowercase
# Output: The-Quick-Brown-Fox

sluggi batch --input names.txt --output slugs.txt
sluggi batch --input names.txt --word-regex "[A-Z][a-z]+" --no-lowercase

# Custom output formatting in batch mode:
sluggi batch --input names.txt --output-format "{line_num}: {original} -> {slug}"
# Output example:
# 1: Foo Bar -> foo-bar
# 2: Baz Qux -> baz-qux

sluggi batch --input names.txt --output-format "{slug}"
# Output: just the slug, as before

# Display results as a rich table in the console:
sluggi batch --input names.txt --display-output
# Output example (with rich):
# ┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━┓
# ┃ row_number ┃ original     ┃ slug     ┃
# ┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━┩
# │ 1          │ Foo Bar      │ foo-bar  │
# │ 2          │ Baz Qux      │ baz-qux  │
# └────────────┴──────────────┴──────────┘
```

**Supported placeholders for --output-format:**
- `{slug}`: The generated slug
- `{original}`: The original input line
- `{line_num}`: The 1-based line number

**Note:** The `--display-output` table uses the [rich](https://github.com/Textualize/rich) Python library. If not installed, a plain text table will be shown instead.

### CLI Options

| Option           | Description                                                      |
|------------------|------------------------------------------------------------------|
| `--separator`    | Separator for words in the slug (default: `-`).                 |
| `--stopwords`    | Comma-separated words to exclude from slug.                     |
| `--custom-map`   | Custom mapping as JSON, e.g. `'{"ä": "ae"}'`.                |
| `--word-regex`   | Custom regex pattern for word extraction (default: `\w+`).     |
| `--no-lowercase` | Preserve capitalization in the slug (default: False).           |
| `--output-format`| Custom output format for batch mode. Supports `{slug}`, `{original}`, `{line_num}`. Default: just the slug. |
| `--display-output`| Display results as a rich table in the console after batch processing. |


### CLI Help
```bash
sluggi --help
```

### Error Handling Example
```bash
sluggi batch --input missing.txt
# Output:
[bold red]Input file not found: missing.txt[/bold red]
```

## Development & Contributing

- Clone the repo:
  ```bash
  git clone https://github.com/blip-box/sluggi.git
  cd sluggi
  ```
- Create a virtual environment and install dependencies using uv:
  ```bash
  uv venv
  uv pip install .[dev,cli]
  ```
- Run tests and lints:
  ```bash
  pytest
  ruff src/sluggi tests
  black --check src/sluggi tests
  ```
- Pre-commit hooks:
  ```bash
  pre-commit install
  pre-commit run --all-files
  ```
- PRs and issues welcome!

## Encoding Notes
- Input and output files must be UTF-8 encoded.
- On Windows, use a UTF-8 capable terminal or set the environment variable `PYTHONUTF8=1` if you encounter encoding issues.

### Help and Examples
- Run `sluggi --help` or any subcommand with `--help` to see detailed usage and examples directly in your terminal.

---

## Performance & Benchmarks

Batch slugification performance was measured using the included benchmark script:

```bash
python scripts/benchmark_batch.py
```

**Results on 20,000 random strings:**

| Mode     | Time (s) | Avg ms/item |
|----------|----------|-------------|
| Serial   | 0.74     | 0.037       |
| Thread   | 0.62–0.72| 0.031–0.036 |
| Process  | 1.55–1.73| 0.078–0.086 |

- **Serial** is fast and reliable for most workloads.
- **Thread** mode may be slightly faster for I/O-bound or lightweight CPU tasks (default for --parallel).
- **Process** mode (multiprocessing) enables true CPU parallelism, but has higher overhead and is best for very CPU-bound or expensive slugification tasks.
- Use `--mode process` for multiprocessing, `--mode thread` for threads, or `--mode serial` for no parallelism. Combine with `--workers` to tune performance.

**Script location:** `scripts/benchmark_batch.py`

### Shell Completion
Enable tab-completion for your shell (bash, zsh, fish):
```bash
sluggi completion bash   # or zsh, fish
# Follow the printed instructions to enable completion in your shell
```

## License
MIT

---

[Changelog]([GitHub Releases](https://github.com/blip-box/sluggi/releases))

> **Note:** This project is a complete rewrite, inspired by existing slugify libraries, but aims to set a new standard for speed, correctness, and extensibility in Python.

---

### See Also

This project was inspired by the Java library [slugify by akullpp](https://github.com/akullpp/slugify). If you need Java or Gradle support, see their documentation for advanced transliteration and custom replacements.

Example (Java):
```java
final Slugify slg = Slugify.builder()
    .customReplacements(Map.of("Foo", "Hello", "bar", "world"))
    .customReplacement("Foo", "Hello")
    .customReplacement("bar", "world")
    .build();
final String result = slg.slugify("Foo, bar!");
// result: hello-world
```

For advanced transliteration in Java:
```groovy
capabilities {
    requireCapability('com.github.slugify:slugify-transliterator')
}
```
Or add the optional dependency `com.ibm.icu:icu4j` to your project.

---

✨ **New Automation & Collaboration Features**

- **Adaptive triage workflows**: Issues and PRs are now auto-labeled, parsed for agent/human status, and incomplete PRs are auto-closed for you—saving time for everyone.
- **Agent-ready templates**: All issue and PR templates are designed for both humans and autonomous agents, with structured metadata and feedback built in.
- **Playground workflow**: Safely experiment, test, or self-heal code with the new playground automation—perfect for bots and contributors alike.

See [.github/workflows/README.md](.github/workflows/README.md) for more details on these next-generation automations!
