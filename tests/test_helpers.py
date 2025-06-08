"""Unit tests for sluggi modular helper functions.

Covers: normalize_unicode, decode_html_entities_and_refs, convert_emojis,
transliterate_text, extract_words, filter_stopwords, join_words, to_lowercase,
and strip_separators.
"""

from sluggi.api import (
    convert_emojis,
    decode_html_entities_and_refs,
    extract_words,
    filter_stopwords,
    join_words,
    normalize_unicode,
    strip_separators,
    to_lowercase,
    transliterate_text,
)


# --- normalize_unicode ---
def test_normalize_unicode_basic():
    """Test normalize_unicode with accented and empty input."""
    assert normalize_unicode("Café déjà vu") == "Cafe deja vu"
    assert normalize_unicode("naïve façade") == "naive facade"
    assert normalize_unicode("crème brûlée") == "creme brulee"
    assert normalize_unicode("") == ""


# --- decode_html_entities_and_refs ---
def test_decode_html_entities_and_refs_basic():
    """Test decoding of HTML entities and numeric refs, including skip options."""
    assert decode_html_entities_and_refs("Tom &amp; Jerry") == "Tom & Jerry"
    assert decode_html_entities_and_refs("&#169; 2024") == "© 2024"
    assert decode_html_entities_and_refs("&#x1F600;") == "😀"
    # No decoding
    assert decode_html_entities_and_refs("&amp;", decode_entities=False) == "&amp;"
    assert decode_html_entities_and_refs("&#169;", decode_decimal=False) == "&#169;"
    assert (
        decode_html_entities_and_refs("&#x1F600;", decode_hexadecimal=False)
        == "&#x1F600;"
    )


# --- convert_emojis ---
def test_convert_emojis_basic():
    """Test emoji conversion to text or fallback, with various separators."""
    result = convert_emojis("I love 🍕!", "-")
    # Fallback if emoji unavailable
    assert "pizza" in result or ":pizza:" in result
    result = convert_emojis("Rocket 🚀 to the moon 🌙", "_")
    assert "rocket" in result and "crescent" in result
    assert convert_emojis("", "-") == ""


# --- transliterate_text ---
def test_transliterate_text_cyrillic():
    """Test transliteration of Cyrillic text and empty input."""
    assert transliterate_text("Привет мир") == "Privet mir"
    assert transliterate_text("Москва") == "Moskva"
    assert transliterate_text("") == ""


def test_transliterate_text_greek():
    """Test transliteration of Greek text."""
    assert transliterate_text("Γειά σου Κόσμε") == "Geia sou Kosme"
    assert transliterate_text("Αθήνα") == "Athina"


# --- extract_words ---
def test_extract_words_default():
    """Test word extraction with default regex and empty input."""
    assert extract_words("Hello, world!", None) == ["Hello", "world"]
    assert extract_words("", None) == []


def test_extract_words_custom_regex():
    """Test word extraction with a custom regex (capitalized words only)."""
    assert extract_words("The Quick Brown Fox", r"[A-Z][a-z]+") == [
        "The",
        "Quick",
        "Brown",
        "Fox",
    ]


# --- filter_stopwords ---
def test_filter_stopwords_basic():
    """Test stopword filtering with/without stopwords and empty input."""
    words = ["the", "quick", "brown", "fox"]
    stop = ["the", "fox"]
    assert filter_stopwords(words, stop, True) == ["quick", "brown"]
    assert filter_stopwords(words, stop, False) == ["quick", "brown"]
    # No stopwords
    assert filter_stopwords(words, None, True) == words
    # Empty word list
    assert filter_stopwords([], stop, True) == []


def test_filter_stopwords_case():
    """Test stopword filtering with case sensitivity on and off."""
    words = ["The", "Quick", "Brown", "Fox"]
    stop = ["the", "fox"]
    assert filter_stopwords(words, stop, True) == ["Quick", "Brown"]
    assert filter_stopwords(words, stop, False) == ["The", "Quick", "Brown", "Fox"]


# --- join_words ---
def test_join_words_basic():
    """Test joining words with various separators and empty input."""
    assert join_words(["foo", "bar"], "-") == "foo-bar"
    assert join_words([], "-") == ""
    assert join_words(["a"], "*") == "a"


# --- to_lowercase ---
def test_to_lowercase_basic():
    """Test to_lowercase with uppercase, mixed case, and empty input."""
    assert to_lowercase("HELLO") == "hello"
    assert to_lowercase("Hello World") == "hello world"
    assert to_lowercase("") == ""


# --- strip_separators ---
def test_strip_separators_basic():
    """Test stripping leading/trailing separators from strings."""
    assert strip_separators("--foo-bar--", "-") == "foo-bar"
    assert strip_separators("__foo__", "_") == "foo"
    assert strip_separators("foo", "-") == "foo"
    assert strip_separators("", "-") == ""
