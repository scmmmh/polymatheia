"""Test the :class:`~polymatheia.data.reader.LocalReader`."""
import os
import pytest

from lxml.etree import XMLSyntaxError

from polymatheia.data.reader import XMLReader


def test_xml_reader():
    """Test that the XML local reading works."""
    count = 0
    for record in XMLReader('tests/fixtures/xml_reader_test'):
        assert record
        assert record.id
        assert record.name.first
        assert record.name.last
        assert record.age
        if record.id == '1':
            assert len(record.name.first) == 2
            assert record['special-tags']
        count = count + 1
    assert count == 3


def test_xml_reader_removed_file():
    """Test that the XML reader aborts on missing files."""
    with open('tests/fixtures/xml_reader_test/temp.xml', 'w') as _:
        pass
    reader = XMLReader('tests/fixtures/xml_reader_test')
    os.unlink('tests/fixtures/xml_reader_test/temp.xml')
    with pytest.raises(FileNotFoundError):
        for record in reader:
            assert record


def test_xml_reader_invalid_file():
    """Test that the XML reader aborts on invalid files."""
    with pytest.raises(XMLSyntaxError):
        for record in XMLReader('tests/fixtures/xml_reader_invalid_test'):
            assert record
