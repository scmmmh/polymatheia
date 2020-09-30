Core Concepts
=============

The functionality provided by the Polymatheia library is built around two concepts:

* The :class:`~polymatheia.data.NavigableDict` as the data-structure used to store all data in the library. The
  :class:`~polymatheia.data.NavigableDict` is a simple extension of the standard ``dict`` that allows for access
  to the values via dot-notation:

  .. sourcecode:: python

      record = NavigableDict({'one': '1', 'two': {'one': '2.1', 'two': '2.2'}})
      record.one      # '1'
      record.two.one  # '2.1'

* All data readers, the filtering, and transformation classes are all designed as iterators, allowing them to be
  chained together however required.
