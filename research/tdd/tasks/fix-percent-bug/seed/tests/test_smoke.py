from percent import percent_change


def test_the_suite_runs():
    assert percent_change(100.0, 150.0) == 50.0
