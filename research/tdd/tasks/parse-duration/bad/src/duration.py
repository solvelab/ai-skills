"""Duration parsing — accepts a bare number, which the spec forbids."""
import re

_UNITS = {"h": 3600, "m": 60, "s": 1}
_PART = re.compile(r"(\d+)([hms]?)")


def parse_duration(text):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("empty duration")
    total = 0
    for match in _PART.finditer(text.strip()):
        total += int(match.group(1)) * _UNITS.get(match.group(2) or "s", 1)
    return total
