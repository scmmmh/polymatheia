Reading and Writing XML Data
============================

For performance and replicability reasons it is generally better to keep a local copy of the data-set that is being
worked on. Polymatheia supports this in two ways, either using :doc:`JSON <json>` or using XML.

Writing XML data
----------------

To store data locally, use the :class:`~polymatheia.data.writer.XMLWriter`, providing the name of the directory to
store the data in and the dotted path to the field that contains each record's unique identifier:

.. sourcecode:: python

    from polymatheia.data.reader import EuropeanaSearchReader
    from polymatheia.data.writer import XMLWriter

    EUROPEANA_API_KEY = 'Put your key here'
    reader = EuropeanaSearchReader(EUROPEANA_API_KEY, 'Gutzkow OR Zäunemann OR Heyse')
    writer = XMLWriter('europeana_xml', 'guid')
    writer.write(reader)

The filename is calculated as a sha-256 digest of the value of the unique identifier. Thus if the identifier is not
actually unique, data will be overwritten and lost.

.. warning::

   The :class:`~polymatheia.data.writer.XMLWriter` will ensure that all keys are transformed into valid XML tag names.
   This means that if a key is not a valid XML tag name, then it will automatically be transformed into a valid XML
   tag name. As a result it is not possible to guarantee that a record saved with the
   :class:`~polymatheia.data.writer.XMLWriter` will have exactly the same keys after loading with the
   :class:`~polymatheia.data.reader.XMLReader`.

   Thus in practice it is recommended that you use :doc:`JSON <json>` as the format for locally storing data, as this
   guarantees that the records remain unchanged.

Reading XML data
----------------

To load data stored locally, use the :class:`~polymatheia.data.reader.XMLReader`, providing the name of the directory
that contains the data to load:

.. sourcecode:: python

    from polymatheia.data.reader import XMLReader

    reader = XMLReader('europeana_xml')
    for record in reader:
        print(record)

This will work with any data stored as XML, not just with data stored using the
:class:`~polymatheia.data.writer.XMLWriter`. The only requirements are that the files to load must have ".xml" as
their extension and each file must contain **exactly one** record.

.. note::

    The order of records is defined by order in which filenames are listed by the underlying operating system. As such
    no order can be guaranteed.
