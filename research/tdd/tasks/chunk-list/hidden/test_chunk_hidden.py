import pytest

from chunk import chunk


def test_exact_multiple():
    assert chunk([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_last_chunk_is_short():
    assert chunk([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]


def test_empty_input_is_empty_output():
    assert chunk([], 3) == []


def test_size_larger_than_input():
    assert chunk([1, 2], 10) == [[1, 2]]


def test_size_of_one():
    assert chunk([1, 2, 3], 1) == [[1], [2], [3]]


def test_zero_size_is_rejected():
    with pytest.raises(ValueError):
        chunk([1, 2, 3], 0)


def test_negative_size_is_rejected():
    with pytest.raises(ValueError):
        chunk([1, 2, 3], -1)


def test_input_is_not_mutated():
    items = [1, 2, 3]
    chunk(items, 2)
    assert items == [1, 2, 3]
