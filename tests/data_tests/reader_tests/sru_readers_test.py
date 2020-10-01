"""Tests for SRU readers."""
from polymatheia.data import NavigableDict
from polymatheia.data.reader import SRUExplainRecordReader, SRURecordReader

SRU_API = 'http://sru.k10plus.de/gvk'
QUERY = "dog"
MAXIMUM_RECORDS = 20
RECORD_SCHEMA = "mods"


def test_read_explain_record():
    """Test that getting and reading a SRU Explain record works."""
    reader = SRUExplainRecordReader(SRU_API)
    for item in reader:
        assert item.explain.serverInfo["@protocol"] == "SRU"
        assert item.explain.databaseInfo.contact == "gbv@gbv.de"
    assert reader.schemas is not None
    assert reader.echo is not None
    assert type(reader.echo) == NavigableDict
    assert reader.echo.query is None


def test_sru_record_reader():
    """Test that SRURecordReader works."""
    reader = SRURecordReader(SRU_API,
                             query=QUERY,
                             maximumRecords=MAXIMUM_RECORDS,
                             recordSchema=RECORD_SCHEMA
                             )
    assert reader.number_of_records > 0
    assert reader.echo is not None
    assert type(reader.echo) == NavigableDict
    assert reader.echo.query == QUERY


def test_sru_record_reader_iteration():
    """Test that SRURecordReader iterates correctly."""
    reader = SRURecordReader(SRU_API,
                             query=QUERY,
                             maximumRecords=MAXIMUM_RECORDS,
                             recordSchema=RECORD_SCHEMA
                             )
    assert iter(reader)
    for item in reader:
        assert type(item) is NavigableDict
        assert item.zs_recordSchema._text == RECORD_SCHEMA
        break


def test_sru_record_reader_repeat():
    """Test that using the SRURecordReader twice works."""
    reader = SRURecordReader(SRU_API,
                             query=QUERY,
                             maximumRecords=MAXIMUM_RECORDS,
                             recordSchema=RECORD_SCHEMA
                             )
    count1 = len(list(iter(reader)))
    count2 = len(list(iter(reader)))
    assert count1 == count2


def test_limited_sru_records():
    """Test that number of SRU records can be limited."""
    limit = 5
    reader = SRURecordReader(SRU_API,
                             query=QUERY,
                             maximumRecords=limit,
                             recordSchema=RECORD_SCHEMA
                             )
    count = 0
    for _ in reader:
        count += 1
    assert count == limit


def test_sru_records_no_results():
    """Test correct behaviour when no SRU records are found."""
    reader = SRURecordReader(SRU_API,
                             query="blablabla?!//!§$923",
                             maximumRecords=MAXIMUM_RECORDS,
                             recordSchema=RECORD_SCHEMA
                             )
    assert len(list(iter(reader))) == 0
    assert reader.number_of_records == 0
