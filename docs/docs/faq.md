# FAQ, Troubleshooting, and Limitations

This page addresses common questions, known limitations, and troubleshooting tips for using `sluggi`.

---

## Frequently Asked Questions (FAQ)

### Q: Why do I get a `TypeError` when calling `slugify` or `batch_slugify`?
A: All slugification functions require string input (or an iterable of strings for batch). Passing `None`, numbers, or other types will raise a `TypeError`.

### Q: How do I handle Unicode or emoji issues in my output?
A: Ensure your terminal and editor are set to UTF-8. On Windows, set `PYTHONUTF8=1` if you see encoding issues. All sluggi functions are Unicode-safe, but your environment must support it.

### Q: Can I customize how emoji or special characters are mapped?
A: Yes! Use the `custom_map` argument to override or extend how characters and emoji are converted. See [Advanced](advanced.md) for examples.

### Q: Why is batch slugification slow on large datasets?
A: For best performance:
- Use `parallel=True` and tune `workers` and `chunk_size`.
- Use `mode="process"` for CPU-bound, `mode="thread"` for I/O-bound jobs.
- See [Advanced](advanced.md) for benchmarks and tips.

### Q: Does sluggi work on Windows, Linux, and Mac?
A: Yes. All core features are cross-platform. For parallel batch processing, `mode="process"` uses Python's multiprocessing, which may behave differently on Windows (e.g., slower startup). If you hit issues, try `mode="thread"`.

---

## Troubleshooting

- **Unicode/emoji not displaying correctly:**
    - Set your terminal/editor to UTF-8.
    - On Windows, set `PYTHONUTF8=1` in your environment.
    - If you see question marks or boxes, your font may not support the characters.

- **CLI errors about invalid options or files:**
    - Run `sluggi <command> --help` for all available options.
    - Double-check your file paths and permissions.

- **TypeError or ValueError in Python:**
    - Ensure all inputs are strings (or iterables of strings for batch).
    - For custom mappings, use a dictionary of single-character keys to string values.

- **Performance issues with large batches:**
    - Use parallel mode and tune `workers`/`chunk_size`.
    - See [Advanced](advanced.md) for performance tuning.

---

## Known Limitations

- **Parallel processing:**
    - `mode="process"` may have higher startup cost on Windows.
    - Caching is only available in `mode="thread"`.
    - Large batches may exhaust memory if not chunked appropriately.

- **Emoji mapping:**
    - Only standard Unicode emoji are supported by default. For custom emoji or symbols, use `custom_map`.

- **Transliteration:**
    - Sluggi uses built-in transliteration for many scripts, but edge cases may exist for rare languages or symbols.

- **CLI batch mode:**
    - Input files must be UTF-8 encoded. Non-UTF-8 files may cause errors.

---

For more help, see the [Usage](usage.md), [API Reference](api.md), or open an issue on [GitHub](https://github.com/blip-box/sluggi/issues).
