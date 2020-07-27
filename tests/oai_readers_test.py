"""Tests for various OAI readers."""
from polymatheia.data.reader import OAIMetadataReader, OAISetReader, OAIRecordReader


def test_list_metadata():
    """Test that OAI metadata format listing works."""
    reader = OAIMetadataReader('https://digital.iai.spk-berlin.de/viewer/oai')
    oai_dc_found = False
    for item in reader:
        assert item.schema
        assert item.metadataPrefix
        assert item.metadataNamespace
        if item.metadataPrefix == 'oai_dc':
            oai_dc_found = True
    assert oai_dc_found is True


def test_list_sets():
    """Test that OAI set listing works."""
    reader = OAISetReader('https://digital.iai.spk-berlin.de/viewer/oai')
    for item in reader:
        assert item.setSpec
        assert item.setName


def test_list_records_oai_dc():
    """Test that listing records in the default oai_dc metadata works."""
    reader = OAIRecordReader('https://digital.iai.spk-berlin.de/viewer/oai')
    for item in reader:
        assert item.header
        assert item.header.identifier
        assert item.metadata
        assert item.metadata['{http://www.openarchives.org/OAI/2.0/oai_dc/}dc']
        assert item.metadata['{http://www.openarchives.org/OAI/2.0/oai_dc/}dc'].dc_title
        break


def test_list_records_mets():
    """Test that listing records in the mets metadata works."""
    reader = OAIRecordReader('https://digital.iai.spk-berlin.de/viewer/oai', metadataPrefix='mets')
    for item in reader:
        assert item.header
        assert item.metadata
        assert item.metadata['{http://www.loc.gov/METS/}mets']
        break
