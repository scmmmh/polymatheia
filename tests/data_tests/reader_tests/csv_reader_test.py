"""Tests for the :class:`~polymatheia.data.reader.CSVReader`."""
from polymatheia.data.reader import CSVReader


def test_read_from_filename():
    """Test reading from a filename."""
    reader = CSVReader('tests/fixtures/csv_reader_test/example_csv.csv')
    count = 0
    for record in reader:
        assert record.id
        assert record.set
        assert record.title
        count = count + 1
    assert count == 10


def test_read_from_filename_repeat():
    """Test that repeated iteration from a filename works."""
    reader = CSVReader('tests/fixtures/csv_reader_test/example_csv.csv')
    assert len(list(reader)) == len(list(reader))


def test_read_from_file():
    """Test reading from an already opened file."""
    with open('tests/fixtures/csv_reader_test/example_csv.csv') as in_file:
        reader = CSVReader(in_file)
        count = 0
        for record in reader:
            assert record.id
            assert record.set
            assert record.title
            count = count + 1
        assert count == 10
