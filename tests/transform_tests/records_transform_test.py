"""Tests for the :class:`~polymatheia.transform.RecordsTransform`."""
from polymatheia.data.reader import JSONReader
from polymatheia.transform import RecordsTransform


def test_apply_iterator_transform():
    """Test that the iteration transform works."""
    reader = JSONReader('tests/fixtures/local_reader_test')
    transform = RecordsTransform(reader, [
        ('copy', 'id', 'header.identifier._text'),
        ('copy', 'set', 'header.setSpec._text'),
        ('copy', 'title', ['metadata', '{http://www.openarchives.org/OAI/2.0/oai_dc/}dc', 'dc_title', '_text'])
    ])
    count = 0
    for record in transform:
        assert record.id
        assert record.set
        assert record.title
        count = count + 1
    assert count == 10


def test_repeat_apply_iterator_transform():
    """Test that the repeat iteration transform works."""
    reader = JSONReader('tests/fixtures/local_reader_test')
    transform = RecordsTransform(reader, [
        ('copy', 'id', 'header.identifier._text'),
        ('copy', 'set', 'header.setSpec._text'),
        ('copy', 'title', ['metadata', '{http://www.openarchives.org/OAI/2.0/oai_dc/}dc', 'dc_title', '_text'])
    ])
    assert len(list(transform)) == len(list(transform)) == 10


def test_iterator():
    """Test that the repeat iteration transform works."""
    reader = JSONReader('tests/fixtures/local_reader_test')
    transform = RecordsTransform(reader, [
        ('copy', 'id', 'header.identifier._text'),
        ('copy', 'set', 'header.setSpec._text'),
        ('copy', 'title', ['metadata', '{http://www.openarchives.org/OAI/2.0/oai_dc/}dc', 'dc_title', '_text'])
    ])
    it = iter(transform)
    assert it == iter(it)
