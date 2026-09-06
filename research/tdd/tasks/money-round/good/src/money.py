"""Money rounding — half away from zero, two decimal places."""
from decimal import ROUND_HALF_UP, Decimal

_CENTS = Decimal("0.01")


def round_money(value):
    return Decimal(value).quantize(_CENTS, rounding=ROUND_HALF_UP)
