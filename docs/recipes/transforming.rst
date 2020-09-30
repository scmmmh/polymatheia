Transforming Data
=================

Polymatheia provides a simple language for transforming one record structure into another. The primary use for this
is to map the nested record structure provided by most archives into the flat structure needed for outputting to
:doc:`CSV <csv>` or :doc:`Pandas <pandas>` for further processing.

Basic transformations
---------------------

The transformations use tuples, similar to the way the :doc:`filtering <filtering>` works. The following basic
transforms are supported:

* :code:`('copy', target, source)`: copy the value identified by the dotted path ``source`` to the location specified
  by the dotted path ``target``.
* :code:`('static', target, value)`: set the static ``value`` at the location specified by the dotted path ``target``.
* :code:`('fill', target, value)`: set the static ``value`` at the location specified by the dotted path ``target``
  **IF** there is no pre-existing value at the dotted path ``target`` or if that value is :code:`None`.
* :code:`('join', target, joiner, source1, source2, ...)`: join together the values identified by the dotted paths
  ``source1``, ``source2``, ... using the string ``joiner`` and set it at the location specified by the dotted path
  ``target``.
* :code:`('custom', target, function)`: call the function ``function`` with the record as the parameter and store
  the returned value at the location specified by the dotted path ``target``.

The following code copies the first value from the ``dcLanguage`` field in the source record into a ``lang`` field in
the result record:

.. sourcecode:: python

    from polymatheia.data.reader import LocalReader
    from polymatheia.transform import RecordsTransform

    reader = LocalReader('europeana_json')
    mapping = ('copy', 'lang', 'dcLanguage[0]')
    transformed = RecordsTransform(reader, mapping)
    for record in transformed:
        print(record)

Joining values
++++++++++++++

To join values from different source fields use the following code:

.. sourcecode:: python

    from polymatheia.data.reader import LocalReader
    from polymatheia.filter import RecordsFilter
    from polymatheia.transform import RecordsTransform

    reader = LocalReader('europeana_json')
    filtered = RecordsFilter(reader, ('and', ('exists', ['edmPlaceLatitude']), ('exists', ['edmPlaceLongitude'])))
    mapping = ('join', 'lat_lon', ',', 'edmPlaceLatitude[0]', 'edmPlaceLongitude[0]')
    transformed = RecordsTransform(filtered, mapping)
    for record in transformed:
        print(record)

Custom transformations
++++++++++++++++++++++

The ``custom`` transformation allows for custom transformation defined either via lambda functions or full functions:

.. sourcecode:: python

    mapping = ('custom', 'title_tokens', lambda record: len(record.title[0].split()))
    transformed = RecordsTransform(reader, mapping)
    for record in transformed:
        print(record)

The transformation function must take a single parameter, which is the source record, and return a single value.

Complex transformations
-----------------------

Two types of complex transformations are provided by Polymatheia. Parallel transformations result in output records
that have more than one field, while sequential transformations allow for transformations to be run in sequence.

Parallel transformations
++++++++++++++++++++++++

Parallel transformations make it possible to create transformed records that have multiple fields:

.. sourcecode:: python

    from polymatheia.data.reader import LocalReader
    from polymatheia.filter import RecordsFilter
    from polymatheia.transform import RecordsTransform

    reader = LocalReader('europeana_json')
    filtered = RecordsFilter(reader, ('and', ('exists', ['edmPlaceLatitude']), ('exists', ['edmPlaceLongitude'])))
    mapping = ('parallel', ('copy', 'id', 'id'),
                           ('copy', 'lang', 'dcLanguage[0]'),
                           ('join', 'lat_lon', ',', 'edmPlaceLatitude[0]', 'edmPlaceLongitude[0]'),
                           ('custom', 'title_tokens', lambda record: len(record.title[0].split())))
    transformed = RecordsTransform(filtered, mapping)
    for record in transformed:
        print(record)

Sequential transformations
++++++++++++++++++++++++++

The most common sequential transformation is to use a ``copy`` transformation to copy a value, followed by a ``fill``
transformation to set an explicit "missing" value:

.. sourcecode:: python

    from polymatheia.data.reader import LocalReader
    from polymatheia.filter import RecordsFilter
    from polymatheia.transform import RecordsTransform

    reader = LocalReader('europeana_json')
    mapping = ('sequence', ('copy', 'lang', 'dcLanguage[0]'),
                           ('fill', 'lang', 'NA'))
    transformed = RecordsTransform(reader, mapping)
    for record in transformed:
        print(record)

This works because the ``copy`` transformation sets the result value to :code:`None`, if there is no value at the
dotted path in the source record. These :code:`None` values are then filled using the ``fill`` transformation.

Complete example
++++++++++++++++

Here is an more complete example combining parallell and sequential transformations:

.. sourcecode:: python

    from polymatheia.data.reader import LocalReader
    from polymatheia.filter import RecordsFilter
    from polymatheia.transform import RecordsTransform

    reader = LocalReader('europeana_json')
    filtered = RecordsFilter(reader, ('and', ('exists', ['edmPlaceLatitude']), ('exists', ['edmPlaceLongitude'])))
    mapping = ('parallel', ('copy', 'id', 'id'),
                           ('sequence', ('copy', 'lang', 'dcLanguage[0]'),
                                        ('fill', 'lang', 'NA')),
                           ('join', 'lat_lon', ',', 'edmPlaceLatitude[0]', 'edmPlaceLongitude[0]'),
                           ('custom', 'title_tokens', lambda record: len(record.title[0].split())))
    transformed = RecordsTransform(filtered, mapping)
    for record in transformed:
        print(record)
