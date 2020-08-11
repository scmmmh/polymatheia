"""Tests for various OAI readers."""
from polymatheia.data.reader import OAIMetadataFormatReader, OAISetReader, OAIRecordReader


def test_list_metadata():
    """Test that OAI metadata format listing works."""
    reader = OAIMetadataFormatReader('http://www.digizeitschriften.de/oai2/')
    oai_dc_found = False
    for item in reader:
        assert item.schema
        assert item.metadataPrefix
        assert item.metadataNamespace
        if item.metadataPrefix == 'oai_dc':
            oai_dc_found = True
    assert oai_dc_found is True


def test_list_metadata_repeat():
    """Test that using the OAIMetadataFormatReader twice works."""
    reader = OAIMetadataFormatReader('http://www.digizeitschriften.de/oai2/')
    count1 = len(list(iter(reader)))
    count2 = len(list(iter(reader)))
    assert count1 == count2


def test_list_sets():
    """Test that OAI set listing works."""
    reader = OAISetReader('http://www.digizeitschriften.de/oai2/')
    for item in reader:
        assert item.setSpec
        assert item.setName


def test_list_sets_repeat():
    """Test that using the OAISetReader twice works."""
    reader = OAISetReader('http://www.digizeitschriften.de/oai2/')
    count1 = len(list(iter(reader)))
    count2 = len(list(iter(reader)))
    assert count1 == count2


def test_list_records_oai_dc():
    """Test that listing records in the default oai_dc metadata works."""
    reader = OAIRecordReader('http://www.digizeitschriften.de/oai2/')
    for item in reader:
        assert item.header
        assert item.header.identifier
        assert item.metadata
        assert item.metadata['{http://www.openarchives.org/OAI/2.0/oai_dc/}dc']
        assert item.metadata['{http://www.openarchives.org/OAI/2.0/oai_dc/}dc'].dc_title
        break


def test_list_records_mets():
    """Test that listing records in the mets metadata works."""
    reader = OAIRecordReader('http://www.digizeitschriften.de/oai2/', metadata_prefix='mets')
    for item in reader:
        assert item.header
        assert item.metadata
        assert item.metadata['{http://www.loc.gov/METS/}mets']
        break


def test_list_limited_records():
    """Test that listing records can be limited."""
    reader = OAIRecordReader('http://www.digizeitschriften.de/oai2/', max_records=10)
    count = 0
    for item in reader:
        assert item.metadata['{http://www.openarchives.org/OAI/2.0/oai_dc/}dc']
        assert item.metadata['{http://www.openarchives.org/OAI/2.0/oai_dc/}dc'].dc_title
        count = count + 1
    assert count == 10


def test_list_set_records():
    """Test that listing records limited to a Set works."""
    oai_sets = OAISetReader('http://www.digizeitschriften.de/oai2/')
    oai_set = next(iter(oai_sets))
    reader = OAIRecordReader('http://www.digizeitschriften.de/oai2/',
                             metadata_prefix='mets',
                             set_spec=oai_set.setSpec)
    for item in reader:
        assert item.header
        assert item.metadata
        assert item.metadata['{http://www.loc.gov/METS/}mets']
        break


def test_list_records_repeat():
    """Test that using the OAIRecordReader twice works."""
    reader = OAIRecordReader('http://www.digizeitschriften.de/oai2/', max_records=10)
    count1 = len(list(iter(reader)))
    count2 = len(list(iter(reader)))
    assert count1 == count2
