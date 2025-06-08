#!/usr/bin/env python3
"""profile.py - Unified profiling tool for sluggi and competitors.

- Supports cProfile, memory profiling (tracemalloc), and pipeline step timing
- Flexible CLI: --library, --mode, --profile, --n, --length, --outfile

Example usage:
    python scripts/profile.py --library sluggi \
        --mode thread --profile cprofile \
        --outfile sluggi_thread.prof
    python scripts/profile.py --library python-slugify \
        --mode single --profile memory
    python scripts/profile.py --profile steps
"""
import argparse
import random
import string
import sys
from typing import Callable, Optional

try:
    from sluggi import batch_slugify
    from sluggi import slugify as sluggi_slugify
except ImportError:
    batch_slugify = None
    sluggi_slugify = None

from sluggi.api import (
    ReplacementConfig,
    ReplacementEngine,
    SlugPipeline,
)


def try_import_py_slugify() -> Optional[Callable]:
    """Try to import python-slugify or slugify as py_slugify.
    Returns the slugify function or None if not available.
    """
    try:
        from python_slugify import slugify as py_slugify

        return py_slugify
    except ImportError:
        try:
            from slugify import slugify as py_slugify

            return py_slugify
        except ImportError:
            return None


py_slugify = try_import_py_slugify()


def random_string(length: int) -> str:
    """Generate a random alphanumeric string of given length."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_test_data(n: int, length: int = 40) -> list[str]:
    """Generate a list of n random strings, each of the specified length."""
    return [random_string(length) for _ in range(n)]


def profile_cprofile(func: Callable, data: list[str], outfile: str) -> None:
    """Run cProfile on the provided function and data, saving output to outfile.

    Args:
        func: The function to profile.
        data: The data to pass to the function.
        outfile: Path to save the .prof file.

    """
    import cProfile

    profiler = cProfile.Profile()
    profiler.enable()
    func(data)
    profiler.disable()
    profiler.dump_stats(outfile)
    print(f"Profile saved to {outfile} (use snakeviz or gprof2dot)")


def profile_memory(func: Callable, data: list[str]) -> None:
    """Profile memory usage of func(data) using tracemalloc.

    Args:
        func: The function to profile (should accept data as argument).
        data: The data to pass to func.

    """
    import tracemalloc

    tracemalloc.start()
    func(data)
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory: {current / 10 ** 6:.2f}MB, Peak: {peak / 10 ** 6:.2f}MB")
    tracemalloc.stop()


def profile_steps(samples: list[str], runs: int = 10000) -> None:
    """Profile the execution time of each step in the sluggi pipeline.

    Args:
        samples: List of sample strings to use (only the first is used).
        runs: Number of runs for timeit (default: 10000).

    """
    replacement_config = ReplacementConfig()
    engine = ReplacementEngine(replacement_config)
    default_word_regex = r"[\w\-]+"
    config = {
        "engine": engine,
        "replacement_config": replacement_config,
        "decode_entities": True,
        "lowercase": True,
        "strip": True,
        "separator": "-",
        "allowed_chars": None,
        "transliterate": True,
        "emoji": True,
        "custom_map": None,
        "word_regex": default_word_regex,
        "strip_diacritics": True,
        "normalize_form": "NFC",
        "remove_stopwords": False,
        "stopwords": set(),
        "max_length": 400,
        "word_boundary": True,
    }
    print("Pipeline step timings (mean ms):")
    pipeline = SlugPipeline.default_pipeline()
    step_names = [step.__name__ for step in pipeline]
    for step, name in zip(pipeline, step_names):

        def stmt():
            return step(samples[0], config)

        import timeit

        t = timeit.timeit(stmt, number=runs)
        print(f"  {name}: {t/runs*1000:.4f} ms")


def main():
    """Run the profiling script entry point."""
    parser = argparse.ArgumentParser(description="Profile sluggi and competitors.")
    parser.add_argument(
        "--library", choices=["sluggi", "python-slugify"], help="Library to profile"
    )
    parser.add_argument(
        "--mode",
        choices=["single", "serial", "thread", "process"],
        default="serial",
        help="Profiling mode",
    )
    parser.add_argument(
        "--profile",
        choices=["cprofile", "memory", "steps"],
        default="cprofile",
        help="Profiling type",
    )
    parser.add_argument("--n", type=int, default=20000, help="Number of items")
    parser.add_argument("--length", type=int, default=40, help="Length of each string")
    parser.add_argument(
        "--outfile",
        type=str,
        default="profile.prof",
        help="Output profile file (for cProfile)",
    )
    args = parser.parse_args()

    data = generate_test_data(args.n, args.length)

    def func_sluggi_single(d):
        return [sluggi_slugify(x) for x in d]

    def func_sluggi_serial(d):
        return list(batch_slugify(d, parallel=False))

    def func_sluggi_thread(d):
        return list(batch_slugify(d, parallel=True, mode="thread"))

    def func_sluggi_process(d):
        return list(batch_slugify(d, parallel=True, mode="process"))

    def func_py_slugify(d):
        return [py_slugify(x) for x in d]

    if args.library == "sluggi":
        if args.mode == "single":
            func = func_sluggi_single
        elif args.mode == "serial":
            func = func_sluggi_serial
        elif args.mode == "thread":
            func = func_sluggi_thread
        elif args.mode == "process":
            func = func_sluggi_process
        else:
            print(f"Unknown mode: {args.mode}")
            sys.exit(1)
    elif args.library == "python-slugify" and py_slugify:
        func = func_py_slugify
    else:
        print("Specify --library (sluggi or python-slugify)")
        sys.exit(1)

    if args.profile == "cprofile":
        profile_cprofile(func, data, args.outfile)
    elif args.profile == "memory":
        profile_memory(func, data)
    elif args.profile == "steps":
        profile_steps(data[:1], runs=1000)
    else:
        print(f"Unknown profile type: {args.profile}")
        sys.exit(1)


if __name__ == "__main__":
    main()
