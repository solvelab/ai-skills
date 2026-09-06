from datetime import date

import pytest

from daterange import date_range


def test_end_is_exclusive():
    assert date_range(date(2026, 1, 1), date(2026, 1, 4)) == [
        date(2026, 1, 1), date(2026, 1, 2), date(2026, 1, 3)]


def test_same_day_is_empty():
    assert date_range(date(2026, 1, 1), date(2026, 1, 1)) == []


def test_single_day():
    assert date_range(date(2026, 1, 1), date(2026, 1, 2)) == [date(2026, 1, 1)]


def test_crosses_month_boundary():
    assert date_range(date(2026, 1, 30), date(2026, 2, 2)) == [
        date(2026, 1, 30), date(2026, 1, 31), date(2026, 2, 1)]


def test_crosses_leap_day():
    assert date(2028, 2, 29) in date_range(date(2028, 2, 28), date(2028, 3, 1))


def test_end_before_start_is_rejected():
    with pytest.raises(ValueError):
        date_range(date(2026, 1, 5), date(2026, 1, 1))
