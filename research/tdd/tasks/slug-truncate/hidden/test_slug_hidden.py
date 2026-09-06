import pytest

from slug import slugify


def test_basic_slug():
    assert slugify("Hello World", 50) == "hello-world"


def test_punctuation_becomes_a_single_hyphen():
    assert slugify("Hello,   World!!", 50) == "hello-world"


def test_short_enough_is_untouched():
    assert slugify("abc", 10) == "abc"


def test_truncates_at_a_word_boundary():
    assert slugify("the quick brown fox", 13) == "the-quick"


def test_never_ends_with_a_hyphen():
    assert not slugify("the quick brown fox", 10).endswith("-")


def test_empty_text_is_empty_slug():
    assert slugify("", 10) == ""


def test_text_with_no_word_characters_is_empty_slug():
    assert slugify("!!! ???", 10) == ""


def test_single_word_longer_than_max_len_is_empty():
    assert slugify("antidisestablishmentarianism", 5) == ""


def test_non_positive_max_len_is_rejected():
    with pytest.raises(ValueError):
        slugify("hello", 0)
