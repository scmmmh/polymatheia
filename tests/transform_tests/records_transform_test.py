"""Tests for the :class:`~polymatheia.transform.RecordsTransform`."""
from polymatheia.data.reader import LocalReader
from polymatheia.transform import RecordsTransform


def test_apply_iterator_transform():
    """Test that the iteration transform works."""
    reader = LocalReader('tests/fixtures/local_reader_test')
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
