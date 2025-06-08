# API Reference

This page documents all core functions and options in `sluggi`.
See [Usage](usage.md) for practical examples and [Advanced](advanced.md) for performance tips.

---

## `slugify`

```python
def slugify(
    text: str,
    separator: str = "-",
    custom_map: Optional[Dict[str, str]] = None,
) -> str
```
Converts a string to a clean, URL-safe slug.

**Parameters:**
- `text` (`str`): Input string to slugify.
- `separator` (`str`): Separator character (default: `-`).
- `custom_map` (`dict`, optional): Custom character mappings (e.g., `{"ä": "ae"}`).

**Returns:** `str` — slugified string
**Raises:** `TypeError` if input is not a string.

**Example:**
```python
slugify("Hello, world!")  # "hello-world"
```

---

## `batch_slugify`

```python
def batch_slugify(
    texts: Iterable[str],
    separator: str = "-",
    custom_map: Optional[Dict[str, str]] = None,
    parallel: bool = False,
    workers: Optional[int] = None,
    mode: str = "thread",
    chunk_size: int = 1000,
    cache_size: int = 2048,
) -> List[str]
```
Efficiently slugifies a batch of strings, with optional parallel processing.

**Parameters:**
- `texts` (`Iterable[str]`): List or iterable of strings to slugify.
- `separator` (`str`): Separator character.
- `custom_map` (`dict`, optional): Custom character mappings.
- `parallel` (`bool`): Enable parallel processing (default: `False`).
- `workers` (`int`, optional): Number of worker threads/processes.
- `mode` (`str`): `"thread"`, `"process"`, or `"serial"`.
- `chunk_size` (`int`): Batch size for each parallel worker.
- `cache_size` (`int`): LRU cache size for thread mode.

**Returns:** `List[str]` — slugified strings
**Raises:** `TypeError` if input is not iterable or contains non-strings.

**Example:**
```python
batch_slugify(["Hello, world!", "Привет мир"])  # ["hello-world", "privet-mir"]
```

---

## `async_slugify`

```python
async def async_slugify(
    text: str,
    separator: str = "-",
    custom_map: Optional[Dict[str, str]] = None,
) -> str
```
Async version of `slugify`.

**Parameters:** Same as `slugify`.
**Returns:** `str` — slugified string
**Raises:** `TypeError` if input is not a string.

**Example:**
```python
await async_slugify("Hello, world!")  # "hello-world"
```

---

## `async_batch_slugify`

```python
async def async_batch_slugify(
    texts: Iterable[str],
    separator: str = "-",
    custom_map: Optional[Dict[str, str]] = None,
    parallel: bool = False,
    workers: Optional[int] = None,
    mode: str = "thread",
    chunk_size: int = 1000,
    cache_size: int = 2048,
) -> List[str]
```
Async version of `batch_slugify`. Accepts the same arguments and returns a list of slugified strings.

**Raises:** `TypeError` if input is not iterable or contains non-strings.

**Example:**
```python
await async_batch_slugify(["Hello, world!", "Привет мир"])
```

---

## Exceptions & Edge Cases

- All functions raise `TypeError` if inputs are of the wrong type.
- `batch_slugify` and `async_batch_slugify` skip empty inputs and preserve order.
- Custom mappings can override Unicode or emoji transliteration.
- For large batches, tune `workers` and `chunk_size` for optimal performance.

!!! info "See also"
    - [Usage](usage.md) for more examples.
    - [Advanced](advanced.md) for performance and customization tips.
