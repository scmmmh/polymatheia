"""Tests for the :mod:`~polymatheia.data.writer` package."""
import os

from lxml import etree
from shutil import rmtree

from polymatheia.data import NavigableDict
from polymatheia.data.writer import XMLWriter


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


def test_local_writing():
    """Test writing to the local filesystem."""
    rmtree('tmp/xml_writer_test', ignore_errors=True)
    writer = XMLWriter('tmp/xml_writer_test', 'id')
    writer.write(DOCUMENTS)
    count = 0
    for basepath, _, filenames in os.walk('tmp/xml_writer_test'):
        for filename in filenames:
            if filename.endswith('.xml'):
                count = count + len(filenames)
                with open(os.path.join(basepath, filename)) as in_f:
                    doc = etree.parse(in_f)
                    assert doc.xpath('id')
                    if doc.xpath('id')[0] == '2':
                        assert len(doc.xpath('name/first')) == 2
                    else:
                        assert doc.xpath('name/first')
                    assert doc.xpath('name/last')
                    assert doc.xpath('age')
                    if doc.xpath('id')[0] == '1':
                        assert doc.xpath('special-tags')
    assert count == 3


def test_local_writing_list_id():
    """Test writing to the local filesystem."""
    rmtree('tmp/xml_writer_test', ignore_errors=True)
    writer = XMLWriter('tmp/xml_writer_test', ['id'])
    writer.write(DOCUMENTS)
    count = 0
    for basepath, _, filenames in os.walk('tmp/xml_writer_test'):
        for filename in filenames:
            if filename.endswith('.xml'):
                count = count + len(filenames)
                with open(os.path.join(basepath, filename)) as in_f:
                    doc = etree.parse(in_f)
                    assert doc.xpath('id')
                    if doc.xpath('id')[0] == '2':
                        assert len(doc.xpath('name/first')) == 2
                    else:
                        assert doc.xpath('name/first')
                    assert doc.xpath('name/last')
                    assert doc.xpath('age')
                    if doc.xpath('id')[0] == '1':
                        assert doc.xpath('special-tags')
    assert count == 3


def test_valid_xml_tag():
    """Test that the valid_xml_tag function works."""
    writer = XMLWriter('', '')
    assert writer._valid_xml_tag('test') == 'test'
    assert writer._valid_xml_tag('this is a test') == 'this-is-a-test'
    assert writer._valid_xml_tag('tag 1 2 3') == 'tag-1-2-3'
    assert writer._valid_xml_tag('1 test') == 'test'
    assert writer._valid_xml_tag('xmlData') == 'Data'
    assert writer._valid_xml_tag('XMLdata') == 'data'
