"""Async tests for the sluggi library.

Covers async_slugify and async_batch_slugify for correctness and edge cases.
"""

import pytest

from sluggi import async_batch_slugify, async_slugify

pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_async_slugify_basic():
    """Test async_slugify with basic ASCII input."""
    result = await async_slugify("Hello, world!")
    assert result == "hello-world"


@pytest.mark.asyncio
async def test_async_slugify_custom_separator():
    """Test async_slugify with a custom separator."""
    result = await async_slugify("Hello, world!", separator="_")
    assert result == "hello_world"


@pytest.mark.asyncio
async def test_async_slugify_custom_map():
    """Test async_slugify with a custom character mapping."""
    result = await async_slugify("ä ö ü", custom_map={"ä": "ae", "ö": "oe", "ü": "ue"})
    assert result == "ae-oe-ue"


@pytest.mark.asyncio
async def test_async_batch_slugify_serial():
    """Test async_batch_slugify on a list of mixed Unicode and ASCII strings
    (serial mode).
    """
    data = ["Hello, world!", "Café déjà vu", "Привет мир"]
    expected = ["hello-world", "cafe-deja-vu", "privet-mir"]
    result = await async_batch_slugify(data)
    assert result == expected


@pytest.mark.asyncio
async def test_async_batch_slugify_parallel():
    """Test async_batch_slugify with parallel processing enabled."""
    data = ["foo"] * 100
    # Use a small chunk_size to force parallel code path
    result = await async_batch_slugify(data, parallel=True, workers=4, chunk_size=10)
    assert result == ["foo"] * 100


@pytest.mark.asyncio
async def test_async_batch_slugify_empty():
    """Test async_batch_slugify with an empty list input."""
    result = await async_batch_slugify([])
    assert result == []


@pytest.mark.asyncio
async def test_async_batch_type_error():
    """Test async_batch_slugify raises TypeError on non-iterable input
    (error handling).
    """
    with pytest.raises(TypeError):
        await async_batch_slugify("not a list")
