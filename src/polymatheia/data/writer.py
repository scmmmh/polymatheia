"""This module provides a writer for serialising data to the local filesystem."""
import json
import os
import re

from csv import DictWriter
from deprecation import deprecated
from hashlib import sha256
from lxml import etree
from pandas import DataFrame

from polymatheia import __version__


class JSONWriter():
    """The :class:`~polymatheia.data.writer.JSONWriter` writes records to the local filesystem as JSON files."""

    def __init__(self, directory, id_path):
        """Create a new :class:`~polymatheia.data.writer.JSONWriter`.

        For each record the identifier is used to create a directory structure. In the leaf directory the identifier
        is then used as the filename.

        :param directory: The base directory within which to create the files
        :type directory: ``str``
        :param id_path: The path used to access the identifier in the record
        :type id_path: ``str`` or ``list``
        """
        self._directory = directory
        if isinstance(id_path, str):
            self._id_path = id_path.split('.')
        else:
            self._id_path = id_path

    def write(self, records):
        """Write the records to the file-system.

        :param records: The records to write
        :type records: Iterable of :class:`~polymatheia.data.NavigableDict`
        """
        for record in records:
            identifier = record.get(self._id_path)
            if identifier:
                hash = sha256(identifier.encode('utf-8'))
                hex = hash.hexdigest()
                file_path = os.path.join(
                    self._directory,
                    *[hex[idx:idx+4] for idx in range(0, len(hex), 4)],
                    hex)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(f'{file_path}.json', 'w') as out_f:
                    json.dump(record, out_f)


@deprecated(deprecated_in='0.2.0', removed_in='1.0.0', current_version=__version__,
            details='Replaced by the polymatheia.data.writer.JSONWriter')
class LocalWriter(JSONWriter):
    """Deprecated. Use :class:`~polymatheia.data.writer.JSONWriter`."""

    pass


class XMLWriter():
    """The :class:`~polymatheia.data.writer.XMLWriter` writes records to the local filesystem as XML."""

    def __init__(self, directory, id_path):
        """Create a new :class:`~polymatheia.data.writer.XMLWriter`.

        For each record the identifier is used to create a directory structure. In the leaf directory the identifier
        is then used as the filename.

        :param directory: The base directory within which to create the files
        :type directory: ``str``
        :param id_path: The path used to access the identifier in the record
        :type id_path: ``str`` or ``list``
        """
        self._directory = directory
        if isinstance(id_path, str):
            self._id_path = id_path.split('.')
        else:
            self._id_path = id_path

    def write(self, records):
        """Write the records to the file-system.

        :param records: The records to write
        :type records: Iterable of :class:`~polymatheia.data.NavigableDict`
        """
        for record in records:
            identifier = record.get(self._id_path)
            if identifier:
                hash = sha256(identifier.encode('utf-8'))
                hex = hash.hexdigest()
                file_path = os.path.join(
                    self._directory,
                    *[hex[idx:idx+4] for idx in range(0, len(hex), 4)],
                    hex)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(f'{file_path}.xml', 'wb') as out_f:
                    root = etree.Element('record')
                    self._build_xml_doc(root, record)
                    out_f.write(etree.tostring(root))

    def _build_xml_doc(self, parent, data):
        """Build the XML document tree.

        Tag names are generated from the keys in the ``data``, ensuring that they are valid XML tag names.

        Handles nested ``data`` trees by nesting elements and lists by generating the same tag repeatedly.

        :param parent: The parent node to attach elements to
        :type parent: :class:`~lxml.etree.Element`
        :param data: The data to build the tree from
        :type data: :class:`~polymatheia.data.NavigableDict`
        """
        for key, value in data.items():
            if isinstance(value, list):
                for sub_value in value:
                    element = etree.Element(self._valid_xml_tag(key))
                    if isinstance(sub_value, dict):
                        self._build_xml_doc(element, sub_value)
                    else:
                        element.text = str(value)
                    parent.append(element)
            elif isinstance(value, dict):
                element = etree.Element(self._valid_xml_tag(key))
                self._build_xml_doc(element, value)
                parent.append(element)
            else:
                element = etree.Element(self._valid_xml_tag(key))
                element.text = str(value)
                parent.append(element)

    def _valid_xml_tag(self, tag):
        """Generate a valid XML tag for the given ``tag``.

        :param tag: The tag to generate a valid XML tag for
        :type tag: ``str``
        :return: A valid XML tag
        :rtype: ``str``
        """
        tag = re.sub(r'\s+', '-', tag)
        tag = ''.join(re.findall(r'\w|\d|-|_|\.', tag))
        while not re.match(r'\w', tag) or re.match(r'\d', tag):
            tag = tag[1:]
        if tag.lower().startswith('xml'):
            tag = tag[3:]
        return tag


class CSVWriter():
    """The :class:`~polymatheia.data.writer.CSVWriter` writes records into a CSV file.

    The :class:`~polymatheia.data.writer.CSVWriter` assumes that no record contains any kind of nested data. If
    it is passed nested data, then the behaviour is undefined.
    """

    def __init__(self, target, default_value='', extras_action='ignore', column_names=None):
        """Create a new :class:`~polymatheia.data.writer.CSVWriter`.

        :param target: The target to write the CSV to. Can either be a ``str`` filename or an existing file-like object
        :param default_value: The default value to output if a record does not contain a value for a specified CSV
                              column name
        :param extras_action: The action to take if a record contains keys that are not in the CVS fieldnames. Set to
                              ``'ignore'`` to just ignore this (the default). Set to ``'raise'`` to raise a
                              ``ValueError``.
        :type extras_action: ``str``
        :param fieldnames: The CSV column names to use. If ``None`` is specified, then the column names are derived
                           from the first record's keys.
        :type fieldnames: ``list`` of ``str``
        """
        self._target = target
        self._default_value = default_value
        self._extras_action = extras_action
        self._column_names = column_names

    def write(self, records):
        """Write the ``records`` to the CSV file.

        :param records: The records to write
        :type records: Iterable of :class:`~polymatheia.data.NavigableDict`
        """
        if isinstance(self._target, str):
            with open(self._target, 'w') as out_file:
                self._write_csv(out_file, records)
        else:
            self._write_csv(self._target, records)

    def _write_csv(self, file, records):
        """Perform the actual writing of the CSV file.

        :param file: The file-like object to write to
        :param records: The records to write
        :type records: Iterable of :class:`~polymatheia.data.NavigableDict`
        """
        csv_writer = None
        for record in records:
            if not csv_writer:
                csv_writer = DictWriter(file,
                                        fieldnames=record.keys() if self._column_names is None
                                        else self._column_names,
                                        restval=self._default_value,
                                        extrasaction=self._extras_action)
                csv_writer.writeheader()
            csv_writer.writerow(record)


class PandasDFWriter(object):
    """The :class:`~polymatheia.data.writer.PandasDFWriter` writes records to a Pandas :class:`~pandas.DataFrame`.

    The :class:`~polymatheia.data.writer.PandasDFWriter` attempts to automatically coerce columns to integers or
    floats.

    The :class:`~polymatheia.data.writer.PandasDFWriter` assumes that no record contains any kind of nested data. If
    it is passed nested data, then the behaviour is undefined.
    """

    def __init__(self):
        """Create a new :class:`~polymatheia.data.writer.PandasDFWriter`."""
        self.df = None

    def write(self, records):
        """Write the ``records`` to the Pandas :class:`~pandas.DataFrame`.

        :param records: The records to write
        :type records: Iterable of :class:`~polymatheia.data.NavigableDict`
        :return: The Pandas dataframe
        :rtype: :class:`~pandas.DataFrame`
        """
        columns = {}
        for record in records:
            for key, value in record.items():
                if key not in columns:
                    columns[key] = []
                columns[key].append(value)
        for key, values in columns.items():
            try:
                columns[key] = [int(v) for v in values]
            except ValueError:
                try:
                    columns[key] = [float(v) for v in values]
                except ValueError:
                    pass
        return DataFrame(columns)
