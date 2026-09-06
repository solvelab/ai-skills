"""Duration parsing."""
import re

_UNITS = {"h": 3600, "m": 60, "s": 1}
_PART = re.compile(r"(\d+)([hms])")


def parse_duration(text):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("empty duration")
    rest = text.strip()
    total = 0
    seen = 0
    for match in _PART.finditer(rest):
        total += int(match.group(1)) * _UNITS[match.group(2)]
        seen += len(match.group(0))
    if seen != len(rest):
        raise ValueError("bad duration: " + text)
    return total
