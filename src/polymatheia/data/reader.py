"""This module provides a range of readers for accessing local and remote resources.

All readers return their data as :class:`~polymatheia.util.NavigableDict`.
"""
import json
import os

from lxml import etree
from sickle import Sickle

from polymatheia.util import NavigableDict, xml_to_navigable_dict


class OAIMetadataReader(object):
    """The class:`~polymatheia.data.reader.OAIMetadataReader` is an iterator for OAI-PMH MetadataFormat.

    The underlying library automatically handles the continuation parameters, allowing for simple iteration.
    """

    def __init__(self, url):
        """Construct a new class:`~polymatheia.data.reader.OAIMetadataReader`.

        :param url: The base URL of the OAI-PMH server
        :type url: ``str``
        """
        self._it = Sickle(url).ListMetadataFormats()

    def __iter__(self):
        """Return this class:`~polymatheia.data.reader.OAIMetadataReader` as the iterator."""
        return self

    def __next__(self):
        """Return the next OAI-PMH MetadataFormt as a :class:`~polymatheia.util.NavigableDict`.

        :raises StopIteration: If no more Sets are available
        """
        oai_metadata = next(self._it)
        return NavigableDict({'schema': oai_metadata.schema,
                              'metadataPrefix': oai_metadata.metadataPrefix,
                              'metadataNamespace': oai_metadata.metadataNamespace})


class OAISetReader(object):
    """The class:`~polymatheia.data.reader.OAISetReader` is an iterator for OAI-PMH Sets.

    The underlying library automatically handles the continuation parameters, allowing for simple iteration.
    """

    def __init__(self, url):
        """Construct a new class:`~polymatheia.data.reader.OAISetReader`.

        :param url: The base URL of the OAI-PMH server
        :type url: ``str``
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
        return NavigableDict({'setSpec': oai_set.setSpec, 'setName': oai_set.setName})


class OAIRecordReader(object):
    """The :class:`~polymatheia.data.reader.OAIRecordReader` is an iterator for OAI-PMH Records.

    The underlying library automatically handles the continuation parameters, allowing for simple iteration.
    """

    def __init__(self, url, metadata_prefix='oai_dc', max_records=None, set_spec=None):
        """Construct a new :class:`~polymatheia.data.reader.OAIRecordReader`.

        :param url: The base URL of the OAI-PMH server
        :type url: ``str``
        :param metadataPrefix: The metadata prefix to use for accessing data
        :type metadataPrefix: ``str``
        :param max_records: The maximum number of records to return. Default (``None``) returns all records
        :type max_records: ``int``
        :param set_spec: The OAI Set specification for limiting which metadata to fetch
        :type set_spec: ``str``
        """
        self._it = Sickle(url).ListRecords(metadataPrefix=metadata_prefix,
                                           set=set_spec,
                                           ignore_deleted=True)
        self._max_records = max_records

    def __iter__(self):
        """Return this :class:`~polymatheia.data.reader.OAIRecordReader` as the iterator."""
        return self

    def __next__(self):
        """Return the next OAI-PMH Record as a :class:`~polymatheia.util.NavigableDict`.

        :raises StopIteration: If no more Records are available
        """
        if self._max_records is not None:
            self._max_records = self._max_records - 1
            if self._max_records < 0:
                raise StopIteration()
        oai_record = next(self._it)
        return xml_to_navigable_dict(etree.fromstring(oai_record.raw))


class LocalReader(object):
    """The :class:`~polymatheia.data.reader.LocalReader` is an iterator for reading from the local filesystem.

    It is designed to provide access to data serialised using the :class:`~polymatheia.data.writer.LocalWriter`.

    .. important::

       It does **not** guarantee that the order of records is the same as the order in which they were written
       to the local filesystem.
    """

    def __init__(self, directory):
        """Create a new :class:`~polymatheia.data.reader.LocalReader`.

        :param directory: The base directory within which to load the files
        :type directory: ``str``
        """
        self._directory = directory
        filelist = []
        for basepath, _, filenames in os.walk(directory):
            for filename in filenames:
                if filename.endswith('.json'):
                    filelist.append(os.path.join(basepath, filename))
        self._it = iter(filelist)

    def __iter__(self):
        """Return this :class:`~polymatheia.data.reader.LocalReader` as the iterator."""
        return self

    def __next__(self):
        """Return the next file as a :class:`~polymatheia.util.NavigableDict`.

        :raises StopIteration: If no more Records are available
        """
        filename = next(self._it)
        try:
            with open(filename) as in_f:
                return NavigableDict(json.load(in_f))
        except FileNotFoundError:
            return next(self)
        except json.JSONDecodeError:
            return next(self)
