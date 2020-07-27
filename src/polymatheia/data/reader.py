"""This module provides a range of readers for accessing local and remote resources.

All readers return their data as :class:`~polymatheia.util.NavigableDict`.
"""
from lxml import etree
from sickle import Sickle

from polymatheia.util import NavigableDict, xml_to_navigable_dict


class OAISetReader(object):
    """The class:`~polymatheia.data.reader.OAISetReader` is an iterator for OAI-PMH Sets.

    The underlying library automatically handles the continuation parameters, allowing for simple iteration.
    """

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
        """Return the next OAI-PMH Set as a :class:`~polymatheia.util.NavigableDict`.

        :raises StopIteration: If no more Sets are available
        """
        oai_set = next(self._it)
        return NavigableDict({'set_spec': oai_set.setSpec, 'set_name': oai_set.setName})


class OAIRecordReader(object):
    """The :class:`~polymatheia.data.reader.OAIRecordReader` is an iterator for OAI-PMH Records.

    The underlying library automatically handles the continuation parameters, allowing for simple iteration.
    """

    def __init__(self, url, metadataPrefix='oai_dc'):
        """Construct a new :class:`~polymatheia.data.reader.OAIRecordReader`.

        :param url: The base URL of the OAI-PMH server
        :type url: ``string``
        :param metadataPrefix: The metadata prefix to use for accessing data
        :type metadataPrefix: ``string``
        """
        self._it = Sickle(url).ListRecords(metadataPrefix=metadataPrefix, ignore_deleted=True)

    def __iter__(self):
        """Return this :class:`~polymatheia.data.reader.OAIRecordReader` as the iterator."""
        return self

    def __next__(self):
        """Return the next OAI-PMH Record as a :class:`~polymatheia.util.NavigableDict`.

        :raises StopIteration: If no more Records are available
        """
        oai_record = next(self._it)
        return xml_to_navigable_dict(etree.fromstring(oai_record.raw))
