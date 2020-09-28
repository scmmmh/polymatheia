"""Test the :class:`~polymatheia.data.reader.LocalReader`."""
import os
import pytest

from json import JSONDecodeError

from polymatheia.data.reader import JSONReader


def test_json_reader():
    """Test that the JSON local reading works."""
    count = 0
    for record in JSONReader('tests/fixtures/json_reader_test'):
        assert record
        assert record.id
        assert record.name.first
        assert record.name.last
        assert record.age
        if record.id == '1':
            assert record['special tags']
        if record.id == '2':
            assert len(record.name.first) == 2
        count = count + 1
    assert count == 3


def test_json_reader_removed_file():
    """Test that the JSON reader aborts on missing files."""
    with open('tests/fixtures/json_reader_test/temp.json', 'w') as _:
        pass
    reader = JSONReader('tests/fixtures/json_reader_test')
    os.unlink('tests/fixtures/json_reader_test/temp.json')
    with pytest.raises(FileNotFoundError):
        for record in reader:
            assert record


def test_json_reader_invalid_file():
    """Test that the JSON reader aborts on invalid files."""
    with pytest.raises(JSONDecodeError):
        for record in JSONReader('tests/fixtures/json_reader_invalid_test'):
            assert record
