"""Tests for the :mod:`~polymatheia.data.writer` package."""
import os

from shutil import rmtree

from polymatheia.data.reader import OAIRecordReader
from polymatheia.data.writer import LocalWriter


def test_local_writing():
    """Test writing to the local filesystem."""
    rmtree('tmp/local_writer_test', ignore_errors=True)
    reader = OAIRecordReader('https://digital.iai.spk-berlin.de/viewer/oai', max_records=10)
    writer = LocalWriter('tmp/local_writer_test', 'header.identifier')
    writer.write(reader)
    count = 0
    for _, _, filenames in os.walk('tmp/local_writer_test'):
        count = count + len(filenames)
    assert count == 10


def test_local_writing_pre_split_id_path():
    """Test writing to the local filesystem."""
    rmtree('tmp/local_writer_test', ignore_errors=True)
    reader = OAIRecordReader('https://digital.iai.spk-berlin.de/viewer/oai', max_records=10)
    writer = LocalWriter('tmp/local_writer_test', ['header', 'identifier'])
    writer.write(reader)
    count = 0
    for _, _, filenames in os.walk('tmp/local_writer_test'):
        count = count + len(filenames)
    assert count == 10
