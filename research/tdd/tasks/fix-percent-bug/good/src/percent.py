"""Percentage change between two readings."""


def percent_change(old, new):
    """Return the change from `old` to `new` as a percentage of `old`."""
    if old == 0:
        if new == 0:
            return 0.0
        raise ValueError("percentage change from zero is undefined")
    return (new - old) / old * 100.0
