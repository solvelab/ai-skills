import pytest

from duration import parse_duration


def test_single_unit():
    assert parse_duration("90s") == 90


def test_combined_units():
    assert parse_duration("1h30m") == 5400


def test_all_three_units():
    assert parse_duration("2h3m4s") == 7384


def test_zero_is_allowed():
    assert parse_duration("0s") == 0


def test_empty_string_is_rejected():
    with pytest.raises(ValueError):
        parse_duration("")


def test_bare_number_is_rejected():
    with pytest.raises(ValueError):
        parse_duration("90")


def test_unknown_unit_is_rejected():
    with pytest.raises(ValueError):
        parse_duration("5d")


def test_trailing_garbage_is_rejected():
    with pytest.raises(ValueError):
        parse_duration("1h30")
