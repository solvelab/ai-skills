import pytest

from percent import percent_change


def test_increase():
    assert percent_change(100.0, 150.0) == 50.0


def test_decrease():
    assert percent_change(200.0, 150.0) == -25.0


def test_no_change():
    assert percent_change(100.0, 100.0) == 0.0


def test_negative_baseline_still_divides_by_it():
    assert percent_change(-100.0, -50.0) == -50.0


def test_zero_to_zero_is_no_change():
    assert percent_change(0.0, 0.0) == 0.0


def test_zero_baseline_with_a_real_new_value_is_rejected():
    with pytest.raises(ValueError):
        percent_change(0.0, 10.0)


def test_zero_baseline_does_not_raise_zero_division_error():
    with pytest.raises(ValueError):
        percent_change(0.0, -3.0)
