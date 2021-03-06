"""Tests for the :mod:`~polymatheia.data.writer` package."""
import json
import os

from deprecation import fail_if_not_removed
from shutil import rmtree

from polymatheia.data import NavigableDict
from polymatheia.data.writer import LocalWriter


DOCUMENTS = [NavigableDict(r) for r in [
    {
        'id': '1',
        'name': {
            'first': 'A',
            'last': 'Person'
        },
        'age': 32,
        'special tags': 'The first'
    },
    {
        'id': '2',
        'name': {
            'first': ['Another', {'abbr': 'Nameless'}],
            'last': 'Parrot'
        },
        'age': 23,
    },
    {
        'id': '3',
        'name': {
            'first': 'The',
            'last': 'Last'
        },
        'age': 65,
    },
]]


@fail_if_not_removed
def test_local_writing():
    """Test writing to the local filesystem."""
    rmtree('tmp/local_writer_test', ignore_errors=True)
    writer = LocalWriter('tmp/local_writer_test', 'header.identifier._text')
    writer.write(DOCUMENTS)
    count = 0
    for basepath, _, filenames in os.walk('tmp/json_writer_test'):
        for filename in filenames:
            if filename.endswith('.json'):
                count = count + len(filenames)
                with open(os.path.join(basepath, filename)) as in_f:
                    doc = json.load(in_f)
                    assert 'id' in doc
                    assert 'name' in doc
                    if doc['id'] == '2':
                        assert 'first' in doc['name']
                        assert len(doc['name']['first']) == 2
                    else:
                        assert 'first' in doc['name']
                    assert 'last' in doc['name']
                    assert 'age' in doc
                    if doc['id'] == '1':
                        assert 'special tags' in doc
    assert count == 3


@fail_if_not_removed
def test_local_writing_pre_split_id_path():
    """Test writing to the local filesystem."""
    rmtree('tmp/local_writer_test', ignore_errors=True)
    writer = LocalWriter('tmp/local_writer_test', ['header', 'identifier', '_text'])
    writer.write(DOCUMENTS)
    count = 0
    for basepath, _, filenames in os.walk('tmp/json_writer_test'):
        for filename in filenames:
            if filename.endswith('.json'):
                count = count + len(filenames)
                with open(os.path.join(basepath, filename)) as in_f:
                    doc = json.load(in_f)
                    assert 'id' in doc
                    assert 'name' in doc
                    if doc['id'] == '2':
                        assert 'first' in doc['name']
                        assert len(doc['name']['first']) == 2
                    else:
                        assert 'first' in doc['name']
                    assert 'last' in doc['name']
                    assert 'age' in doc
                    if doc['id'] == '1':
                        assert 'special tags' in doc
    assert count == 3
