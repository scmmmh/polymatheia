"""This module provides a writer for serialising data to the local filesystem."""
import json
import os

from copy import copy
from csv import DictWriter

from polymatheia.util import identifier_to_directory_structure


class LocalWriter():
    """The :class:`~polymatheia.data.writer.LocalWriter` writes records to the local filesystem."""

    def __init__(self, directory, id_path):
        """Create a new :class:`~polymatheia.data.writer.LocalWriter`.

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
            path = copy(self._id_path)
            identifier = record
            while path:
                identifier = identifier[path[0]]
                path = path[1:]
            identifier = identifier._text
            file_path = os.path.join(
                self._directory,
                *identifier_to_directory_structure(identifier),
                identifier)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(f'{file_path}.json', 'w') as out_f:
                json.dump(record, out_f)


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
                              ``ValueError`.
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
