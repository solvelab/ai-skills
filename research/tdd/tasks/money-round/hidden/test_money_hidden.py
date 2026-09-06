from decimal import Decimal

from money import round_money


def test_rounds_half_up():
    assert round_money(Decimal("2.345")) == Decimal("2.35")


def test_half_up_is_not_bankers_rounding():
    assert round_money(Decimal("2.325")) == Decimal("2.33")


def test_negative_half_rounds_away_from_zero():
    assert round_money(Decimal("-2.345")) == Decimal("-2.35")


def test_already_two_places_is_unchanged():
    assert round_money(Decimal("10.10")) == Decimal("10.10")


def test_rounds_down_below_half():
    assert round_money(Decimal("2.344")) == Decimal("2.34")


def test_zero():
    assert round_money(Decimal("0")) == Decimal("0.00")


def test_result_always_has_two_places():
    assert str(round_money(Decimal("5"))) == "5.00"
