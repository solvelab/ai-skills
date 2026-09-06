"""Percentage change — the zero case patched into a sentinel instead of the documented behaviour."""


def percent_change(old, new):
    """Return the change from `old` to `new` as a percentage of `old`."""
    if old == 0:
        return 0.0
    return (new - old) / old * 100.0
