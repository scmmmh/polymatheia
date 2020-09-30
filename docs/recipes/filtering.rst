Filtering Data
==============

Polymatheia provides a simple filtering language to remove records that are not needed for further processing. All
filtering is performed using the :class:`polymatheia.filter.RecordsFilter`. All filters are specified using tuples.

Basic filters
-------------

The basic filters provided by Polymatheia allow you to compare a value in a record to a fixed value:

* :code:`('true',)`: Lets any record pass.
* :code:`('false',)`: Lets no record pass.
* :code:`('eq', a, b)`: Lets the record pass if the value of :code:`a` is equal to the value of :code:`b`.
* :code:`('neq', a, b)`: Lets the record pass if the value of :code:`a` is not equal to the value of :code:`b`.
* :code:`('gt', a, b)`: Lets the record pass if the value of :code:`a` is greater than the value of :code:`b`.
* :code:`('gte', a, b)`: Lets the record pass if the value of :code:`a` is greater than or equal to the value of
  :code:`b`.
* :code:`('lt', a, b)`: Lets the record pass if the value of :code:`a` is less than the value of :code:`b`.
* :code:`('lte', a, b)`: Lets the record pass if the value of :code:`a` is less than or equal to the value of
  :code:`b`.
* :code:`('contains', a, b)`: Lets the record pass if the value of :code:`a` is contains the value of :code:`b`.
* :code:`('exists', a)`: Lets the record pass if the value of :code:`a` is not :code:`None`.

Where the filter expression contains :code:`a` and :code:`b`, either of these can be one of:

* A dotted string: in this case the value to be compared is taken from the record using the dotted string to identify
  the value to compare.
* A list: the value to be compared is taken from the record using the list to identify the value to compare.
* Anything else: the value is compared as is.

.. sourcecode:: python

    from polymatheia.data.reader import LocalReader
    from polymatheia.filter import RecordsFilter

    reader = LocalReader('europeana_json')
    fltr = ('eq', ['type'], 'IMAGE')
    images = RecordsFilter(reader, fltr)
    for record in images:
        print(record)

Compound filters
----------------

Filters can be combined into more complex filter expressions using the following compound filters:

* :code:`('not', filter_expression)`: Lets the record pass if the :code:`filter_expression` is not :code:`True`.
* :code:`('or', filter_expression_1, ..., filter_expression_n)`: Lets the record pass if one or more of the
  :code:`filter_expression_1` to :code:`filter_expression_n` is :code:`True`.
* :code:`('and', filter_expression_1, ..., filter_expression_n)`: Lets the record pass only if all
  :code:`filter_expression_1` to :code:`filter_expression_n` are :code:`True`.

The negation filter ``not`` is primarily needed with the ``contains`` filter, as the other basic filters provide
explicit negation filters:

.. sourcecode:: python

    from polymatheia.data.reader import LocalReader
    from polymatheia.filter import RecordsFilter

    reader = LocalReader('europeana_json')
    fltr = ('not', ('contains', ['dcLanguage'], 'de'))
    not_german = RecordsFilter(reader, fltr)
    for record in not_german:
        print(record)

The ``or`` and ``and`` filters use standard boolean logic for evaluation:

.. sourcecode:: python

    from polymatheia.data.reader import LocalReader
    from polymatheia.filter import RecordsFilter

    reader = LocalReader('europeana_json')
    fltr = ('or', ('contains', ['dcLanguage'], 'de'), ('contains', ['dcLanguage'], 'ger'))
    full_german = RecordsFilter(reader, fltr)
    for record in full_german:
        print(record)

.. sourcecode:: python

    from polymatheia.data.reader import LocalReader
    from polymatheia.filter import RecordsFilter

    reader = LocalReader('europeana_json')
    fltr = ('and', ('contains', ['dcLanguage'], 'de'), ('eq', ['type'], 'IMAGE'))
    german_images = RecordsFilter(reader, fltr)
    for record in german_images:
        print(record)

The compound filters can themselves be nested:

.. sourcecode:: python

    from polymatheia.data.reader import LocalReader
    from polymatheia.filter import RecordsFilter

    reader = LocalReader('europeana_json')
    fltr = ('and',
                ('or',
                    ('contains', ['dcLanguage'], 'de'),
                    ('contains', ['dcLanguage'], 'ger')),
                ('eq', ['type'], 'IMAGE'))
    full_german_images = RecordsFilter(reader, fltr)
    for record in full_german_images:
        print(record)
