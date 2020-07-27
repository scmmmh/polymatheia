"""This module provides a writer for serialising data to the local filesystem."""
import json
import os

from copy import copy

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
        """Write the records to the file-system."""
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
