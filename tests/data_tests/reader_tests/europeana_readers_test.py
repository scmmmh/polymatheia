"""Tests for the :class:`~polymatheia.data.reader.EuropeanaSearchReader`."""
import os
import pytest

from polymatheia.data.reader import EuropeanaSearchReader


def test_basic_query():
    """Test that a basic query works."""
    reader = EuropeanaSearchReader(os.environ['EUROPEANA_API_KEY'], 'Python')
    count = 0
    for record in reader:
        assert record.id
        count = count + 1
    assert reader.result_count > 0
    assert reader.result_count == count


def test_limited_query():
    """Test that result set limiting works."""
    reader = EuropeanaSearchReader(os.environ['EUROPEANA_API_KEY'], 'Python', max_records=65)
    count = 0
    for record in reader:
        assert record.id
        count = count + 1
    assert reader.result_count > 0
    assert count == 65


def test_faceted_query():
    """Test that query facets work."""
    reader = EuropeanaSearchReader(os.environ['EUROPEANA_API_KEY'], 'Westminster',
                                   query_facets=['where:London'],
                                   max_records=65)
    count = 0
    for record in reader:
        assert record.id
        count = count + 1
    assert reader.result_count > 0
    assert count == 65


def test_media_query():
    """Test that restricting to files with media works."""
    reader = EuropeanaSearchReader(os.environ['EUROPEANA_API_KEY'], 'Python', media=True, max_records=65)
    count = 0
    for record in reader:
        assert record.id
        assert 'edmIsShownAt' in record or 'edmIsShownBy' in record or 'edmHasView' in record
        count = count + 1
    assert reader.result_count > 0
    assert count == 65


def test_thumbnail_query():
    """Test that restricting to files with thumbnails works."""
    reader = EuropeanaSearchReader(os.environ['EUROPEANA_API_KEY'], 'Python', thumbnail=True, max_records=65)
    count = 0
    for record in reader:
        assert record.id
        assert record.edmPreview
        count = count + 1
    assert reader.result_count > 0
    assert count == 65


def test_profile_minimal():
    """Test that the minimal profile is returned."""
    reader = EuropeanaSearchReader(os.environ['EUROPEANA_API_KEY'], 'Python', profile='minimal', max_records=65)
    count = 0
    for record in reader:
        assert record.id
        with pytest.raises(KeyError):
            assert record.language
        count = count + 1
    assert reader.result_count > 0
    assert count == 65


def test_profile_standard():
    """Test that the standard profile is returned."""
    reader = EuropeanaSearchReader(os.environ['EUROPEANA_API_KEY'], 'Python', profile='standard', max_records=65)
    count = 0
    for record in reader:
        assert record.id
        assert record.language
        with pytest.raises(KeyError):
            assert record.edmLandingPage
        count = count + 1
    assert reader.result_count > 0
    assert count == 65


def test_profile_facets():
    """Test that the facets profile contains facets."""
    reader = EuropeanaSearchReader(os.environ['EUROPEANA_API_KEY'], 'Python', profile='facets', max_records=65)
    count = 0
    for record in reader:
        assert record.id
        assert record.language
        with pytest.raises(KeyError):
            assert record.edmLandingPage
        count = count + 1
    assert reader.result_count > 0
    assert count == 65
    assert len(reader.facets) > 0
    assert reader.facets[0].name
    assert len(reader.facets[0].fields) > 0


def test_reusability_query():
    """Test that limiting to open reusability works."""
    reader = EuropeanaSearchReader(os.environ['EUROPEANA_API_KEY'], 'Python', reusability='open')
    count = 0
    for record in reader:
        assert record.id
        for right in record.rights:
            assert right in ['http://creativecommons.org/publicdomain/zero/1.0/',
                             'http://creativecommons.org/publicdomain/mark/1.0/',
                             'http://creativecommons.org/licenses/by/2.5/',
                             'http://creativecommons.org/licenses/by/3.0/',
                             'http://creativecommons.org/licenses/by/4.0/',
                             'http://creativecommons.org/licenses/by-sa/3.0/',
                             'http://creativecommons.org/licenses/by-sa/4.0/']
        count = count + 1
    assert reader.result_count > 0
    assert count == 89


def test_invalid_api_key():
    """Test that an invalid API key generates an error."""
    with pytest.raises(Exception):
        EuropeanaSearchReader('Invalid', 'Python', max_records=35)
