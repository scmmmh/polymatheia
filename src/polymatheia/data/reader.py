"""This module provides a range of readers for accessing local and remote resources.

All readers return their data as :class:`~polymatheia.data.NavigableDict`.
"""
import json
import os

from csv import DictReader
from lxml import etree
from requests import get
from sickle import Sickle

from polymatheia.data import NavigableDict, xml_to_navigable_dict


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
        """Return the next OAI-PMH MetadataFormt as a :class:`~polymatheia.data.NavigableDict`.

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
        """Return the next OAI-PMH Set as a :class:`~polymatheia.data.NavigableDict`.

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
        """Return the next OAI-PMH Record as a :class:`~polymatheia.data.NavigableDict`.

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
        """Return the next file as a :class:`~polymatheia.data.NavigableDict`.

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


class EuropeanaSearchReader(object):
    """The :class:`~polymatheia.data.reader.EuropeanaSearchReader` provides access to the Europeana Search API.

    The initial search is run immediately on creating a new :class:`~polymatheia.data.reader.EuropeanaSearchReader`.
    The iterator will automatically paginate through the full set of result pages.

    .. attribute:: result_count
       :type: ``int``

       The total number of records returned by the search.

    .. attribute:: facets
       :type: ``list`` of :class:`~polymatheia.data.NavigableDict`

       The facets generated by the search. This is only set if the ``profile`` parameter is set to ``'facets'``.
    """

    def __init__(self, api_key, query, max_records=None, query_facets=None, media=None, thumbnail=None,
                 reusability=None, profile=None):
        """Create a new :class:`~polymatheia.data.reader.EuropeanaSearchReader`.

        :param api_key: The Europeana API key
        :type api_key: ``str``
        :param query: The query string
        :type query: ``str``
        :param max_records: The maximum number of records to return. Defaults to all records
        :type max_records: ``int``
        :param query_facets: The list of query facets to apply to the search
        :type query_facets: ``list`` of ``str``
        :param media: Whether to require that matching records have media attached. Defaults to no requirement
        :type media: ``bool``
        :param thumbnail: Whether to require that matching records have a thumbnail. Defaults to no requirement
        :type thumbnail: ``bool``
        :param reusability: The reusability (rights) to require. Defaults to no limits
        :type reusability: ``str``
        :param profile: The result profile to request. Defaults to ``'standard'``
        :type profile: ``str``
        """
        self._api_key = api_key
        self._query = query
        self._max_records = max_records
        self._offset = 1
        self._query_facets = query_facets
        self._media = media
        self._thumbnail = thumbnail
        self._reusability = reusability
        self._profile = profile
        self.result_count = 0
        self.facets = None
        self._run_search()

    def __iter__(self):
        """Return this :class:`~polymatheia.data.reader.EuropeanaSearchReader`` as the iterator."""
        return self

    def __next__(self):
        """Return the next record as a :class:`~polymatheia.data.NavigableDict``.

        :raises StopIteration: If no more Records are available
        """
        if self._max_records is not None:
            self._max_records = self._max_records - 1
            if self._max_records < 0:
                raise StopIteration()
        try:
            return NavigableDict(next(self._it))
        except StopIteration:
            if self._offset < self.result_count:
                self._run_search()
                return NavigableDict(next(self._it))
            else:
                raise StopIteration()

    def _run_search(self):
        """Run the actual search query."""
        params = [('wskey', self._api_key),
                  ('query', self._query),
                  ('start', self._offset)]
        if self._max_records and self._max_records < 50:
            params.append(('rows', self._max_records))
        else:
            params.append(('rows', 50))
        if self._query_facets:
            params.extend([('qf', qf) for qf in self._query_facets])
        if self._media is not None:
            params.append(('media', 'true' if self._media else 'false'))
        if self._thumbnail is not None:
            params.append(('thumbnail', 'true' if self._thumbnail else 'false'))
        if self._reusability is not None:
            params.append(('reusability', self._reusability))
        if self._profile is not None:
            params.append(('profile', self._profile))
        response = get('https://api.europeana.eu/record/v2/search.json', params=params)
        if response.status_code == 200:
            data = response.json()
            self._it = iter(data['items'])
            self.result_count = data['totalResults']
            self._offset = self._offset + data['itemsCount']
            if 'facets' in data:
                self.facets = [NavigableDict(facet) for facet in data['facets']]
        else:
            raise Exception(response.json()['error'])


class CSVReader(object):
    """The :class:`~polymatheia.data.reader.CSVReader` provides access to a CSV file."""

    def __init__(self, source):
        """Create a new :class:`~polymatheia.data.reader.CSVReader`.

        :param source: The source to load the CSV from. Can either be a ``str`` filename or a file-like object
        """
        if isinstance(source, str):
            self._file = open(source)
            self._it = iter(DictReader(self._file))
        else:
            self._file = None
            self._it = iter(DictReader(source))

    def __iter__(self):
        """Return this :class:`~polymatheia.data.reader.CSVReader` as the iterator."""
        return self

    def __next__(self):
        """Return the next CSV line as a :class:`~polymatheia.data.NavigableDict`."""
        try:
            return NavigableDict(next(self._it))
        except StopIteration:
            if self._file and not self._file.closed:
                self._file.close()
            raise StopIteration()
