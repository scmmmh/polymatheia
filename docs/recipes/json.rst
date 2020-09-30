Reading and Writing JSON Data
=============================

For performance and replicability reasons it is generally better to keep a local copy of the data-set that is being
worked on. Polymatheia supports this in two ways, either using JSON or using :doc:`XML <xml>`.

Writing JSON data
-----------------

To store data locally, use the :class:`~polymatheia.data.writer.JSONWriter`, providing the name of the directory to
store the data in and the dotted path to the field that contains each record's unique identifier:

.. sourcecode:: python

    from polymatheia.data.reader import EuropeanaSearchReader
    from polymatheia.data.writer import JSONWriter

    EUROPEANA_API_KEY = 'Put your key here'
    reader = EuropeanaSearchReader(EUROPEANA_API_KEY, 'Gutzkow OR Zäunemann OR Heyse')
    writer = JSONWriter('europeana_json', 'guid')
    writer.write(reader)

The filename is calculated as a sha-256 digest of the value of the unique identifier. Thus if the identifier is not
actually unique, data will be overwritten and lost.

Reading JSON data
-----------------

To load data stored locally, use the :class:`~polymatheia.data.reader.JSONReader`, providing the name of the directory
that contains the data to load:

.. sourcecode:: python

    from polymatheia.data.reader import JSONReader

    reader = JSONReader('europeana_json')
    for record in reader:
        print(record)

This will work with any data stored as JSON, not just with data stored using the
:class:`~polymatheia.data.writer.JSONWriter`. The only requirements are that the files to load must have ".json" as
their extension and each file must contain **exactly one** record.

.. note::

    The order of records is defined by order in which filenames are listed by the underlying operating system. As such
    no order can be guaranteed.
