"""Tests for the :class:`~polymatheia.data.NavigableDict`."""
from polymatheia.data import NavigableDict, NavigableDictIterator, LimitingIterator


def test_basic_iteration():
    """Test that the :class:`~polymatheia.data.NavigableDictIterator` follows the basic iterator protocol."""
    it = NavigableDictIterator(iter([{'a': 1}, {'a': 2}, {'a': 3}]))
    count = 0
    for record in it:
        assert isinstance(record, NavigableDict)
        assert record.a is not None
        count = count + 1
    assert count == 3
    count = 0
    for _ in it:
        count = count + 1
    assert count == 0


def test_mapper_iteration():
    """Test that the mapper function works as desired."""
    it = NavigableDictIterator(iter([1, 2, 3]), mapper=lambda v: {'a': v})
    count = 0
    for record in it:
        assert isinstance(record, NavigableDict)
        assert record.a is not None
        count = count + 1
    assert count == 3


def test_default_value_iteration():
    """Test that the default handling of value mapping works correctly."""
    it = NavigableDictIterator(iter([1, 2, 3]))
    count = 0
    for record in it:
        assert isinstance(record, NavigableDict)
        assert record.value is not None
        count = count + 1
    assert count == 3


def test_limiting_iterator():
    """Test that the LimitingIterator limits iteration correctly."""
    assert len(list(LimitingIterator(iter([1, 2, 3, 4, 5]), 3))) == 3
    assert len(list(LimitingIterator(iter([1, 2, 3, 4, 5]), -1))) == 0
    assert len(list(LimitingIterator(iter([1, 2, 3, 4, 5]), 8))) == 5
