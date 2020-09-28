"""Test the :class:`~polymatheia.data.reader.LocalReader`."""
import os
import pytest

from json import JSONDecodeError

from polymatheia.data.reader import LocalReader


def test_local_reader():
    """Test that the basic local reading works."""
    count = 0
    for record in LocalReader('tests/fixtures/local_reader_test'):
        assert record
        assert record.header
        assert record.metadata
        count = count + 1
    assert count == 10


def test_local_reader_removed_file():
    """Test that the local reader aborts on missing files."""
    with open('tests/fixtures/local_reader_test/temp.json', 'w') as _:
        pass
    reader = LocalReader('tests/fixtures/local_reader_test')
    os.unlink('tests/fixtures/local_reader_test/temp.json')
    with pytest.raises(FileNotFoundError):
        for record in reader:
            assert record


def test_local_reader_invalid_file():
    """Test that the local reader aborts on invalid files."""
    with pytest.raises(JSONDecodeError):
        for record in LocalReader('tests/fixtures/local_reader_invalid_test'):
            assert record
