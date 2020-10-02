Loading Data via SRU
====================

Polymatheia supports accessing metadata records via the `SRU`_ protocol. SRU (Search/Retrieve via URL) is
a standard XML-based protocol for search queries, utilizing CQL (Contextual Query Language),
a standard syntax for representing queries. Each web service that implements the SRU protocol should
provide an `Explain record`_ at its base URL that allows a client to retrieve a
description of the facilities available at this SRU server.

.. _`SRU`: http://www.loc.gov/standards/sru/
.. _`Explain record`: http://www.loc.gov/standards/sru/explain/

Getting the Explain record
--------------------------

Use the :class:`~polymatheia.data.reader.SRUExplainRecordReader`. Polymatheia provides direct
access to the record schemas that can be used with the SRU web service as well as to the echoed request
(i.e., the request parameters echoed back to the client).

.. sourcecode:: python

    from polymatheia.data.reader import SRUExplainRecordReader

    reader = SRUExplainRecordReader("http://sru.k10plus.de/gvk")
    for record in reader:
        print(record)

    print(reader.schemas)
    print(reader.echo)

Fetching records
----------------

Use the class :class:`~polymatheia.data.reader.SRURecordReader` to query an SRU server.
Provide a parameter ``max_records`` that specifies the desired number of records to return:

.. sourcecode:: python

    from polymatheia.data.reader import SRURecordReader

    reader = SRURecordReader("http://sru.k10plus.de/gvk",
                             query="dog cat mouse",
                             max_records=10)
    for record in reader:
        print(record)

.. note::

    This will either retrieve exactly *n* records that match the query or less.
    It is a good idea to check the total number of records a query retrieves beforehand (see below).

Getting the total number of records for a query
+++++++++++++++++++++++++++++++++++++++++++++++

The function ``result_count`` of :class:`~polymatheia.data.reader.SRURecordReader`
returns the number of records that match the given query. Checking this value in advance allows to
specify the ``max_records`` as necessary. After starting iterating over an
:class:`~polymatheia.data.reader.SRURecordReader`, the result count is also available as a
class attribute:

.. sourcecode:: python

    from polymatheia.data.reader import SRURecordReader

    result_count = SRURecordReader.result_count("http://sru.k10plus.de/gvk",
                                                query="dog cat mouse")
    print(result_count)

    reader = SRURecordReader("http://sru.k10plus.de/gvk",
                             query="dog cat mouse",
                             max_records=result_count)  # to retrieve all records
    for record in reader:
        print(reader.result_count)
        break


Selecting a recordSchema
++++++++++++++++++++++++

Passing the parameter ``record_schema``, i.e. a metadata format, to the :class:`~polymatheia.data.reader.SRURecordReader` returns all
records in this format:

.. sourcecode:: python

    from polymatheia.data.reader import SRURecordReader

    reader = SRURecordReader("http://sru.k10plus.de/gvk",
                             query="dog cat mouse",
                             max_records=10,
                             record_schema="mods"
                             )
    for record in reader:
        print(record)

.. note::

    See the SRU Explain record of the appropriate web service for all supported record schemas.
    Also, consider the `SRU specification`_ for more details about other available SRU parameters.

.. _`SRU specification`: http://www.loc.gov/standards/sru/


Getting the echoed request
++++++++++++++++++++++++++

The ``echo`` attribute of :class:`~polymatheia.data.reader.SRURecordReader`
echoes the request parameters back to the client. It is available after starting the iteration:

.. sourcecode:: python

    from polymatheia.data.reader import SRURecordReader

    reader = SRURecordReader("http://sru.k10plus.de/gvk",
                             query="dog cat mouse",
                             max_records=10)
    for record in reader:
        print(reader.echo)
        break