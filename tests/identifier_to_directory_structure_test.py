"""Test the :func:`~polymatheia.util.oai_identifier_to_list` function."""
import pytest

from polymatheia.util import identifier_to_directory_structure


def test_full_schema():
    """Test that full OAI identifier schema identifiers are correctly split."""
    tmp = identifier_to_directory_structure('oai:example.com:abcd')
    assert tmp == ['example.com', 'ab', 'cd']
    tmp = identifier_to_directory_structure('oai:example.com:abcde')
    assert tmp == ['example.com', 'ab', 'cd', 'e']


def test_only_local_schema():
    """Test that local-only identifiers are correctly split."""
    tmp = identifier_to_directory_structure('abcd')
    assert tmp == ['ab', 'cd']
    tmp = identifier_to_directory_structure('abcde')
    assert tmp == ['ab', 'cd', 'e']


def test_empty_schema():
    """Test that an empty identifier raises an exception."""
    with pytest.raises(Exception):
        identifier_to_directory_structure('')
