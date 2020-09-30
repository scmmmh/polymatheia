Loading Data via OAI-PMH
========================

Polymatheia supports accessing metadata records via the `OAI-PMH`_ protocol. It is a generic protocol designed for
harvesting large amounts of metadata from an archive and was initially intended primarily as an archive-to-archive
metadata exchange protocol. As a result of this focus, the OAI-PMH protocol provides only very limited facilities
for filtering data on the server side. Instead the standard pattern is to download complete data-sets from the
server and then filter and transform locally.

.. _`OAI-PMH`: https://www.openarchives.org/pmh/

Finding the available Sets
--------------------------

OAI-PMH supports filtering on the server-side via the concept of a set. To find the available sets use the
:class:`~polymatheia.data.reader.OAISetReader`:

.. sourcecode:: python

    from polymatheia.data.reader import OAISetReader

    reader = OAISetReader('http://www.digizeitschriften.de/oai2/')
    for setSpec in reader:
        print(setSpec)

Finding the available MetadataFormats
-------------------------------------

An OAI-PMH server can provide the same metadata using different formats. To find which formats the server provides
use the :class:`~polymatheia.data.reader.OAIMetadataFormatReader`:

.. sourcecode:: python

    from polymatheia.data.reader import OAIMetadataFormatReader

    reader = OAIMetadataFormatReader('http://www.digizeitschriften.de/oai2/')
    for format in reader:
        print(format)

Fetching records
----------------

To retrieve all records use the :class:`~polymatheia.data.reader.OAIRecordReader`:

.. sourcecode:: python

    from polymatheia.data.reader import OAIRecordReader

    reader = OAIRecordReader('http://www.digizeitschriften.de/oai2/')
    for record in reader:
        print(record)

.. warning::

   This will retrieve **ALL** records provided by the OAI-PMH server, which can take a significant amount of time.

Limiting the number of records
++++++++++++++++++++++++++++++

To retrieve the first n records:

.. sourcecode:: python

    from polymatheia.data.reader import OAIRecordReader

    reader = OAIRecordReader('http://www.digizeitschriften.de/oai2/', max_records=10)
    for record in reader:
        print(record)

.. note::

   Whether running this code repeatedly returns the same records depends on the OAI-PMH server implementation.
   Polymatheia cannot guarantee any order.

Selecting by set
++++++++++++++++

To retrieve only those records that are in a set, provide the set specifier via the ``set_spec`` parameter:

.. sourcecode:: python

    from polymatheia.data.reader import OAIRecordReader

    reader = OAIRecordReader('http://www.digizeitschriften.de/oai2/', max_records=10, set_spec='EU')
    for record in reader:
        print(record)

Selecting the metadata format
+++++++++++++++++++++++++++++

To retrieve the records in a specific metadata format, provide the format identifier via the ``metadata_prefix``
parameter:

.. sourcecode:: python

    from polymatheia.data.reader import OAIRecordReader

    reader = OAIRecordReader('http://www.digizeitschriften.de/oai2/', max_records=10, metadata_prefix='mets')
    for record in reader:
        print(record)
