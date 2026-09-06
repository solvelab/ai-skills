"""Percentage change between two readings."""


def percent_change(old, new):
    """Return the change from `old` to `new` as a percentage of `old`."""
    return (new - old) / old * 100.0
