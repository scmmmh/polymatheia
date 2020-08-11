"""Tests for the :class:`~polymatheia.filter.Filter`."""
from polymatheia.data import NavigableDict
from polymatheia.filter import Filter


def test_equal_filter():
    """Test the equality filter."""
    fltr = Filter(('eq', 'a.one', 1))
    assert fltr(NavigableDict({'a': {'one': 1}})) is True
    assert fltr(NavigableDict({'a': {'one': 2}})) is False
    assert fltr(NavigableDict({'a': {'one': '1'}})) is False
    fltr = Filter(('eq', 'a.one', '1'))
    assert fltr(NavigableDict({'a': {'one': '1'}})) is True
    assert fltr(NavigableDict({'a': {'one': 1}})) is False
    assert fltr(NavigableDict({'b': {'one': 1}})) is False
    fltr = Filter(('eq', 'a.one', 'b.one'))
    assert fltr(NavigableDict({'a': {'one': '1'}, 'b': {'one': '1'}})) is True
    assert fltr(NavigableDict({'a': {'one': '1'}, 'b': {'one': '2'}})) is False
    assert fltr(NavigableDict({'a': {'one': '1'}, 'b': {'one': 1}})) is False
    assert fltr(NavigableDict({'a': {'one': '1'}})) is False
    fltr = Filter(('eq', 'a', 'b'))
    assert fltr(NavigableDict({'a': 1, 'b': 1})) is False
    assert fltr(NavigableDict({'a': 2, 'b': 1})) is False
    assert fltr(NavigableDict({'a': 1, 'b': 2})) is False
    fltr = Filter(('eq', ['a'], ['b']))
    assert fltr(NavigableDict({'a': 1, 'b': 1})) is True
    assert fltr(NavigableDict({'a': 2, 'b': 1})) is False
    assert fltr(NavigableDict({'a': 1, 'b': 2})) is False


def test_not_equal_filter():
    """Test the not-equal filter."""
    fltr = Filter(('neq', 'a.one', 1))
    assert fltr(NavigableDict({'a': {'one': 1}})) is False
    assert fltr(NavigableDict({'a': {'one': 2}})) is True
    assert fltr(NavigableDict({'a': {'one': '1'}})) is True
    fltr = Filter(('neq', 'a.one', '1'))
    assert fltr(NavigableDict({'a': {'one': '1'}})) is False
    assert fltr(NavigableDict({'a': {'one': 1}})) is True
    assert fltr(NavigableDict({'b': {'one': 1}})) is True


def test_greater_than_filter():
    """Test the greater than filter."""
    fltr = Filter(('gt', 'a.one', 3))
    assert fltr(NavigableDict({'a': {'one': 5}})) is True
    assert fltr(NavigableDict({'a': {'one': 3}})) is False
    assert fltr(NavigableDict({'a': {'one': 2}})) is False


def test_greater_than_or_equal_filter():
    """Test the greater than or equal filter."""
    fltr = Filter(('gte', 'a.one', 3))
    assert fltr(NavigableDict({'a': {'one': 5}})) is True
    assert fltr(NavigableDict({'a': {'one': 3}})) is True
    assert fltr(NavigableDict({'a': {'one': 2}})) is False


def test_less_than_filter():
    """Test the less than filter."""
    fltr = Filter(('lt', 'a.one', 3))
    assert fltr(NavigableDict({'a': {'one': 1}})) is True
    assert fltr(NavigableDict({'a': {'one': 3}})) is False
    assert fltr(NavigableDict({'a': {'one': 4}})) is False


def test_less_than_or_equal_filter():
    """Test the less than or equal filter."""
    fltr = Filter(('lte', 'a.one', 3))
    assert fltr(NavigableDict({'a': {'one': 1}})) is True
    assert fltr(NavigableDict({'a': {'one': 3}})) is True
    assert fltr(NavigableDict({'a': {'one': 4}})) is False


def test_not_filter():
    """Test the not filter."""
    fltr = Filter(('not', ('eq', 'a.one', 1)))
    assert fltr(NavigableDict({'a': {'one': 1}})) is False
    assert fltr(NavigableDict({'a': {'one': 2}})) is True
    assert fltr(NavigableDict({'a': {'one': '1'}})) is True


def test_empty_not_filter():
    """Test the not filter."""
    fltr = Filter(('not',))
    assert fltr(NavigableDict({'a': {'one': 1}})) is True
    assert fltr(NavigableDict({'a': {'one': 2}})) is True
    assert fltr(NavigableDict({'a': {'one': '1'}})) is True


def test_and_filter():
    """Test the and filter."""
    fltr = Filter(('and',))
    assert fltr(NavigableDict({'a': {'one': 1}})) is True
    fltr = Filter(('and', ('eq', 'a.one', 1)))
    assert fltr(NavigableDict({'a': {'one': 1}})) is True
    assert fltr(NavigableDict({'a': {'one': 2}})) is False
    assert fltr(NavigableDict({'a': {'one': '1'}})) is False
    fltr = Filter(('and', ('eq', 'a.one', 1), ('eq', 'b.one', 1)))
    assert fltr(NavigableDict({'a': {'one': 1}, 'b': {'one': 1}})) is True
    assert fltr(NavigableDict({'a': {'one': 2}, 'b': {'one': 1}})) is False
    assert fltr(NavigableDict({'a': {'one': 1}, 'b': {'one': 2}})) is False
    assert fltr(NavigableDict({'a': {'one': 2}, 'b': {'one': 2}})) is False


def test_or_filter():
    """Test the or filter."""
    fltr = Filter(('or',))
    assert fltr(NavigableDict({'a': {'one': 1}})) is True
    fltr = Filter(('or', ('eq', 'a.one', 1)))
    assert fltr(NavigableDict({'a': {'one': 1}})) is True
    assert fltr(NavigableDict({'a': {'one': 2}})) is False
    assert fltr(NavigableDict({'a': {'one': '1'}})) is False
    fltr = Filter(('or', ('eq', 'a.one', 1), ('eq', 'b.one', 1)))
    assert fltr(NavigableDict({'a': {'one': 1}, 'b': {'one': 1}})) is True
    assert fltr(NavigableDict({'a': {'one': 2}, 'b': {'one': 1}})) is True
    assert fltr(NavigableDict({'a': {'one': 1}, 'b': {'one': 2}})) is True
    assert fltr(NavigableDict({'a': {'one': 2}, 'b': {'one': 2}})) is False


def test_unknown_filter():
    """Test that an unknown filter works."""
    fltr = Filter(('does_not_exist', 'a.one', 1))
    assert fltr(NavigableDict({'a': {'one': 1}})) is False


def test_true_filter():
    """Test the true filter."""
    fltr = Filter(('true',))
    assert fltr(NavigableDict({'a': {'one': 1}})) is True
    assert fltr(NavigableDict({'a': {'one': 2}})) is True
    assert fltr(NavigableDict({'a': {'one': '1'}})) is True


def test_false_filter():
    """Test the false filter."""
    fltr = Filter(('false',))
    assert fltr(NavigableDict({'a': {'one': 1}})) is False
    assert fltr(NavigableDict({'a': {'one': 2}})) is False
    assert fltr(NavigableDict({'a': {'one': '1'}})) is False


def test_contains_filter():
    """Test the contains filter."""
    fltr = Filter(('contains', ['a'], '2'))
    assert fltr(NavigableDict({'a': ['1', '2', '3']})) is True
    assert fltr(NavigableDict({'a': '2'})) is True
    assert fltr(NavigableDict({'a': [1, 2, 3]})) is False
