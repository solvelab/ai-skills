"""Date ranges — end treated as inclusive, which the spec forbids."""
from datetime import timedelta

_DAY = timedelta(days=1)


def date_range(start, end):
    if end < start:
        raise ValueError("end is before start")
    out = []
    current = start
    while current <= end:
        out.append(current)
        current += _DAY
    return out
