"""sluggi: Utilities for generating URL-safe slugs and batch processing."""

__version__ = "0.1.1"
from .api import (
    SlugPipeline,
    async_batch_slugify,
    async_slugify,
    batch_slugify,
    emoji,
    slugify,
)

__all__ = [
    "SlugPipeline",
    "__version__",
    "async_batch_slugify",
    "async_slugify",
    "batch_slugify",
    "slugify",
    "emoji",
]
