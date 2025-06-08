"""sluggi main module: Provides slugify and batch_slugify utilities.

Generates URL-safe slugs from text with Unicode normalization, transliteration,
emoji handling, batch processing, async support, and LRU caching.

sluggi.api
----------

Main module for sluggi: provides the modular, extensible slugification pipeline.

Key exports:
    - slugify: Main entry point for converting text to a URL-safe slug.
    - batch_slugify: Batch-processing for lists of slugs.
    - SlugPipeline: Advanced pipeline customization and extension.
    - Modular pipeline helpers: normalize_unicode, decode_html_entities_and_refs,
      convert_emojis, transliterate_text, extract_words, filter_stopwords, join_words,
      to_lowercase, strip_separators, smart_truncate.

Pipeline design:
    The slugification process is broken into pure, single-purpose functions, each
    responsible for a well-defined transformation (normalization, decoding, emoji,
    transliteration, tokenization, filtering, joining, casing, truncation, etc).
    This enables easy extension, testing, and maintenance, while supporting staged
    replacements and custom mappings.

Advanced Usage:
---------------

sluggi exposes a `SlugPipeline` class for advanced users who wish to customize the
slugification process. You can modify the sequence of processing steps, add custom
logic, or subclass the pipeline for full control over slug generation.

Example (custom pipeline):
    >>> from sluggi.api import SlugPipeline
    >>> def my_step(text, config):
    ...     return text.replace("foo", "bar")
    >>> pipeline = SlugPipeline.default(separator="_", lowercase=False)
    >>> pipeline.steps.insert(2, my_step)
    >>> result = pipeline.run("foo baz!")
    >>> print(result)
    bar_baz

See each function and class docstring for detailed usage information and extension
points.
"""

import asyncio
import concurrent.futures
import html
import json
import os
import re
import time
import traceback
import unicodedata
import warnings
from collections.abc import Iterable
from functools import lru_cache, partial
from typing import Optional

from .constants import (
    _BUILTIN_TRANSLIT_MAP,
    _RE_EMOJI_ADJACENT,
    _RE_EMOJI_NAME,
    _RE_HTML_ENTITY_DECIMAL,
    _RE_HTML_ENTITY_HEXADECIMAL,
    _RE_WORD,
    _TRANSLIT_REGEX,
)
from .replacements import ReplacementConfig, ReplacementEngine, custom_map_to_config
from .utils import truncate_slug

try:
    import emoji
except ImportError:
    emoji = None


def normalize_unicode(text: str) -> str:
    """Normalize unicode using NFKD and remove diacritics.

    Args:
        text (str): Input string.

    Returns:
        str: Unicode-normalized string with diacritics removed.

    Example:
        >>> normalize_unicode("Café déjà vu")
        'Cafe deja vu'

    """
    text = unicodedata.normalize("NFKD", text)
    return "".join([c for c in text if not unicodedata.combining(c)])


def decode_html_entities_and_refs(
    text: str,
    decode_entities: bool = True,
    decode_decimal: bool = True,
    decode_hexadecimal: bool = True,
) -> str:
    """Decode HTML entities (e.g., &eacute;), decimal (e.g., &#233;), and hexadecimal
    (e.g., &#xE9;) numeric references.

    Args:
        text (str): Input string.
        decode_entities (bool): Decode named HTML entities (default True).
        decode_decimal (bool): Decode decimal numeric references (default True).
        decode_hexadecimal (bool): Decode hexadecimal numeric references (default True).

    Returns:
        str: Decoded string.

    Example:
        >>> decode_html_entities_and_refs("Fran&ccedil;ois &#233;tait l&#xE9;ger")
        'François était léger'

    """
    if decode_entities:
        # Custom unescape to skip numeric refs if flags are False
        def selective_unescape(s):
            # Replace named entities only
            def repl(m):
                entity = m.group(1)
                if entity.startswith("#x") or entity.startswith("#X"):
                    return (
                        m.group(0)
                        if not decode_hexadecimal
                        else html.unescape(m.group(0))
                    )
                elif entity.startswith("#"):
                    return (
                        m.group(0) if not decode_decimal else html.unescape(m.group(0))
                    )
                else:
                    return html.unescape(m.group(0))

            return re.sub(r"&([#a-zA-Z0-9]+);", repl, s)

        text = selective_unescape(text)
    else:
        # If not decoding named entities, only decode numeric if flags are set
        if decode_decimal:

            def dec_entity(m):
                try:
                    return chr(int(m.group(1)))
                except Exception:
                    return m.group(0)

            text = _RE_HTML_ENTITY_DECIMAL.sub(dec_entity, text)
        if decode_hexadecimal:

            def hex_entity(m):
                try:
                    return chr(int(m.group(1), 16))
                except Exception:
                    return m.group(0)

            text = _RE_HTML_ENTITY_HEXADECIMAL.sub(hex_entity, text)
    return text


def convert_emojis(text: str, separator: str) -> str:
    """Convert emojis to :name: format and replace with separator-based names if
    emoji module is present.

    Args:
        text (str): Input string.
        separator (str): Separator to use in place of underscores in emoji names.

    Returns:
        str: String with emojis converted to separator-based names, or unchanged if
            emoji module is not installed.

    Example:
        >>> convert_emojis("I love 🍕!", "-")
        'I love pizza!'

    """
    if emoji is None:
        # Optionally, warn user (commented out to avoid spam):
        # warnings.warn("emoji package is not installed; skipping emoji conversion.")
        return text
    text = emoji.demojize(text, language="en")
    text = _RE_EMOJI_ADJACENT.sub(r"\1" + separator, text)
    text = _RE_EMOJI_NAME.sub(lambda m: m.group(1).replace("_", separator), text)
    return text


def transliterate_text(text: str) -> str:
    """Apply built-in transliteration for Cyrillic, Greek, and single-character
    mappings.

    Args:
        text (str): Input string.

    Returns:
        str: Transliterated string (e.g., Cyrillic → Latin).

    Example:
        >>> transliterate_text("Привет мир")
        'Privet mir'

    """
    return _TRANSLIT_REGEX.sub(lambda m: _BUILTIN_TRANSLIT_MAP[m.group(0)], text)
    # for k, v in _BUILTIN_TRANSLIT_MAP.items():
    #     text = text.replace(k, v)
    # # Single-character transliteration for any new Greek base letters
    # text = "".join(_BUILTIN_TRANSLIT_MAP.get(char, char) for char in text)
    # return text


def extract_words(
    text: str,
    word_regex: Optional[str],
) -> list[str]:
    """Extract words using a custom regex or default pattern.

    Args:
        text (str): Input string.
        word_regex (str, optional): Regex pattern for word extraction. Defaults to
            built-in pattern.

    Returns:
        List[str]: List of extracted words.

    Example:
        >>> extract_words("Hello, world!", None)
        ['Hello', 'world']

    """
    if word_regex is None:
        pattern = _RE_WORD
    else:
        pattern = re.compile(word_regex)
    return pattern.findall(text)


def filter_stopwords(
    words: list[str], stopwords: Optional[Iterable[str]], lowercase: bool
) -> list[str]:
    """Remove stopwords from the list of words.

    Args:
        words (list[str]): List of words.
        stopwords (Iterable[str], optional): Words to remove.
        lowercase (bool): Whether to compare stopwords in lowercase.

    Returns:
        list[str]: Filtered list of words.

    Example:
        >>> filter_stopwords(["the", "quick", "brown", "fox"], ["the", "fox"], True)
        ['quick', 'brown']

    """
    if stopwords:
        stopwords_set = (
            set(w.lower() for w in stopwords) if lowercase else set(stopwords)
        )
        if lowercase:
            words = [w for w in words if w.lower() not in stopwords_set]
        else:
            words = [w for w in words if w not in stopwords_set]
    return words


def join_words(words: list[str], separator: str) -> str:
    """Join words with the given separator.

    Args:
        words (List[str]): Words to join.
        separator (str): Separator character(s).

    Returns:
        str: Joined string.

    Example:
        >>> join_words(["hello", "world"], "-")
        'hello-world'

    """
    return separator.join(words)


def to_lowercase(text: str) -> str:
    """Convert text to lowercase.

    Args:
        text (str): Input string.

    Returns:
        str: Lowercased string.

    Example:
        >>> to_lowercase("Hello World!")
        'hello world!'

    """
    return text.lower()


def strip_separators(
    text: str,
    separator: str,
) -> str:
    """Remove leading/trailing separators.

    Args:
        text (str): Input string.
        separator (str): Separator to strip.

    Returns:
        str: String with leading/trailing separators removed.

    Example:
        >>> strip_separators("--foo-bar--", "-")
        'foo-bar'

    """
    return text.strip(separator)


# --- Refactored slugify using modular functions ---
class SlugPipeline:
    """A customizable pipeline for slugification.

    The SlugPipeline class allows advanced users to modify the sequence of
    processing steps, add or remove steps, or subclass the pipeline for full
    control over the slugification process.

    Args:
        steps (list of callables): Each step is a function (data, config) -> data.
        config (dict): Configuration dictionary passed to each step.

    Usage:
        - Use SlugPipeline.default(...) to construct a pipeline with default steps
          and configuration.
        - Modify `pipeline.steps` to insert, remove, or reorder processing steps.
        - Call `pipeline.run(text)` to process input text through the pipeline.
        - Subclass SlugPipeline to override or extend behavior.

    Examples:
        >>> from sluggi.api import SlugPipeline
        >>> def my_step(text, config):
        ...     return text.replace("foo", "bar")
        >>> pipeline = SlugPipeline.default(separator="_", lowercase=False)
        >>> pipeline.steps.insert(2, my_step)
        >>> result = pipeline.run("foo baz!")
        >>> print(result)
        bar_baz

        # Subclassing for custom behavior
        >>> class MyPipeline(SlugPipeline):
        ...     def run(self, data):
        ...         data = super().run(data)
        ...         return data.upper()
        >>> pipeline = MyPipeline.default(separator="-")
        >>> print(pipeline.run("hello world!"))
        HELLO-WORLD

    See the module docstring for more advanced usage and extension points.

    """

    def __init__(self, steps, config):
        """Initialize the pipeline with steps and configuration."""
        self.steps = steps
        self.config = config

    def run(self, data):
        """Run the pipeline on the input data."""
        for step in self.steps:
            data = step(data, self.config)
        return data

    @classmethod
    def default_pipeline(cls, separator="-", lowercase=True):
        """Return a default pipeline with common steps."""

        # --- Step definitions ---
        def pre_replacements_step(text, config):
            return config["engine"].apply(text, stage="pre")[0]

        def decode_entities_step(text, config):
            return decode_html_entities_and_refs(
                text,
                decode_entities=config["decode_entities"],
            )

        def normalize_step(text, config):
            # Lazy normalization: only if text has non-ASCII or combining marks
            if text.isascii():
                return text
            return normalize_unicode(text)

        def transliterate_step(text, config):
            # Config flag: skip transliteration if requested
            if not config.get("process_transliteration", True):
                return text

            # ASCII fast-path: if text is ASCII, skip transliteration
            if text.isascii():
                return text

            if not any(c in _BUILTIN_TRANSLIT_MAP for c in text):
                return text
            return transliterate_text(text)

        def emoji_step(text, config):
            if emoji is None or not config.get("process_emoji") or text.isascii():
                return text
            return convert_emojis(text, config["separator"])

        def lowercase_step(text, config):
            return to_lowercase(text) if config["lowercase"] else text

        def extract_words_step(text, config):
            return extract_words(text, config["word_regex"])

        def filter_stopwords_step(words, config):
            return filter_stopwords(words, config["stopwords"], config["lowercase"])

        def join_words_step(words, config):
            return join_words(words, config["separator"])

        def strip_separators_step(text, config):
            return strip_separators(text, config["separator"])

        def truncate_step(text, config):
            return truncate_slug(
                text,
                config["max_length"],
                config["word_boundary"],
                config["separator"],
            )

        def post_replacements_step(text, config):
            return config["engine"].apply(text, stage="post")[0]

        return [
            pre_replacements_step,
            decode_entities_step,
            normalize_step,
            transliterate_step,
            emoji_step,
            lowercase_step,
            extract_words_step,
            filter_stopwords_step,
            join_words_step,
            strip_separators_step,
            truncate_step,
            post_replacements_step,
        ]

    @classmethod
    def default(cls, **kwargs):
        """Construct a SlugPipeline with the default steps and config.
        Accepts the same keyword arguments as slugify (except text).

        Keyword Args:
            process_emoji (bool): If False, disables emoji-to-name conversion for
                maximum performance. Default is False.
            process_transliteration (bool): If False, disables transliteration for
                maximum performance. Default is True.
            kwargs: Keyword arguments to pass to slugify.

        """
        # Remove text if present
        config = dict(kwargs)
        config.pop("text", None)
        if "process_emoji" not in config:
            config["process_emoji"] = False
        if "process_transliteration" not in config:
            config["process_transliteration"] = True
        pipeline = cls.default_pipeline(
            separator=config.get("separator", "-"),
            lowercase=config.get("lowercase", True),
        )
        return cls(pipeline, config)


def slugify(
    text: str,
    separator: str = "-",
    custom_map: Optional[dict[str, str]] = None,
    stopwords: Optional[Iterable[str]] = None,
    lowercase: bool = True,
    word_regex: Optional[str] = None,
    decode_entities: bool = True,
    decode_decimal: bool = True,
    decode_hexadecimal: bool = True,
    max_length: Optional[int] = None,
    word_boundary: bool = True,
    process_emoji: bool = False,
    replacement_config: Optional[ReplacementConfig] = None,
) -> str:
    """Convert a string to a clean, URL-safe slug with Unicode normalization,
    transliteration, emoji handling, HTML entity/numeric reference decoding, and
    stopword removal. Supports staged pre- and post-processing replacements via
    ReplacementConfig.

    Args:
        text (str): Input text to slugify.
        separator (str, optional): Separator for words in the slug (default: '-').
        custom_map (dict, optional): Custom character replacements.
        stopwords (Iterable[str], optional): Words to exclude from slug.
        lowercase (bool, optional): Convert result to lowercase (default: True).
        word_regex (str, optional): Custom regex for word extraction.
        decode_entities (bool, optional): Decode named HTML entities (default: True).
        decode_decimal (bool, optional): Decode decimal numeric references
            (default: True).
        decode_hexadecimal (bool, optional): Decode hexadecimal numeric references
            (default: True).
        max_length (int, optional): Maximum length for the slug (default: None).
        word_boundary (bool, optional): Truncate at word boundary (default: True).
        process_emoji (bool, optional): Whether to process emoji (default: False).
        replacement_config (ReplacementConfig, optional): Custom replacements.

    Returns:
        str: Slugified string.

    Advanced Usage:
        For advanced customization, use the SlugPipeline class to define your own
            pipeline:

        >>> pipeline = SlugPipeline.default(separator="_", lowercase=False)
        >>> pipeline.steps.insert(2, my_custom_step)
        >>> result = pipeline.run("My Text!")

    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")

    # --- Replacement config setup ---
    if replacement_config is None and custom_map is not None:
        replacement_config = custom_map_to_config(custom_map, stage="both")
    elif replacement_config is None:
        replacement_config = ReplacementConfig()
    engine = ReplacementEngine(replacement_config)

    config = {
        "separator": separator,
        "stopwords": stopwords,
        "lowercase": lowercase,
        "word_regex": word_regex,
        "decode_entities": decode_entities,
        "decode_decimal": decode_decimal,
        "decode_hexadecimal": decode_hexadecimal,
        "max_length": max_length,
        "word_boundary": word_boundary,
        "process_emoji": process_emoji,
        "engine": engine,
        "replacement_config": replacement_config,
    }

    # Always use the full pipeline for all input (ASCII and Unicode)
    pipeline = SlugPipeline.default_pipeline(
        separator=separator,
        lowercase=lowercase,
    )
    return SlugPipeline(pipeline, config).run(text)


async def async_slugify(
    text: str,
    separator: str = "-",
    custom_map: Optional[dict[str, str]] = None,
    stopwords: Optional[Iterable[str]] = None,
    lowercase: bool = True,
    word_regex: Optional[str] = None,
    max_length: Optional[int] = None,
    word_boundary: bool = True,
    process_emoji: bool = False,
    replacement_config: Optional[ReplacementConfig] = None,
) -> str:
    """Async version of slugify, offloading to a thread."""
    return await asyncio.to_thread(
        slugify,
        text,
        separator,
        custom_map,
        stopwords,
        lowercase,
        word_regex,
        max_length=max_length,
        word_boundary=word_boundary,
        process_emoji=process_emoji,
        replacement_config=replacement_config,
    )


async def async_batch_slugify(
    texts: Iterable[str],
    separator: str = "-",
    custom_map: Optional[dict[str, str]] = None,
    stopwords: Optional[Iterable[str]] = None,
    lowercase: bool = True,
    word_regex: Optional[str] = None,
    parallel: bool = False,
    workers: Optional[int] = None,
    chunk_size: int = 1000,
    max_length: Optional[int] = None,
    word_boundary: bool = True,
    process_emoji: bool = False,
) -> list[str]:
    """Async version of batch_slugify. Processes items concurrently using asyncio.

    Args:
        texts (Iterable[str]): List of input strings.
        separator (str, optional): Separator for words in the slug.
        custom_map (dict, optional): Custom character replacements.
        stopwords (Iterable[str], optional): Words to exclude from slug.
        lowercase (bool, optional): Convert result to lowercase (default: True).
        word_regex (str, optional): Custom regex pattern for word extraction.
        parallel (bool): Whether to process in parallel.
        workers (int, optional): Number of parallel workers.
        chunk_size (int): Chunk size for parallel processing.
        max_length (int, optional): Maximum length for each slug (default: None).
        word_boundary (bool, optional): Truncate at word boundary (default: True).
        process_emoji (bool, optional): Whether to process emoji (default: False).

    Returns:
        List[str]: List of slugified strings.

    """
    if isinstance(texts, (str, bytes)):
        raise TypeError(
            "Input to async_batch_slugify must be an iterable of strings, "
            "not a string/bytes."
        )
    items = list(texts)
    if not items:
        return []
    if not parallel or len(items) < chunk_size:
        # Always call async_slugify so the ASCII fast-path is used for each input
        return [
            await async_slugify(
                t,
                separator,
                custom_map,
                stopwords,
                lowercase,
                word_regex,
                max_length=max_length,
                word_boundary=word_boundary,
                process_emoji=process_emoji,
            )
            for t in items
        ]
    sem = asyncio.Semaphore(workers or (os.cpu_count() or 1))

    async def sem_task(t):
        async with sem:
            # Always call async_slugify so the ASCII fast-path is used for each input
            return await async_slugify(
                t,
                separator,
                custom_map,
                stopwords,
                lowercase,
                word_regex,
                max_length=max_length,
                word_boundary=word_boundary,
                process_emoji=process_emoji,
            )

    return await asyncio.gather(*(sem_task(t) for t in items))


def batch_slugify(
    texts: Iterable[str],
    separator: str = "-",
    custom_map: Optional[dict[str, str]] = None,
    stopwords: Optional[Iterable[str]] = None,
    lowercase: bool = True,
    word_regex: Optional[str] = None,
    parallel: bool = False,
    workers: Optional[int] = None,
    mode: str = "thread",
    chunk_size: int = 1000,
    cache_size: int = 2048,
    max_length: Optional[int] = None,
    word_boundary: bool = True,
    process_emoji: bool = False,
    replacement_config: Optional[ReplacementConfig] = None,
) -> list[str]:
    """Slugify a batch of strings efficiently, with optional staged replacements.

    This function supports:
        - Serial, threaded, or process-based parallel processing
        - Chunked processing for large batches (chunk_size param)
        - Automatic LRU caching for repeated or batch slugification
          (except in process mode)
        - Optional stopword removal (case-insensitive if lowercase is True)
        - Smart truncation (optional)

    Args:
        texts (Iterable[str]): List of input strings.
        separator (str, optional): Separator for words in the slug.
        custom_map (dict, optional): Custom character replacements.
        stopwords (Iterable[str], optional): Words to exclude from slug.
        lowercase (bool, optional): Convert to lowercase (default: True).
        word_regex (str, optional): Custom regex pattern for word extraction.
        parallel (bool, optional): Use parallel processing (default: False).
        workers (int, optional): Number of parallel workers.
        mode (str, optional): 'thread', 'process', or 'serial' (default: 'thread').
        chunk_size (int, optional): Size of chunks for batch processing.
        cache_size (int, optional): LRU cache size for repeated inputs.
        max_length (int, optional): Maximum length for each slug (default: None).
        word_boundary (bool, optional): Truncate at word boundary (default: True).
        process_emoji (bool, optional): Whether to process emoji (default: False).
        replacement_config (ReplacementConfig, optional): Custom replacements.

    Returns:
        List[str]: List of slugified strings.

    """
    if isinstance(texts, (str, bytes)):
        raise TypeError(
            "Input to batch_slugify must be an iterable of strings, "
            "not a string/bytes."
        )
    # Backward compatibility: if only custom_map is provided, convert to
    # ReplacementConfig
    if replacement_config is None and custom_map is not None:
        replacement_config = custom_map_to_config(custom_map, stage="both")
    elif replacement_config is None:
        replacement_config = ReplacementConfig()
    items = list(texts)
    n_items = len(items)
    if n_items == 0:
        return []
    if not parallel or n_items < chunk_size:
        # Always call slugify so the ASCII fast-path is used for each input
        return [
            slugify(
                t,
                separator=separator,
                custom_map=custom_map,
                stopwords=stopwords,
                lowercase=lowercase,
                word_regex=word_regex,
                max_length=max_length,
                word_boundary=word_boundary,
                process_emoji=process_emoji,
                replacement_config=replacement_config,
            )
            for t in items
        ]
    if mode not in {"thread", "process", "serial"}:
        raise ValueError(f"Invalid mode: {mode}")
    executor_cls = {
        "thread": concurrent.futures.ThreadPoolExecutor,
        "process": concurrent.futures.ProcessPoolExecutor,
    }.get(mode, concurrent.futures.ThreadPoolExecutor)
    if workers is None:
        workers = os.cpu_count() or 1
    use_cache = mode != "process"
    global _cached_slugify
    if (
        use_cache
        and getattr(_cached_slugify, "cache_info", lambda: None)().maxsize != cache_size
    ):
        _cached_slugify = _get_cached_slugify(cache_size)
    func = partial(
        _process,
        separator=separator,
        custom_map=custom_map,
        stopwords=stopwords,
        lowercase=lowercase,
        use_cache=use_cache,
        word_regex=word_regex,
        max_length=max_length,
        word_boundary=word_boundary,
        process_emoji=process_emoji,
    )
    if mode == "process" and cache_size is not None:
        msg = (
            "Caching is not available in process mode; repeated inputs will be "
            "recomputed. "
            f"Unique: {time.time()}"
        )
        warnings.warn(msg, UserWarning, stacklevel=4)

        traceback.print_stack()
    with executor_cls(max_workers=workers) as executor:
        if mode == "process":
            n_chunks = (n_items + chunk_size - 1) // chunk_size
            results = list(
                executor.map(
                    _process_chunk,
                    chunked(texts, chunk_size),
                    [separator] * n_chunks,
                    [custom_map] * n_chunks,
                    [stopwords] * n_chunks,
                    [lowercase] * n_chunks,
                    [use_cache] * n_chunks,
                    [word_regex] * n_chunks,
                    [max_length] * n_chunks,
                    [word_boundary] * n_chunks,
                    [process_emoji] * n_chunks,
                ),
            )
            return [item for sublist in results for item in sublist]
        else:
            n_chunks = (n_items + chunk_size - 1) // chunk_size
            results = list(
                executor.map(
                    lambda chunk: [func(t) for t in chunk],
                    chunked(texts, chunk_size),
                ),
            )
            return [item for sublist in results for item in sublist]


def _get_cached_slugify(cache_size=2048):
    @lru_cache(maxsize=cache_size)
    def _cached_slugify(
        text: str,
        separator: str,
        cmap_str: Optional[str],
        stopwords_str: Optional[str],
        lowercase: bool,
        word_regex: Optional[str] = None,
        max_length: Optional[int] = None,
        word_boundary: bool = True,
        process_emoji: bool = False,
    ) -> str:
        """Cache slugification results for a given input."""
        cmap = json.loads(cmap_str) if cmap_str else None
        stopwords = json.loads(stopwords_str) if stopwords_str else None
        return slugify(
            text,
            separator=separator,
            custom_map=cmap,
            stopwords=stopwords,
            lowercase=lowercase,
            word_regex=word_regex,
            max_length=max_length,
            word_boundary=word_boundary,
            process_emoji=process_emoji,
        )

    return _cached_slugify


# Default LRU cache for slugification
_cached_slugify = _get_cached_slugify()


def _process(
    text: str,
    separator: str = "-",
    custom_map: Optional[dict[str, str]] = None,
    stopwords: Optional[Iterable[str]] = None,
    lowercase: bool = True,
    use_cache: bool = True,
    word_regex: Optional[str] = None,
    max_length: Optional[int] = None,
    word_boundary: bool = True,
    process_emoji: bool = False,
    replacement_config: Optional[ReplacementConfig] = None,
) -> str:
    """Process a string for slugification.

    Args:
        text (str): Input text.
        separator (str, optional): Separator to use in the slug (default: '-').
        custom_map (dict, optional): Custom character replacements.
        stopwords (Iterable[str], optional): Words to exclude from slug.
        lowercase (bool, optional): Convert result to lowercase (default: True).
        use_cache (bool, optional): Enable caching (default: True).
        word_regex (str, optional): Custom regex for word extraction.
        max_length (int, optional): Maximum length for the slug (default: None).
        word_boundary (bool, optional): Truncate at word boundary (default: True).
        process_emoji (bool, optional): Whether to process emoji (default: False).
        replacement_config (ReplacementConfig, optional): Custom replacements.

    Returns:
        str: Slugified string.

    """
    # Always use slugify, which internally uses the ASCII fast-path if eligible
    return slugify(
        text,
        separator=separator,
        custom_map=custom_map,
        stopwords=stopwords,
        lowercase=lowercase,
        word_regex=word_regex,
        max_length=max_length,
        word_boundary=word_boundary,
        process_emoji=process_emoji,
        replacement_config=replacement_config,
    )


def _process_chunk(
    chunk,
    separator,
    custom_map,
    stopwords,
    lowercase,
    use_cache,
    word_regex=None,
    max_length=None,
    word_boundary=True,
    process_emoji=False,
    replacement_config=None,
):
    """Process a chunk of items for parallel slugification.

    (This is a top-level function for multiprocessing.)

    Args:
        chunk (list): List of input strings.
        separator (str): Separator for the slug.
        custom_map (dict): Custom character replacements.
        stopwords (Iterable[str]): Words to exclude from slug.
        lowercase (bool): Convert result to lowercase.
        use_cache (bool): Whether to use the slugify cache.
        word_regex (str, optional): Custom regex pattern for word extraction.
        max_length (int, optional): Maximum length for each slug (default: None).
        word_boundary (bool, optional): Truncate at word boundary (default: True).
        process_emoji (bool, optional): Whether to process emoji (default: False).
        replacement_config (ReplacementConfig, optional): Custom replacements.

    Returns:
        list: List of slugified strings.

    """
    # Defensive: if stopwords or custom_map are JSON strings or lists, convert to
    # correct type
    if isinstance(stopwords, str):
        try:
            stopwords = json.loads(stopwords)
        except Exception:
            stopwords = []
    if isinstance(custom_map, str):
        try:
            custom_map = json.loads(custom_map)
        except Exception:
            custom_map = None
    func = partial(
        _process,
        separator=separator,
        custom_map=custom_map,
        stopwords=stopwords,
        lowercase=lowercase,
        use_cache=use_cache,
        word_regex=word_regex,
        max_length=max_length,
        word_boundary=word_boundary,
        process_emoji=process_emoji,
        replacement_config=replacement_config,
    )
    return [func(t) for t in chunk]


def chunked(seq, size):
    """Yield successive chunks of a given size from a sequence.

    Args:
        seq (Sequence): Input sequence.
        size (int): Size of each chunk.

    Yields:
        Sequence: Chunks of the input sequence.

    """
    for i in range(0, len(seq), size):
        yield seq[i : i + size]
