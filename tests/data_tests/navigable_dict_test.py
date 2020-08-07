"""Tests for the :class:`~polymatheia.data.NavigableDict`."""
import json
import pytest

from polymatheia.data import NavigableDict


def test_basic_get_value():
    """Test that accessing a single value works."""
    tmp = NavigableDict({'a': 1})
    assert tmp.a == 1
    assert tmp['a'] == 1
    assert tmp['a'] == tmp.a


def test_nested_get_value():
    """Test that accessing a nested value works."""
    tmp = NavigableDict({'a': {'one': 1}})
    assert tmp.a.one == 1
    assert tmp['a'].one == 1
    assert tmp['a']['one'] == 1
    assert tmp['a']['one'] == tmp.a.one
    assert tmp.get('a.one') == 1


def test_fail_missing():
    """Test that accessing a missing value throws an exception."""
    tmp = NavigableDict({'a': 1})
    with pytest.raises(KeyError):
        tmp.b


def test_fail_missing_default():
    """Test that accessing a mising value with a default returns the default."""
    tmp = NavigableDict({'a': 1})
    assert tmp.get('b') is None
    assert tmp.get('b', default=2) == 2


def test_basic_set_value():
    """Test that setting a single value works."""
    tmp = NavigableDict({'a': 1})
    assert tmp.a == 1
    tmp.a = 2
    assert tmp.a == 2
    assert tmp['a'] == 2


def test_nested_set_value():
    """Test that setting a nested value works and coerces the nested value."""
    tmp = NavigableDict({'a': 1})
    tmp.a = {'one': 1}
    assert tmp['a'].one == 1
    assert tmp['a']['one'] == 1
    assert tmp['a']['one'] == tmp.a.one


def test_nested_nd_set_value():
    """Test that setting a :class:`~polymatheia.data.NavigableDict` does not needlessly coerce."""
    tmp = NavigableDict({'a': 1})
    tmp.a = NavigableDict({'one': 1})
    assert tmp['a'].one == 1
    assert tmp['a']['one'] == 1
    assert tmp['a']['one'] == tmp.a.one


def test_delete_value():
    """Test that deleting a value works."""
    tmp = NavigableDict({'a': 1})
    assert tmp.a == 1
    del tmp.a
    with pytest.raises(KeyError):
        tmp.a


def test_json_str():
    """Test that the str representation is a JSON serialisation."""
    tmp = NavigableDict({'a': {'one': 1}, 'b': 2})
    assert json.loads(str(tmp)) == tmp


def test_nested_list():
    """Test that nested lists are correctly coerced."""
    tmp = NavigableDict({'a': [{'one': 1}, NavigableDict({'two': 2}), 3]})
    assert tmp.a[0].one == 1
    assert tmp.a[1].two == 2
    assert tmp.a[2] == 3
    assert tmp.get('a.0.one') == 1
    assert tmp.get('a[0].one') == 1
    assert tmp.get('a.1.two') == 2
    assert tmp.get('a.2') == 3


def test_nested_list_fail():
    """Test that nested lists are correctly coerced."""
    tmp = NavigableDict({'a': [{'one': 1}, NavigableDict({'two': 2}), 3]})
    assert tmp.get('a[4].one') is None


def test_nested_list_get():
    """Test that invalid list access is handled correctly."""
    tmp = NavigableDict({'a': [{'one': 1}, {'one': 2}, 3]})
    assert tmp.get('a.one') == [1, 2, None]


def test_setting_dotted_path():
    """Test that setting a value via a dotted path creates the required structure."""
    tmp = NavigableDict({})
    tmp.set('data.type', 'tests')
    tmp.set('data.id', '1')
    assert tmp.data.type == 'tests'
    assert tmp.data.id == '1'


def test_setting_list_path():
    """Test that setting a value via a dotted path creates the required structure."""
    tmp = NavigableDict({})
    tmp.set(['data', 'type'], 'tests')
    tmp.set(['data', 'id'], '1')
    assert tmp.data.type == 'tests'
    assert tmp.data.id == '1'


def test_setting_dotted_path_list_value():
    """Test that setting a value via a dotted path creates the required structure."""
    tmp = NavigableDict({'data': {'numbers': [1, 2, 3]}})
    tmp.set('data.numbers.0', 4)
    tmp.set('data.numbers.2', 0)
    assert tmp.data.numbers[0] == 4
    assert tmp.data.numbers[2] == 0
