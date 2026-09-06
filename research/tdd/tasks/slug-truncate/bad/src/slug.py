"""Slugs — hard truncation, so a slug can end mid-word or on a hyphen."""
import re

_NON_WORD = re.compile(r"[^a-z0-9]+")


def slugify(text, max_len):
    if max_len <= 0:
        raise ValueError("max_len must be positive")
    slug = _NON_WORD.sub("-", (text or "").lower()).strip("-")
    return slug[:max_len]
