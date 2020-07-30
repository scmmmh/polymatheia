"""Tests for the :class:`~polymatheia.transform.Transform`."""
from polymatheia.data import NavigableDict
from polymatheia.transform import Transform


def test_copy_transform():
    """Test the copy transformation."""
    record = NavigableDict({'a': {'one': {'_text': '1'}}, 'b': {'two': {'_text': '2'}}})
    transform = Transform([('copy', 'a', 'a.one._text'), ('copy', 'b', 'b.two._text')])
    result = transform(record)
    assert len(result) == 2
    assert result.a == '1'
    assert result.b == '2'


def test_static_transform():
    """Test the static transformation."""
    record = NavigableDict({'a': {'one': {'_text': '1'}}, 'b': {'two': {'_text': '2'}}})
    transform = Transform([('static', 'a', 'Test')])
    result = transform(record)
    assert len(result) == 1
    assert result.a == 'Test'


def test_split_string_transform():
    """Test the string splitting transformation."""
    record = NavigableDict({'a': {'_text': 'This is a test'}})
    transform = Transform([('split', 'a_{}', ' ', 'a._text')])
    result = transform(record)
    assert len(result) == 4
    assert result.a_1 == 'This'
    assert result.a_2 == 'is'
    assert result.a_3 == 'a'
    assert result.a_4 == 'test'


def test_split_list_transform():
    """Test the list splitting transformation."""
    record = NavigableDict({'a': {'tokens': ['This', 'is', 'a', 'test']}})
    transform = Transform([('split', 'a_{}', '', 'a.tokens')])
    result = transform(record)
    assert len(result) == 4
    assert result.a_1 == 'This'
    assert result.a_2 == 'is'
    assert result.a_3 == 'a'
    assert result.a_4 == 'test'


def test_combine_transform():
    """Test the combine transformation."""
    record = NavigableDict({'a': {'one': {'_text': '1'}}, 'b': {'two': {'_text': '2'}}})
    transform = Transform([('combine', 'a', 'a.one._text', 'b.two._text')])
    result = transform(record)
    assert len(result) == 1
    assert result.a == ['1', '2']


def test_join_list_transform():
    """Test the list joining transformation."""
    record = NavigableDict({'a': {'tokens': ['This', 'is', 'a', 'test']}})
    transform = Transform([('join', 'a', ' ', 'a.tokens')])
    result = transform(record)
    assert len(result) == 1
    assert result.a == 'This is a test'


def test_join_values_transform():
    """Test the value joining transformation."""
    record = NavigableDict({'a': {'one': {'_text': '1'}}, 'b': {'two': {'_text': '2'}}})
    transform = Transform([('join', 'a', ', ', 'a.one._text', 'b.two._text')])
    result = transform(record)
    assert len(result) == 1
    assert result.a == '1, 2'


def test_sequence_transform():
    """Test the sequence transformation."""
    record = NavigableDict({'a': {'one': {'_text': '1'}}, 'b': {'two': {'_text': '2'}}})
    transform = Transform([('sequence', ('combine', 'a', 'a.one._text', 'b.two._text'), ('join', 'a', ', ', 'a'))])
    result = transform(record)
    assert len(result) == 1
    assert result.a == '1, 2'


def test_multiple_transform():
    """Test that having multiple transformations together works."""
    record = NavigableDict({'a': {'one': {'_text': '1'}}, 'b': {'two': {'_text': '2'}}})
    transform = Transform([('copy', 'a', 'a.one._text'), ('copy', 'b', 'b.two._text'), ('static', 'c', 'Test')])
    result = transform(record)
    assert len(result) == 3
    assert result.a == '1'
    assert result.b == '2'
    assert result.c == 'Test'


def test_dotted_target_transform():
    """Tests that a dotted path as the target works."""
    record = NavigableDict({'a': {'one': {'_text': '1'}}, 'b': {'two': {'_text': '2'}}})
    transform = Transform([('copy', 'data.a', 'a.one._text'),
                           ('copy', 'data.b', 'b.two._text'),
                           ('static', 'data.c', 'Test')])
    result = transform(record)
    assert len(result) == 1
    assert result.data.a == '1'
    assert result.data.b == '2'
    assert result.data.c == 'Test'
