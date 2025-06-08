"""Property-based tests for sluggi using Hypothesis.

Covers invariants and edge cases for slugify and batch_slugify.
"""

from hypothesis import given
from hypothesis import strategies as st

from sluggi import batch_slugify, slugify


@given(st.text())
def test_slugify_output_is_string(s):
    """Test that slugify always returns a string."""
    out = slugify(s)
    assert isinstance(out, str)


@given(st.text())
def test_slugify_no_whitespace(s):
    """Test that slugify output contains no whitespace characters."""
    out = slugify(s)
    assert all(c not in out for c in [" ", "\t", "\n", "\r"])


@given(st.text(), st.integers(min_value=1, max_value=100))
def test_slugify_max_length(s, max_length):
    """Test that slugify output never exceeds max_length."""
    out = slugify(s, max_length=max_length)
    assert len(out) <= max_length


@given(st.text())
def test_slugify_idempotent_ascii(s):
    """Test slugify is idempotent for ASCII-safe outputs only."""
    out1 = slugify(s)
    # Only check idempotency if the output is pure ASCII
    if all(ord(c) < 128 for c in out1):
        out2 = slugify(out1)
        assert out1 == out2


@given(st.lists(st.text(), min_size=1, max_size=10))
def test_batch_slugify_outputs_match(slugs):
    """Test batch_slugify returns a list of equal length and string outputs."""
    outs = batch_slugify(slugs)
    assert isinstance(outs, list)
    assert len(outs) == len(slugs)
    for out in outs:
        assert isinstance(out, str)
        assert all(c not in out for c in [" ", "\t", "\n", "\r"])


@given(st.text())
def test_slugify_custom_map_applies_to_range(s):
    """Test custom_map for codepoints 128-255 is applied by slugify."""
    custom_map = {chr(i): "x" for i in range(128, 256)}
    out = slugify(s, custom_map=custom_map)
    # For each char in input that is in the mapped range, ensure 'x' appears in
    # output if that char was present
    for c in s:
        if 128 <= ord(c) < 256:
            assert "x" in out or out == ""


@given(st.text())
def test_slugify_no_leading_trailing_separator(s):
    """Test slugify output has no leading or trailing separator."""
    out = slugify(s)
    assert not out.startswith("-") and not out.endswith("-")


@given(st.lists(st.text(), min_size=1, max_size=10))
def test_batch_slugify_idempotent_ascii(slugs):
    """Test batch_slugify is idempotent for ASCII-only outputs."""
    outs1 = batch_slugify(slugs)
    # Only check idempotency for outputs that are pure ASCII
    if all(all(ord(c) < 128 for c in out) for out in outs1):
        outs2 = batch_slugify(outs1)
        assert outs1 == outs2
