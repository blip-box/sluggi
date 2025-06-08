# Usage

Get started using `sluggi` in your Python projects or from the command line—sync, async, and with custom options.

!!! info
    - **Having trouble?** See the [FAQ & Troubleshooting](faq.md) for common issues and solutions.

---

## CLI Quickstart

```bash
sluggi slug "Hello, world!"
# hello-world

echo "Café au lait" | sluggi slug --process-emoji
# cafe-au-lait
```

See the [CLI docs](cli.md) for all commands and options.

---

## Python API

### Basic Usage

```python
from sluggi import slugify, batch_slugify

slug = slugify("Hello, world!")
print(slug)  # hello-world

slugs = batch_slugify(["Hello, world!", "Привет мир"])
print(slugs)  # ['hello-world', 'privet-mir']
```

### Async Usage

```python
import asyncio
from sluggi import async_slugify, async_batch_slugify

async def main():
    slug = await async_slugify("Hello, world!")
    slugs = await async_batch_slugify(
        ["Hello, world!", "Привет мир"],
        parallel=True,
    )
    print(slug, slugs)

asyncio.run(main())
```

### Custom Separator and Mapping

```python
slug = slugify("Hello, world!", separator="_")
print(slug)  # hello_world

slug = slugify(
    "ä ö ü",
    custom_map={
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
    },
)
print(slug)  # ae-oe-ue
```

---

!!! info "Troubleshooting & Unicode"
    - For best results with Unicode and emoji, ensure your terminal and editor use UTF-8.
    - On Windows, set `PYTHONUTF8=1` if you see encoding issues.

---

## Error Handling

- All slugification functions raise `TypeError` for invalid input types.
- The CLI prints helpful errors for invalid files, options, or mappings.

---

See the [API Reference](api.md) for all available options and advanced usage.

For common problems, platform notes, and limitations, check the [FAQ & Troubleshooting](faq.md).
