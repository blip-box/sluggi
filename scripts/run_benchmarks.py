#!/usr/bin/env python3
"""Benchmark sluggi vs python-slugify. Skips emoji/transliteration steps in sluggi.

Usage:
    python scripts/benchmark_vs_slugify_noemoji.py \
        --n 20000 \
        --length 40
"""

import argparse
import random
import string
import time

from sluggi import batch_slugify
from sluggi.api import SlugPipeline
from sluggi.replacements import (
    ReplacementConfig,
    ReplacementEngine,
    custom_map_to_config,
)

try:
    from python_slugify import slugify as py_slugify
except ImportError:
    try:
        from slugify import slugify as py_slugify
    except ImportError:
        raise ImportError(
            "python-slugify is not installed. Please run 'pip install python-slugify'."
        )


def random_string(length: int) -> str:
    """Generate a random alphanumeric string of given length.

    Args:
        length: Length of the string to generate.

    Returns:
        Random alphanumeric string.

    """
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_test_data(n: int, length: int = 40) -> list[str]:
    """Generate a list of n random ASCII strings, each of the specified length.

    Args:
        n: Number of strings to generate.
        length: Length of each string.

    Returns:
        List of random ASCII strings.

    """
    return [random_string(length) for _ in range(n)]


def generate_mixed_test_data(n: int, length: int = 40) -> list[str]:
    """Generate n synthetic lines, each mixing ASCII, Unicode, and emoji.

    Args:
        n: Number of strings to generate.
        length: Length of each string.

    Returns:
        List of mixed-content strings.

    """
    ascii_chars = string.ascii_letters + string.digits
    unicode_samples = [
        "é",
        "ü",
        "ç",
        "ø",
        "ß",
        "ñ",
        "å",
        "œ",
        "ž",
        "š",
        "Д",
        "Б",
        "Ж",
        "я",
        "ф",
        "ю",
        "你",
        "好",
        "世",
        "界",
        "あ",
        "い",
        "う",
        "え",
        "お",
        "日",
        "本",
        "語",
        "한",
        "글",
        "ह",
        "ि",
        "न",
        "्",
        "द",
        "ी",
        "م",
        "ر",
        "ح",
        "ب",
        "ا",
    ]
    emojis = [
        "😀",
        "😂",
        "😍",
        "👍",
        "🔥",
        "🎉",
        "🍕",
        "🍔",
        "🏆",
        "🤖",
        "😊",
        "😎",
        "🥇",
        "🚀",
        "🌟",
    ]
    all_chars = ascii_chars + "".join(unicode_samples) + "".join(emojis)
    data = []
    for _ in range(n):
        s = "".join(random.choices(all_chars, k=length))
        data.append(s)
    return data


def load_realworld_data(input_file: str = None, n: int = None) -> list[str]:
    """Load real-world test data from a file, or use a built-in diverse sample.

    Args:
        input_file: Path to input file with test strings (utf-8, one per line).
        n: Number of lines to load (optional).

    Returns:
        List of test strings.

    """
    if input_file:
        with open(input_file, encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        if n:
            lines = lines[:n]
        return lines
    # Built-in diverse sample with unicode, accents, emoji, etc
    sample = [
        "Café del Mar",
        "naïve façade coöperate soupçon",
        "Добро пожаловать",
        "中文测试",
        "Español: ¿Cómo estás?",
        "français: déjà vu",
        "日本語のテスト",
        "I love 🍕 and 🍔!",
        "smörgåsbord",
        "crème brûlée",
        "São Paulo",
        "München",
        "emoji: 😎🤖🎉",
        "مرحبا بالعالم",
        "हिन्दी भाषा",
        "Zażółć gęślą jaźń",
        "Grüß Gott!",
        "résumé",
        "coördinate",
        "touché",
        "mañana",
        "piñata",
        "über-cool",
        "façade",
        "Pokémon",
        "smile 😊",
        "中文: 你好，世界！",
        "emoji+accents: crème 🍦 brûlée",
        "🏆 Winner takes all! 🏆",
        "100% — done!",
    ]
    if n:
        return sample[:n]
    return sample


def bench_one(func: callable, data: list[str]) -> tuple[float, float]:
    """Benchmark a function on a list of inputs (single-item mode).

    Args:
        func: Function to benchmark (accepts a single string).
        data: List of input strings.

    Returns:
        Tuple of (total elapsed seconds, average ms per item).

    """
    start = time.perf_counter()
    out = [func(x) for x in data]
    elapsed = time.perf_counter() - start
    assert len(out) == len(data)
    return elapsed, elapsed / len(data) * 1000


def bench_batch(func: callable, data: list[str]) -> tuple[float, float]:
    """Benchmark a batch function on a list of inputs (batch mode).

    Args:
        func: Function to benchmark (accepts a list of strings).
        data: List of input strings.

    Returns:
        Tuple of (total elapsed seconds, average ms per item).

    """
    start = time.perf_counter()
    out = list(func(data))
    elapsed = time.perf_counter() - start
    assert len(out) == len(data)
    return elapsed, elapsed / len(data) * 1000


def slugify_custom(text: str, mode: str = "noemoji_notranslit", **kwargs) -> str:
    """Perform custom slugification using sluggi pipeline with flexible step selection.

    Args:
        text: Input string to slugify.
        mode: Pipeline mode (
            'noemoji_notranslit', 'emoji_only', 'translit_only', 'both'
        ).
        **kwargs: Additional config options for the pipeline.

    Returns:
        Slugified string.

    """
    separator = kwargs.get("separator", "-")
    custom_map = kwargs.get("custom_map", None)
    stopwords = kwargs.get("stopwords", None)
    lowercase = kwargs.get("lowercase", True)
    word_regex = kwargs.get("word_regex", None)
    decode_entities = kwargs.get("decode_entities", True)
    decode_decimal = kwargs.get("decode_decimal", True)
    decode_hexadecimal = kwargs.get("decode_hexadecimal", True)
    max_length = kwargs.get("max_length", None)
    word_boundary = kwargs.get("word_boundary", True)
    save_order = kwargs.get("save_order", True)
    replacement_config = kwargs.get("replacement_config", None)
    if replacement_config is None:
        if custom_map:
            replacement_config = custom_map_to_config(custom_map)
        else:
            replacement_config = ReplacementConfig()
    engine = ReplacementEngine(replacement_config)
    config = {
        "separator": separator,
        "custom_map": custom_map,
        "stopwords": stopwords,
        "lowercase": lowercase,
        "word_regex": word_regex,
        "decode_entities": decode_entities,
        "decode_decimal": decode_decimal,
        "decode_hexadecimal": decode_hexadecimal,
        "max_length": max_length,
        "word_boundary": word_boundary,
        "save_order": save_order,
        "replacement_config": replacement_config,
        "engine": engine,
    }
    pipeline = SlugPipeline.default()
    steps = pipeline.steps.copy()
    if mode == "noemoji_notranslit":
        steps = [
            s for s in steps if s.__name__ not in ("emoji_step", "transliterate_step")
        ]
    elif mode == "emoji_only":
        steps = [s for s in steps if s.__name__ != "transliterate_step"]
    elif mode == "translit_only":
        steps = [s for s in steps if s.__name__ != "emoji_step"]
    elif mode == "both":
        pass  # keep all steps
    else:
        raise ValueError(f"Unknown mode: {mode}")
    pipeline.steps = steps
    pipeline.config = config
    return pipeline.run(text)


def batch_slugify_custom(
    texts: list[str], mode: str = "noemoji_notranslit", **kwargs
) -> list[str]:
    """Batch slugify a list of input strings using slugify_custom."""
    return [slugify_custom(t, mode=mode, **kwargs) for t in texts]


def main():
    """Run the benchmarking script for sluggi and python-slugify."""
    parser = argparse.ArgumentParser(
        description="Benchmark sluggi vs python-slugify with step control"
    )
    parser.add_argument(
        "--n", type=int, default=None, help="Number of items (default: all)"
    )
    parser.add_argument(
        "--length", type=int, default=40, help="Length of each string (for synthetic)"
    )
    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Input file with real-world test strings (one per line, utf-8)",
    )
    parser.add_argument(
        "--mode",
        default=None,
        choices=[
            "noemoji_notranslit",
            "emoji_only",
            "translit_only",
            "both",
            "all",
        ],
        help="Pipeline mode: which steps to enable",
    )
    parser.add_argument(
        "--synthetic-mixed",
        action="store_true",
        help="Use synthetic mixed-content data (ASCII, Unicode, emoji)",
    )
    parser.add_argument(
        "--process-emoji",
        dest="process_emoji",
        action="store_true",
        help="Enable emoji-to-name conversion (default: off)",
    )
    parser.add_argument(
        "--no-process-emoji",
        dest="process_emoji",
        action="store_false",
        help="Disable emoji-to-name conversion (default)",
    )
    parser.add_argument(
        "--process-transliteration",
        dest="process_transliteration",
        action="store_true",
        help="Enable transliteration (default: on)",
    )
    parser.add_argument(
        "--no-process-transliteration",
        dest="process_transliteration",
        action="store_false",
        help="Disable transliteration",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON (for agents/automation)",
    )
    parser.add_argument(
        "--json-summary",
        action="store_true",
        help="Print only JSON summary (for CI/badge parsing)",
    )
    parser.set_defaults(process_emoji=False, process_transliteration=True)
    args = parser.parse_args()

    if args.synthetic_mixed:
        n = args.n or 10000
        data = generate_mixed_test_data(n, args.length)
        print(
            f"Benchmarking {len(data)} synthetic mixed-content strings "
            f"of length {args.length}..."
        )
    elif args.input:
        data = load_realworld_data(args.input, args.n)
        print(f"Benchmarking {len(data)} real-world strings from {args.input}...")
    elif args.n is not None:
        data = generate_test_data(args.n, args.length)
        print(
            f"Benchmarking {len(data)} synthetic ASCII-only strings "
            f"of length {args.length}..."
        )
    else:
        data = load_realworld_data(None, None)
        print(f"Benchmarking {len(data)} built-in real-world samples...")

    modes = (
        ["noemoji_notranslit", "emoji_only", "translit_only", "both"]
        if args.mode in (None, "all")
        else [args.mode]
    )
    results = []
    # Compute py_slugify benchmark once for reference
    t2, avg2 = bench_one(lambda x: py_slugify(x), data)
    for mode in modes:
        # Explicitly set process_emoji/process_transliteration for each mode
        if mode == "emoji_only":
            process_emoji = True
            process_transliteration = False
        elif mode == "translit_only":
            process_emoji = False
            process_transliteration = True
        elif mode == "both":
            process_emoji = True
            process_transliteration = True
        else:
            process_emoji = False
            process_transliteration = False
        t1, avg1 = bench_one(
            lambda x: slugify_custom(
                x,
                mode=mode,
                process_emoji=process_emoji,
                process_transliteration=process_transliteration,
            ),
            data,
        )
        t3, avg3 = bench_batch(
            lambda d: batch_slugify(
                d,
                mode=mode,
            ),
            data,
        )
        results.append((mode, t1, avg1, t2, avg2, t3, avg3))

    if args.json:
        import json

        json_results = []
        for mode, t1, avg1, t2, avg2, t3, avg3 in results:
            json_results.append(
                {
                    "mode": mode,
                    "method": "sluggi.slugify",
                    "total_ms": round(t1 * 1000, 6),
                    "avg_ms_per_item": round(avg1, 6),
                }
            )
            json_results.append(
                {
                    "mode": mode,
                    "method": "sluggi.batch",
                    "total_ms": round(t3 * 1000, 6),
                    "avg_ms_per_item": round(avg3, 6),
                }
            )
        json_results.append(
            {
                "mode": "python-slugify",
                "method": "python-slugify (single)",
                "total_ms": round(t2 * 1000, 6),
                "avg_ms_per_item": round(avg2, 6),
            }
        )
        print(json.dumps(json_results, indent=2))
        return

    if args.json_summary:
        import json

        json_results = []
        for mode, t1, avg1, t2, avg2, t3, avg3 in results:
            json_results.append(
                {
                    "mode": mode,
                    "method": "sluggi.slugify",
                    "total_ms": round(t1 * 1000, 3),
                    "avg_ms_per_item": round(avg1, 3),
                }
            )
            json_results.append(
                {
                    "mode": mode,
                    "method": "sluggi.batch",
                    "total_ms": round(t3 * 1000, 3),
                    "avg_ms_per_item": round(avg3, 3),
                }
            )
        json_results.append(
            {
                "mode": "python-slugify",
                "method": "python-slugify (single)",
                "total_ms": round(t2 * 1000, 3),
                "avg_ms_per_item": round(avg2, 3),
            }
        )
        with open("benchmark.json", "w", encoding="utf-8") as f:
            json.dump(json_results, f, indent=2)
        print("[INFO] Benchmark results written to benchmark.json")
        return
    print("\nSummary:")
    try:
        from rich.console import Console
        from rich.table import Table

        console = Console()
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Mode", style="dim", width=22)
        table.add_column("Method", width=30)
        table.add_column("Total (ms)", justify="right", width=10)
        table.add_column("Avg ms/item", justify="right", width=13)
        for mode, t1, avg1, t2, avg2, t3, avg3 in results:
            table.add_row(mode, "sluggi.slugify", f"{t1 * 1000:.3f}", f"{avg1:.3f}")
            table.add_row(mode, "sluggi.batch", f"{t3 * 1000:.3f}", f"{avg3:.3f}")
        table.add_row(
            "python-slugify",
            "python-slugify (single)",
            f"{t2 * 1000:.3f}",
            f"{avg2:.3f}",
        )
        console.print(table)
    except ImportError:
        # Fallback to plain summary if rich is not available
        print(f"{'Mode':<22} {'Method':<30} {'Total (ms)':>10} {'Avg ms/item':>13}")
        print("-" * 75)
        for mode, t1, avg1, t2, avg2, t3, avg3 in results:
            print(f"{mode:<22} {'sluggi.slugify':<30} {t1 * 1000:10.3f} {avg1:13.3f}")
            print(f"{mode:<22} {'sluggi.batch':<30}   {t3 * 1000:10.3f} {avg3:13.3f}")
            print(
                f"{'python-slugify':<22} {'python-slugify (single)':<30} "
                f"{t2 * 1000:10.3f} {avg2:13.3f}"
            )


if __name__ == "__main__":
    main()
