"""Tests for the :class:`~polymatheia.data.writer.CSVWriter`."""
import os

from csv import DictReader
from io import StringIO
from shutil import rmtree

from polymatheia.data.reader import JSONReader
from polymatheia.data.writer import CSVWriter
from polymatheia.transform import RecordsTransform


def test_csv_file_writing():
    """Test writing records to a local filename."""
    reader = JSONReader('tests/fixtures/local_reader_test')
    transform = RecordsTransform(reader, [
        ('copy', 'id', 'header.identifier._text'),
        ('copy', 'set', 'header.setSpec._text'),
        ('copy', 'title', ['metadata', '{http://www.openarchives.org/OAI/2.0/oai_dc/}dc', 'dc_title', '_text'])
    ])
    rmtree('tmp/csv_writer_test.csv', ignore_errors=True)
    writer = CSVWriter('tmp/csv_writer_test.csv')
    writer.write(transform)
    assert os.path.exists('tmp/csv_writer_test.csv')
    count = 0
    with open('tmp/csv_writer_test.csv') as in_file:
        for line in DictReader(in_file):
            assert 'id' in line
            assert 'set' in line
            assert 'title' in line
            count = count + 1
    assert count == 10


def test_csv_in_memory_writing():
    """Test that writing records to an existing file-like object works."""
    reader = JSONReader('tests/fixtures/local_reader_test')
    transform = RecordsTransform(reader, [
        ('copy', 'id', 'header.identifier._text'),
        ('copy', 'set', 'header.setSpec._text'),
        ('copy', 'title', ['metadata', '{http://www.openarchives.org/OAI/2.0/oai_dc/}dc', 'dc_title', '_text'])
    ])
    buffer = StringIO()
    writer = CSVWriter(buffer)
    writer.write(transform)
    buffer.seek(0)
    count = 0
    for line in DictReader(buffer):
        assert 'id' in line
        assert 'set' in line
        assert 'title' in line
        count = count + 1
    assert count == 10
