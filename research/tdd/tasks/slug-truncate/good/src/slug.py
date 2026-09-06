"""Slugs — truncated at a word boundary, never ending in a hyphen."""
import re

_NON_WORD = re.compile(r"[^a-z0-9]+")


def slugify(text, max_len):
    if max_len <= 0:
        raise ValueError("max_len must be positive")
    slug = _NON_WORD.sub("-", (text or "").lower()).strip("-")
    if not slug:
        return ""
    if len(slug) <= max_len:
        return slug
    cut = slug[:max_len]
    if "-" not in cut:
        return ""
    return cut[:cut.rindex("-")].strip("-")
