"""Tests for the :class:`~polymatheia.data.writer.PandasDFWriter`."""
import numpy as np

from polymatheia.data.reader import LocalReader, CSVReader
from polymatheia.data.writer import PandasDFWriter
from polymatheia.transform import RecordsTransform


def test_create_dataframe_from_transform():
    """Tests that a Pandas dataframe can be created from an iterator."""
    reader = LocalReader('tests/fixtures/local_reader_test')
    transform = RecordsTransform(reader, [
        ('copy', 'id', 'header.identifier._text'),
        ('copy', 'set', 'header.setSpec._text'),
        ('copy', 'title', ['metadata', '{http://www.openarchives.org/OAI/2.0/oai_dc/}dc', 'dc_title', '_text'])
    ])
    writer = PandasDFWriter()
    writer.write(transform)
    assert writer.df.columns.all(['id', 'set', 'title'])
    assert writer.df.shape == (10, 3)
    assert writer.df.dtypes[0] == np.dtype('O')
    assert writer.df.dtypes[1] == np.dtype('O')
    assert writer.df.dtypes[2] == np.dtype('O')


def test_create_dataframe_from_csv():
    """Tests that a Pandas dataframe can be created from an iterator and that data-types are coerced correctly."""
    reader = CSVReader('tests/fixtures/csv_reader_test/example_csv.csv')
    writer = PandasDFWriter()
    writer.write(reader)
    assert writer.df.columns.all(['id', 'set', 'title', 'length'])
    assert writer.df.shape == (10, 4)
    assert writer.df.dtypes[0] == np.dtype('O')
    assert writer.df.dtypes[1] == np.dtype('O')
    assert writer.df.dtypes[2] == np.dtype('O')
    assert writer.df.dtypes[3] == np.dtype('int64')
