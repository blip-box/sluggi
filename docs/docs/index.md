# sluggi

> A Python library and CLI for generating clean, URL-safe slugs from any text. 20,000 strings in 0.74 seconds on the included benchmark, no runtime dependencies.

[![PyPI](https://img.shields.io/pypi/v/sluggi.svg)](https://pypi.org/project/sluggi/)
[![CI](https://github.com/blip-box/sluggi/actions/workflows/ci.yml/badge.svg)](https://github.com/blip-box/sluggi/actions/workflows/ci.yml)
[![Docs](https://github.com/blip-box/sluggi/actions/workflows/deploy-docs.yml/badge.svg)](https://blip-box.github.io/sluggi/)

- 🚀 **Fast & robust**: Optimized for performance and reliability
- 🌍 **Unicode & emoji**: Handles all languages and emoji out of the box
- 🧩 **Customizable**: Supports custom mappings, stopwords, and pipelines
- 🪄 **Batch & async**: Parallel and async slugification for large datasets
- 🖥️ **CLI & Python API**: Use from the command line or in your code

---

## Why sluggi?

sluggi outperforms legacy slugification tools with full Unicode, emoji, and async support—ideal for modern web, data, and content pipelines.

---

## Get Started

**Requirements:** Python 3.8+

Install with pip:

```bash
pip install sluggi
```

Basic usage:

```python
from sluggi import slugify
slug = slugify("Hello, world!")  # hello-world
```

---

- See [Usage](usage.md) for more examples.
- Explore the [API Reference](api.md) for all options.
- Try the [CLI](cli.md) for quick slug generation.
- Check [Advanced](advanced.md) for custom pipelines and performance tips.
- Visit the [FAQ & Troubleshooting](faq.md) for common questions and limitations.

---

sluggi is open source and maintained by [blipbox](https://github.com/blip-box).
