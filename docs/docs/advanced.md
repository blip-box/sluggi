# Advanced Topics

Unlock maximum performance and flexibility with sluggi’s advanced features for batch, async, parallel, and custom mapping.

!!! info "See also"
    - [FAQ & Troubleshooting](faq.md) for edge cases, platform notes, and known limitations.

---

## Batch and Async Performance

- Use `parallel=True` for large batches.
- `mode="process"` for CPU-bound work, `mode="thread"` for I/O-bound or cached inputs.
- Tune `workers` and `chunk_size` for your workload.
- Async batch uses a semaphore to avoid event loop starvation.

!!! tip "CLI parallelism"
    All these options are available from the CLI as well (see [CLI docs](cli.md)).

---

## Custom Emoji Mapping

You can extend or override emoji mappings:

```python
from sluggi import slugify
emoji_map = {"😀": "smile", "🔥": "fire"}
slug = slugify("Hello 😀🔥", custom_map=emoji_map)
print(slug)  # hello-smile-fire
```

---

## Batch Slugification: Custom Chunk Size & Error Handling

Handle errors and tune chunk size for large jobs:

```python
from sluggi import batch_slugify
try:
    slugs = batch_slugify(["foo", "bar", None], chunk_size=2)
except TypeError as e:
    print(f"Error: {e}")
```

---

## Async Slugification in FastAPI

Integrate async batch slugification into a web API:

```python
from fastapi import FastAPI
from sluggi import async_batch_slugify

app = FastAPI()

@app.post("/bulk-slugify")
async def bulk_slugify(payload: list[str]):
    return await async_batch_slugify(
        payload,
        parallel=True,
        workers=8,
    )
```

---

## Parallel Processing Benchmarks

Compare thread vs. process mode for large batches:

```python
import time
from sluggi import batch_slugify

texts = ["foo"] * 10000

start = time.time()
batch_slugify(
    texts,
    parallel=True,
    mode="thread",
    workers=4,
)
print("Threaded:", time.time() - start)

start = time.time()
batch_slugify(
    texts,
    parallel=True,
    mode="process",
    workers=4,
)
print("Process:", time.time() - start)
```

---

## Caching

- **Thread mode:** Enables result caching for repeated inputs.
- **Process mode:** Disables cache (each process is isolated).

---

## When to Use Which Mode

- **Serial:** Small batches, low latency.
- **Parallel:** Large batches, heavy CPU work.
- **Async:** For async web frameworks or high concurrency.

!!! info "See also"
    - [API Reference](api.md) for all arguments and options.
    - [CLI docs](cli.md) for command-line usage.
    - [FAQ & Troubleshooting](faq.md) for advanced issues, platform notes, and limitations.
