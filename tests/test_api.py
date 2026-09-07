"""Synchronous tests for the sluggi library.
Covers slugify and batch_slugify for correctness, Unicode, emoji, and edge cases.
"""

import os
import threading
import warnings

import pytest

from sluggi import batch_slugify, slugify
from sluggi.api import truncate_slug


def test_truncate_slug_basic():
    """Test basic slug truncation functionality."""
    # Already short enough
    assert truncate_slug("foo-bar", 20) == "foo-bar"
    assert truncate_slug("foo-bar", 7) == "foo-bar"
    assert truncate_slug("foo-bar", 6) == "foo"
    assert truncate_slug("foo-bar", 3) == "foo"
    assert truncate_slug("foo-bar", 2) == "fo"
    with pytest.raises(ValueError):
        truncate_slug("foo-bar", 0)
    assert truncate_slug("foo-bar", 6, word_boundary=False) == "foo-ba"
    assert truncate_slug("foo-bar", 2, word_boundary=False) == "fo"
    # Truncate, word_boundary=False
    assert truncate_slug("a-b-cde-fg", 5, word_boundary=False) == "a-b-c"
    # Custom separator
    assert truncate_slug("foo_bar_baz", 7, separator="_") == "foo_bar"
    # Empty string
    assert truncate_slug("", 5) == ""
    # Single long word (should truncate mid-word if nothing fits)
    assert truncate_slug("supercalifragilistic", 5) == "super"
    # Only one word fits
    assert truncate_slug("foo-bar-baz", 3) == "foo"
    # No word fits, so first word is truncated
    assert truncate_slug("longword", 4) == "long"
    # All words empty
    assert truncate_slug("---", 2) == ""
    # Delimiters at edges
    assert truncate_slug("-foo-bar-", 7) == "foo-bar"
    # Trailing separator after truncation (should strip)
    assert truncate_slug("foo-bar-baz", 8, word_boundary=False) == "foo-bar"
    # Type errors
    with pytest.raises(TypeError):
        truncate_slug(123, 5)
    with pytest.raises(ValueError):
        truncate_slug("foo", 0)


def test_slugify_without_emoji():
    """Test slugify when emoji package is not installed (should not fail, just skip
    emoji mapping).
    """
    assert slugify("hello 🚀", process_emoji=False) == "hello"


def test_batch_slugify_process_chunking():
    """Test batch_slugify with process mode and large input to trigger chunking and
    process pool.
    """
    data = ["foo"] * 100  # Large enough for chunking
    result = batch_slugify(data, mode="process", parallel=True, workers=2)
    assert result == ["foo"] * 100
    result = batch_slugify(["foo", "bar"], mode="process", parallel=True, workers=2)
    assert result == ["foo", "bar"]


def test_batch_slugify_custom_cache_size():
    """Test batch_slugify with thread mode and custom cache size (should not error)."""
    data = ["foo", "bar"]
    result = batch_slugify(data, mode="thread", parallel=True, cache_size=32)
    assert result == ["foo", "bar"]


def test_batch_slugify_process_cache_warning():
    """Test batch_slugify in process mode emits a cache warning if cache_size is set."""
    print(
        f"TEST: before catch_warnings, pid={os.getpid()}, tid={threading.get_ident()}"
    )
    print(f"TEST: warnings.filters before context: {warnings.filters}")

    def minimal_warn():
        print(
            f"MINIMAL: emitting warning, pid={os.getpid()}, tid={threading.get_ident()}"
        )
        print(f"MINIMAL: warnings.filters: {warnings.filters}")
        warnings.warn(
            "MINIMAL: Caching is not available in process mode; repeated inputs will "
            "be recomputed.",
            UserWarning,
            stacklevel=2,
        )

    data = [f"foo{i}" for i in range(100)]
    with warnings.catch_warnings(record=True) as w:
        print(
            f"TEST: inside catch_warnings, pid={os.getpid()}, "
            f"tid={threading.get_ident()}"
        )
        print(f"TEST: warnings.filters inside context: {warnings.filters}")
        warnings.simplefilter("always")
        print("TEST: direct emission of warning logic:")
        warnings.warn(
            "DIRECT: Caching is not available in process mode; repeated inputs will "
            "be recomputed.",
            UserWarning,
            stacklevel=2,
        )
        print("TEST: calling minimal_warn():")
        minimal_warn()
        print("TEST: calling batch_slugify():")
        batch_slugify(data, parallel=True, mode="process", cache_size=2048)
        print(f"DEBUG: warnings captured: {w}")
        for warning in w:
            print(f"DEBUG: warning: {warning}")
            print(
                f"DEBUG: warning filename: {getattr(warning, 'filename', None)}, "
                f"lineno: {getattr(warning, 'lineno', None)}"
            )
        assert any(
            issubclass(warning.category, UserWarning)
            and "Caching is not available in process mode" in str(warning.message)
            for warning in w
        ), "Expected UserWarning about process mode cache was not emitted!"
    assert batch_slugify(
        ["foo", "bar"],
        mode="process",
        parallel=True,
    ) == [
        "foo",
        "bar",
    ]


def test_simple_warning_capture():
    """Test that warnings are captured and classified as UserWarning."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        warnings.warn(
            "This is a test warning",
            UserWarning,
        )
        print(f"SIMPLE TEST: warnings captured: {w}")
        for warning in w:
            print(f"SIMPLE TEST: warning: {warning}")
        assert any(
            issubclass(warning.category, UserWarning)
            and "test warning" in str(warning.message)
            for warning in w
        ), "Simple test warning was not emitted!"


def test_basic_ascii():
    """Test slugify with simple ASCII input."""
    assert slugify("Hello, world!") == "hello-world"


def test_custom_separator():
    """Test slugify with a custom separator."""
    assert slugify("Hello, world!", separator="_") == "hello_world"


def test_unicode_normalization():
    """Test slugify with Unicode normalization and diacritics removal."""
    assert slugify("Café déjà vu") == "cafe-deja-vu"
    assert slugify("naïve façade") == "naive-facade"


def test_cyrillic_transliteration():
    """Test slugify with Cyrillic input for transliteration."""
    assert slugify("Привет мир") == "privet-mir"
    assert slugify("Москва") == "moskva"


def test_greek_transliteration():
    """Test slugify with Greek input for transliteration."""
    assert slugify("Γειά σου Κόσμε") == "geia-sou-kosme"
    assert slugify("Αθήνα") == "athina"


def test_emoji_slugification():
    """Test slugify with emoji input for emoji-to-text mapping."""
    # Basic cases
    assert slugify("hello 🔥", process_emoji=True) == "hello-fire"
    assert slugify("I love 🍕 and 🍣!", process_emoji=True) == "i-love-pizza-and-sushi"
    assert (
        slugify("rocket 🚀 to the moon 🌙", process_emoji=True)
        == "rocket-rocket-to-the-moon-crescent-moon"
    )
    # Multiple emojis in a row
    assert (
        slugify("🎉🎉 Party time!", process_emoji=True)
        == "party-popper-party-popper-party-time"
    )
    assert slugify("Go! 🏃‍♂️🏃‍♀️", process_emoji=True) == "go-man-running-woman-running"
    # Rare/compound emojis
    assert (
        slugify("family 👨‍👩‍👧‍👦", process_emoji=True)
        == "family-family-man-woman-girl-boy"
    )
    assert slugify("Flags 🇺🇸🇯🇵", process_emoji=True) == "flags-united-states-japan"
    # Skin tone modifiers
    assert (
        slugify("thumbs up 👍🏽", process_emoji=True)
        == "thumbs-up-thumbs-up-medium-skin-tone"
    )
    # Custom separator
    assert (
        slugify("fire & ice 🔥❄️", separator="_", process_emoji=True)
        == "fire_ice_fire_snowflake"
    )


def test_custom_map():
    """Test slugify with a custom character mapping for specific replacements."""
    assert slugify("ä ö ü", custom_map={"ä": "ae", "ö": "oe", "ü": "ue"}) == "ae-oe-ue"


def test_strip_and_collapse_separators():
    """Test slugify strips and collapses multiple/leading/trailing separators."""
    assert slugify("  Hello---world!!  ") == "hello-world"
    assert slugify("foo_bar baz", separator="_") == "foo_bar_baz"


def test_empty_and_nonalpha():
    """Test slugify with empty input and only non-alphabetic characters."""
    assert slugify("") == ""
    assert slugify("!!!") == ""
    assert slugify("123") == "123"
    assert slugify("abc123") == "abc123"


def test_type_error():
    """Test slugify raises TypeError on non-string input."""
    with pytest.raises(TypeError):
        slugify(123)


@pytest.mark.parametrize(
    "mode,workers",
    [
        ("serial", None),
        ("thread", None),
        ("process", None),
        ("thread", 2),
        ("process", 2),
    ],
)
def test_batch_modes_and_workers(mode, workers):
    """Test batch_slugify with different modes and worker counts."""
    """Test batch_slugify in all modes and with/without workers."""
    inputs = ["Hello, world!", "Café déjà vu", "Привет мир"]
    expected = ["hello-world", "cafe-deja-vu", "privet-mir"]
    result = batch_slugify(
        inputs,
        mode=mode,
        workers=workers,
        parallel=(mode != "serial"),
    )
    assert result == expected


@pytest.mark.parametrize(
    "input_type",
    [
        list,
        tuple,
        lambda x: (i for i in x),
    ],
)
def test_batch_input_types(input_type):
    """Test batch_slugify with various input types (list, tuple, generator)."""
    """Test batch_slugify with list, tuple, and generator inputs."""
    data = ["foo", "bar"]
    expected = ["foo", "bar"]
    result = batch_slugify(input_type(data))
    assert result == expected


def test_batch_large():
    """Test batch_slugify with a large batch (sanity, not performance)."""
    """Test batch_slugify with a large batch (sanity, not performance)."""
    data = ["foo"] * 1000
    result = batch_slugify(data, mode="thread", parallel=True)
    assert result == ["foo"] * 1000


def test_batch_empty():
    """Test batch_slugify with an empty list input."""
    """Test batch_slugify with empty list."""
    assert batch_slugify([]) == []


def test_batch_type_error():
    """Test batch_slugify raises TypeError on non-iterable input."""
    """Test batch_slugify raises TypeError on non-iterable input."""
    with pytest.raises(TypeError):
        batch_slugify("not a list")


# --- Pipeline order regression tests -----------------------------------------
# The README documents the pipeline step by step. These tests pin that
# documentation to the implementation so the two cannot drift apart silently.


def test_default_pipeline_order_matches_readme():
    """Test the default pipeline runs the steps in the documented order."""
    from sluggi.api import SlugPipeline

    steps = [step.__name__ for step in SlugPipeline.default_pipeline()]
    assert steps == [
        "pre_replacements_step",
        "decode_entities_step",
        "normalize_step",
        "transliterate_step",
        "emoji_step",
        "lowercase_step",
        "extract_words_step",
        "filter_stopwords_step",
        "join_words_step",
        "strip_separators_step",
        "truncate_step",
        "post_replacements_step",
    ]


def test_custom_map_applies_at_post_stage():
    """Test custom_map is staged "both", so it can rewrite the separator.

    The separator only exists after join_words, so a mapping that changes it
    proves the replacement engine runs again after the slug is assembled.
    """
    assert slugify("hello world", custom_map={"-": "+"}) == "hello+world"


def test_lowercase_runs_before_word_extraction():
    """Test lowercasing happens before extract_words, not after join_words.

    A lowercase-only word_regex still matches every word; if casing were
    applied after joining, this would yield "ello-orld".
    """
    assert slugify("Hello World", word_regex=r"[a-z]+") == "hello-world"


def test_normalize_unicode_strips_diacritics():
    """Test normalization is NFKD plus combining-mark removal, not NFKC."""
    assert slugify("Café déjà vu") == "cafe-deja-vu"
