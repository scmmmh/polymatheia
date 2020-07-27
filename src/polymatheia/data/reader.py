"""This module provides a range of readers for accessing local and remote resources.

All readers return their data as :class:`~polymatheia.util.NavigableDict`.
"""
from sickle import Sickle

from polymatheia.util import NavigableDict


class OAISetReader(object):
    """The class:`~polymatheia.data.reader.OAISetReader` is an iterator for the Sets provided by an OAI-PMH server."""

    def __init__(self, url):
        """Construct a new class:`~polymatheia.data.reader.OAISetReader`.

        :param url: The base URL of the OAI-PMH server
        :type url: ``string``
        """
        self._it = Sickle(url).ListSets()

    def __iter__(self):
        """Return this class:`~polymatheia.data.reader.OAISetReader` as the iterator."""
        return self

    def __next__(self):
        """Return the next OAI-PMH Set.

        :raises StopIteration: If no more Sets are available
        """
        oai_set = next(self._it)
        return NavigableDict({'set_spec': oai_set.setSpec, 'set_name': oai_set.setName})
