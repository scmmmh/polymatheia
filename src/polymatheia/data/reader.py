"""This module provides a range of readers for accessing local and remote resources.

All readers return their data as :class:`~polymatheia.data.NavigableDict`.
"""
import json
import os

from csv import DictReader
from deprecation import deprecated
from lxml import etree
from requests import get
from sickle import Sickle
from srupy import SRUpy

from polymatheia import __version__
from polymatheia.data import NavigableDict, NavigableDictIterator, LimitingIterator, xml_to_navigable_dict


class OAIMetadataFormatReader(object):
    """The class:`~polymatheia.data.reader.OAIMetadataFormatReader` is a container for OAI-PMH MetadataFormat.

    The underlying library automatically handles the continuation parameters, allowing for simple iteration.
    """

    def __init__(self, url):
        """Construct a new class:`~polymatheia.data.reader.OAIMetadataFormatReader`.

        :param url: The base URL of the OAI-PMH server
        :type url: ``str``
        """
        self._url = url

    def __iter__(self):
        """Return a new class:`~polymatheia.data.NavigableDictIterator` as the iterator."""
        return NavigableDictIterator(Sickle(self._url).ListMetadataFormats(),
                                     mapper=lambda meta_format: {'schema': meta_format.schema,
                                                                 'metadataPrefix': meta_format.metadataPrefix,
                                                                 'metadataNamespace': meta_format.metadataNamespace})


class OAISetReader(object):
    """The class:`~polymatheia.data.reader.OAISetReader` is an iteration container for OAI-PMH Sets.

    The underlying library automatically handles the continuation parameters, allowing for simple iteration.
    """

    def __init__(self, url):
        """Construct a new class:`~polymatheia.data.reader.OAISetReader`.

        :param url: The base URL of the OAI-PMH server
        :type url: ``str``
        """
        self._url = url
        self._it = Sickle(url).ListSets()

    def __iter__(self):
        """Return a new class:`~polymatheia.data.NavigableDictIterator` as the iterator."""
        return NavigableDictIterator(Sickle(self._url).ListSets(),
                                     mapper=lambda oai_set: {'setSpec': oai_set.setSpec, 'setName': oai_set.setName})


class OAIRecordReader(object):
    """The :class:`~polymatheia.data.reader.OAIRecordReader` is an iteration container for OAI-PMH Records.

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
        self._url = url
        self._metadata_prefix = metadata_prefix
        self._set_spec = set_spec
        self._max_records = max_records

    def __iter__(self):
        """Return a new class:`~polymatheia.data.NavigableDictIterator` as the iterator.

        If ``max_records`` is set, then the class:`~polymatheia.data.NavigableDictIterator` is wrapped in a
        class:`~polymatheia.data.LimitingIterator`.
        """
        it = NavigableDictIterator(Sickle(self._url).ListRecords(metadataPrefix=self._metadata_prefix,
                                                                 set=self._set_spec,
                                                                 ignore_deleted=True),
                                   mapper=lambda record: xml_to_navigable_dict(etree.fromstring(
                                       record.raw,
                                       parser=etree.XMLParser(remove_comments=True))))
        if self._max_records is not None:
            it = LimitingIterator(it, self._max_records)
        return it


class JSONReader():
    """The :class:`~polymatheia.data.reader.JSONReader` is a container for reading JSON files from the filesystem.

    It is designed to provide access to data serialised using the :class:`~polymatheia.data.writer.JSONWriter`.

    .. important::

       It does **not** guarantee that the order of records is the same as the order in which they were written
       to the local filesystem.
    """

    def __init__(self, directory):
        """Create a new :class:`~polymatheia.data.reader.JSONReader`.

        :param directory: The base directory within which to load the files
        :type directory: ``str``
        """
        self._directory = directory
        self._filelist = []
        for basepath, _, filenames in os.walk(directory):
            for filename in filenames:
                if filename.endswith('.json'):
                    self._filelist.append(os.path.join(basepath, filename))

    def __iter__(self):
        """Return a new :class:`~polymatheia.data.NavigableDictIterator` as the iterator."""
        return NavigableDictIterator(iter(self._filelist),
                                     mapper=self._load)

    def _load(self, filename):
        """Return the next file as a :class:`~polymatheia.data.NavigableDict`."""
        with open(filename) as in_f:
            return json.load(in_f)


@deprecated(deprecated_in='0.2.0', removed_in='1.0.0', current_version=__version__,
            details='Replaced by the polymatheia.data.reader.JSONReader')
class LocalReader(JSONReader):
    """Deprecated. Use :class:`~polymatheia.data.reader.JSONReader`."""

    pass


class XMLReader():
    """The :class:`~polymatheia.data.reader.XMLReader` is a container for reading XML files from the local filesystem.

    The :class:`~polymatheia.data.reader.XMLReader` will only load files that have a ".xml" extension.
    """

    def __init__(self, directory):
        """Create a new :class:`~polymatheia.data.reader.XMLReader`.

        :param directory: The base directory within which to load the files
        :type directory: ``str``
        """
        self._directory = directory
        self._filelist = []
        for basepath, _, filenames in os.walk(directory):
            for filename in filenames:
                if filename.endswith('.xml'):
                    self._filelist.append(os.path.join(basepath, filename))

    def __iter__(self):
        """Return a new :class:`~polymatheia.data.NavigableDictIterator` as the iterator."""
        return NavigableDictIterator(iter(self._filelist),
                                     mapper=self._load)

    def _load(self, filename):
        """Return the next file as a :class:`~polymatheia.data.NavigableDict`."""
        with open(filename) as in_f:
            return xml_to_navigable_dict(etree.parse(in_f, parser=etree.XMLParser(remove_comments=True)).getroot())


class EuropeanaSearchReader(object):
    """The :class:`~polymatheia.data.reader.EuropeanaSearchReader` provides access to the Europeana Search API.

    The initial search is run immediately on creating a new :class:`~polymatheia.data.reader.EuropeanaSearchReader`.
    The iterator will automatically paginate through the full set of result pages.

    .. attribute:: result_count
       :type: int

       The total number of records returned by the search.

    .. attribute:: facets
       :type: polymatheia.data.NavigableDict

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
        self._cursor = '*'
        self._offset = 0
        self._query_facets = query_facets
        self._media = media
        self._thumbnail = thumbnail
        self._reusability = reusability
        self._profile = profile
        it = iter(self)
        self.result_count = it.result_count
        self.facets = it.facets

    def __iter__(self):
        """Return this :class:`~polymatheia.data.reader.EuropeanaSearchReader` as the iterator."""
        return EuropeanaSearchIterator(self._api_key, self._query, self._max_records, self._query_facets, self._media,
                                       self._thumbnail, self._reusability, self._profile)


class EuropeanaSearchIterator(object):
    """The :class:`~polymatheia.data.reader.EuropeanaSearchIterator` provides an iterator for the Europeana Search API.

    The initial search is run immediately on creating a new :class:`~polymatheia.data.reader.EuropeanaSearchIterator`.
    The iterator will automatically paginate through the full set of result pages.

    .. attribute:: result_count
       :type: int

       The total number of records returned by the search.

    .. attribute:: facets
       :type: polymatheia.data.NavigableDict

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
        self._cursor = '*'
        self._offset = 0
        self._query_facets = query_facets
        self._media = media
        self._thumbnail = thumbnail
        self._reusability = reusability
        self._profile = profile
        self.result_count = 0
        self.facets = None
        self._run_search()

    def __iter__(self):
        """Return this :class:`~polymatheia.data.reader.EuropeanaSearchIterator` as the iterator."""
        return self

    def __next__(self):
        """Return the next record as a :class:`~polymatheia.data.NavigableDict`.

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
                  ('cursor', self._cursor)]
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
            if 'nextCursor' in data:
                self._cursor = data['nextCursor']
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
        else:
            self._file = source

    def __iter__(self):
        """Return this :class:`~polymatheia.data.reader.CSVReader` as the iterator."""
        if self._file.seekable():
            self._file.seek(0)
        return NavigableDictIterator(iter(DictReader(self._file)))


class SRUExplainRecordReader(object):
    """The class:`~polymatheia.data.reader.SRUExplainRecordReader` is a container for SRU Explain Records."""

    def __init__(self, url):
        """Construct a new class:`~polymatheia.data.reader.SRUExplainRecordReader`.

        :param url: The base URL of the SRU server
        :type url: ``str``
        """
        self._url = url
        self._explain = SRUpy(self._url).explain()
        self.schemas = [(schema["@name"], schema.title)
                        for schema in NavigableDict(self._explain).explain.schemaInfo.schema]
        self.echo = NavigableDict(self._explain.echo)

    def __iter__(self):
        """Return a new class:`~polymatheia.data.NavigableDictIterator` as the iterator."""
        return NavigableDictIterator(iter(self._explain),
                                     mapper=lambda record: {record[0]: record[1]}
                                     )


class SRURecordReader(object):
    """The :class:`~polymatheia.data.reader.SRURecordReader` is an iteration container for Records fetched via SRU.

    The underlying library (SRUpy) automatically handles the continuation parameters, allowing for simple iteration.
    """

    def __init__(self, url, query, max_records=None, record_schema="dc", **kwargs):
        """Construct a new :class:`~polymatheia.data.reader.SRURecordReader`.

        :param url: The base URL of the SRU endpoint
        :type url: ``str``
        :param query: The query string
        :type query: ``str``
        :param max_records: The maximum number of records to return
        :type max_records: ``int``
        :param record_schema: Schema in which records will be returned. Defaults to Dublin Core schema.
        :type record_schema: ``str``
        :param kwargs: Additional request parameters that will be sent to the SRU server
        """
        self._url = url
        self._query = query
        self._max_records = max_records
        self._record_schema = record_schema
        self._kwargs = kwargs
        self.record_count = None
        self.echo = None

    def __iter__(self):
        """Return a new class:`~polymatheia.data.NavigableDictIterator` as the iterator."""
        sru_records = SRUpy(self._url).get_records(query=self._query,
                                                   maximumRecords=self._max_records,
                                                   recordSchema=self._record_schema,
                                                   **self._kwargs)
        self.record_count = sru_records.number_of_records
        if sru_records.echo:
            self.echo = NavigableDict(sru_records.echo)
        return NavigableDictIterator(sru_records,
                                     mapper=lambda record: xml_to_navigable_dict(
                                         etree.fromstring(
                                             record.raw,
                                             parser=etree.XMLParser(remove_comments=True)
                                         )
                                     ))

    @staticmethod
    def result_count(url, query):
        """Return result count for the given query.

        :param url: The base URL of the SRU endpoint
        :type url: ``str``
        :param query: The query string
        :type query: ``str``
        """
        return SRUpy(url).get_records(query=query, maximumRecords=1).number_of_records
