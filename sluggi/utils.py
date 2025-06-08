"""Shared utility functions for sluggi (truncate, smart_truncate, etc)."""


def truncate_slug(
    slug: str,
    max_length: int,
    word_boundary: bool = True,
    separator: str = "-",
) -> str:
    """Truncate a slug to a specified max_length."""
    if not isinstance(slug, str):
        raise TypeError("slug must be a string")
    if max_length is not None and max_length < 1:
        raise ValueError("max_length must be a positive integer")
    if max_length is None or len(slug) <= max_length:
        return slug
    if not word_boundary:
        return slug[:max_length].rstrip(separator)
    words = slug.split(separator)
    non_empty_words = [w for w in words if w]
    if not non_empty_words:
        return ""
    result = []
    total = 0
    sep_len = len(separator)
    for i, word in enumerate(words):
        if not word:
            continue
        # Calculate added length if this word is included
        added = len(word)
        if result:
            added += sep_len
        if total + added > max_length:
            break
        result.append(word)
        total += added
    if not result:
        # If no word fits, truncate the first word
        return words[0][:max_length]
    return separator.join(result)
