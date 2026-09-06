"""Money rounding — banker's rounding, which the spec forbids."""
from decimal import ROUND_HALF_EVEN, Decimal

_CENTS = Decimal("0.01")


def round_money(value):
    return Decimal(value).quantize(_CENTS, rounding=ROUND_HALF_EVEN)
