"""Tests for SRU readers."""
from polymatheia.data import NavigableDict
from polymatheia.data.reader import SRUExplainRecordReader, SRURecordReader

URL = 'http://sru.k10plus.de/gvk'
QUERY = "dog"
MAX_RECORDS = 20
RECORD_SCHEMA = "mods"


def test_read_explain_record():
    """Test that getting and reading a SRU Explain record works."""
    reader = SRUExplainRecordReader(URL)
    for item in reader:
        assert item.explain.serverInfo["@protocol"] == "SRU"
        assert item.explain.databaseInfo.contact == "gbv@gbv.de"
    assert reader.schemas is not None
    assert reader.echo is not None
    assert type(reader.echo) == NavigableDict
    assert reader.echo.query is None


def test_sru_record_reader():
    """Test that SRURecordReader works."""
    assert SRURecordReader.get_result_count(URL, QUERY) > 0
    reader = SRURecordReader(URL,
                             query=QUERY,
                             max_records=MAX_RECORDS,
                             record_schema=RECORD_SCHEMA
                             )
    assert reader.echo is None
    for _ in reader:  # set echo attribute when iteration starts
        assert type(reader.echo) == NavigableDict
        assert reader.echo.query == QUERY
        assert reader.record_count > 0
        break


def test_sru_record_reader_iteration():
    """Test that SRURecordReader iterates correctly."""
    reader = SRURecordReader(URL,
                             query=QUERY,
                             max_records=MAX_RECORDS,
                             record_schema=RECORD_SCHEMA
                             )
    assert iter(reader)
    for item in reader:
        assert type(item) is NavigableDict
        assert item.zs_recordSchema._text == RECORD_SCHEMA
        break


def test_sru_record_reader_repeat():
    """Test that using the SRURecordReader twice works."""
    reader = SRURecordReader(URL,
                             query=QUERY,
                             max_records=MAX_RECORDS,
                             record_schema=RECORD_SCHEMA
                             )
    count1 = len(list(iter(reader)))
    count2 = len(list(iter(reader)))
    assert count1 == count2


def test_limited_sru_records():
    """Test that number of SRU records can be limited."""
    limit = 5
    reader = SRURecordReader(URL,
                             query=QUERY,
                             max_records=limit,
                             record_schema=RECORD_SCHEMA
                             )
    count = 0
    for _ in reader:
        count += 1
    assert count == limit


def test_sru_records_no_results():
    """Test correct behaviour when no SRU records are found."""
    reader = SRURecordReader(URL, query="blablabla?!//!§$923", max_records=MAX_RECORDS)
    assert len(list(iter(reader))) == 0
    assert SRURecordReader.get_result_count(URL, query="blablabla?!//!§$923") == 0
