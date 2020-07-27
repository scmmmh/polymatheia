"""Tests for :class:`~polymatheia.data.reader.OAISetReader."""
from polymatheia.data.reader import OAISetReader


def test_list_sets():
    """Test that OAI set listing works."""
    reader = OAISetReader('http://www.digizeitschriften.de/oai2/')
    for item in reader:
        assert item.set_spec
        assert item.set_name
