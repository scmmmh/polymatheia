"""Tests for the :class:`~polymatheia.filter.RecordsFilter`."""
from polymatheia.data.reader import LocalReader
from polymatheia.filter import Filter, RecordsFilter


def test_true_filter():
    """Tests filtering with the basic true filter."""
    reader = LocalReader('tests/fixtures/local_reader_test')
    count = 0
    for _ in RecordsFilter(reader, ('true',)):
        count = count + 1
    assert count == 10


def test_existing_true_filter():
    """Tests filtering with an existing :class:`~polymatheia.filter.Filter``."""
    reader = LocalReader('tests/fixtures/local_reader_test')
    fltr = Filter(('true',))
    count = 0
    for _ in RecordsFilter(reader, fltr):
        count = count + 1
    assert count == 10


def test_false_filter():
    """Tests a filter that filters out everything."""
    reader = LocalReader('tests/fixtures/local_reader_test')
    count = 0
    for _ in RecordsFilter(reader, ('false',)):
        count = count + 1
    assert count == 0


def test_very_limited_filter():
    """Tests a very limited filter."""
    reader = LocalReader('tests/fixtures/local_reader_test')
    count = 0
    for _ in RecordsFilter(reader, ('eq', 'header.identifier._text', '757662544')):
        count = count + 1
    assert count == 1


def test_permissive_filter():
    """Tests a very permissive filter."""
    reader = LocalReader('tests/fixtures/local_reader_test')
    count = 0
    for _ in RecordsFilter(reader, ('eq', 'header.setSpec._text', 'argentinischetheaterundromanzeitschriften')):
        count = count + 1
    assert count == 10


def test_repeat_filter():
    """Tests that repeating the filter works."""
    reader = LocalReader('tests/fixtures/local_reader_test')
    filtered = RecordsFilter(reader, ('eq', 'header.setSpec._text', 'argentinischetheaterundromanzeitschriften'))
    assert len(list(filtered)) == len(list(filtered)) == 10


def test_filter_iterator():
    """Tests that repeating the filter works."""
    reader = LocalReader('tests/fixtures/local_reader_test')
    it = iter(RecordsFilter(reader, ('eq', 'header.setSpec._text', 'argentinischetheaterundromanzeitschriften')))
    assert it == iter(it)
