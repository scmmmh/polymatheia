"""The :mod:`~polymatheia.filter` module implements a number of filtering classes.

All filters support the same expression language and are designed to work with the
:class:`~polymatheia.data.NavigableDict`. Each individual expression is structured as follows:
``('operator', 'parameter'[, 'parameter', ...])``. The number of parameters depends on the operator:

* Equal: ``('eq', param1, param2)``: returns ``True`` if the two parameters are equal
* Not-equal: ``('neq', param1, param2)``: returns ``True`` if the two parameters are not equal
* Greater than: ``('gt', param1, param2)``: returns ``True`` if the param1 is greater than param2
* Greater than or equal: ``('gte', param1, param2)``: returns ``True`` if the param1 is greater than or equal to param2
* Less than: ``('lt', param1, param2)``: returns ``True`` if the param1 is less than param2
* Less than or equal: ``('lte', param1, param2)``: returns ``True`` if the param1 is less than or equal to param2
* Containment: ``('contains', param1, param2)``: returns ``True`` if the param2 is contained within param1
* Exists: ``('exists', param1)``: returns ``True`` if the param1 exists and has a value that is not ``None``
* Not: ``('not', expression)``: See below
* And: ``('and', expression1, expression2, ...)``: See below
* Or: ``('and', expression1, expression2, ...)``: See below
* True: ``('true',)``: always returns ``True``
* False: ``('true',)``: always returns ``False``

In the first six expressions both ``param1`` and ``param2`` can be one of the following three, allowing for comparison
of a value from a :class:`~polymatheia.data.NavigableDict` record against a constant value, two values from the same
:class:`~polymatheia.data.NavigableDict` record, or two constant values:

* A constant value: The comparison is performed against this value
* A dotted path: The comparison is performed against the value fetched from the record using the path
* A a list: The comparison is performed against the value fetched from the record using the path in list form. This
  is needed if either the path elements contain a full-stop or square brackets or if you wish to compare against a
  value
  at the top level of the :class:`~polymatheia.data.NavigableDict` record.

For the operators ``'not'``, ``'and'``, and ``'or'`` the ``expression`` parameter is a nested expression using any of
the given operators. The ``'not'`` operator only supports at most a single nested expression. The ``'and'`` and
``'or'`` operators allow any number of nested expression parameters. This

* ``'not'``, ``'and'``, or ``'or'`` with no nested expressions always return ``True``
* ``'and'`` or ``'or'`` with a single nested expression always return the value of the nested expression
* ``'and'`` or ``'or'`` with more than one nested expression are evaluated lazily. That means that for ``'and'`` as
  soon as a nested expression is ``False``, ``False`` is immediately returned. Likewise for ``'or'`` as soon as
  a nested expression is ``True``, then ``True`` is immediately returned.
"""


class Filter(object):
    """The :class:`~polymatheia.filter.Filter` is a callable filter for :class:`~polymatheia.data.NavigableDict`."""

    def __init__(self, expression):
        """Create a new :class:`~polymatheia.filter.Filter`.

        :param expression: The expression that this :class:`~polymatheia.filter.Filter` will apply.
        :type expression: ``tuple``
        """
        if expression[0] == 'not':
            if len(expression) == 1:
                self._expression = ('true',)
            else:
                self._expression = ('not', Filter(expression[1]))
        elif expression[0] == 'and':
            if len(expression) == 2:
                self._expression = expression[1]
            else:
                self._expression = tuple(['and'] + [Filter(exp) for exp in expression[1:]])
        elif expression[0] == 'or':
            if len(expression) == 2:
                self._expression = expression[1]
            else:
                self._expression = tuple(['or'] + [Filter(exp) for exp in expression[1:]])
        else:
            self._expression = expression

    def __call__(self, record):
        """Apply the expression to the ``record``.

        :param record: The record to apply the filter expression to.
        :type record: :class:`~polymatheia.data.NavigableDict`
        :return: Whether the filter expression matches the record or not.
        :rtype: ``bool``
        """
        if self._expression[0] == 'eq':
            return self._get_value(record, self._expression[1]) == self._get_value(record, self._expression[2])
        elif self._expression[0] == 'neq':
            return self._get_value(record, self._expression[1]) != self._get_value(record, self._expression[2])
        elif self._expression[0] == 'gt':
            return self._get_value(record, self._expression[1]) > self._get_value(record, self._expression[2])
        elif self._expression[0] == 'gte':
            return self._get_value(record, self._expression[1]) >= self._get_value(record, self._expression[2])
        elif self._expression[0] == 'lt':
            return self._get_value(record, self._expression[1]) < self._get_value(record, self._expression[2])
        elif self._expression[0] == 'lte':
            return self._get_value(record, self._expression[1]) <= self._get_value(record, self._expression[2])
        elif self._expression[0] == 'contains':
            try:
                return self._get_value(record, self._expression[2]) in self._get_value(record, self._expression[1])
            except TypeError:
                return False
        elif self._expression[0] == 'exists':
            return self._get_value(record, self._expression[1]) is not None
        elif self._expression[0] == 'not':
            return not self._expression[1](record)
        elif self._expression[0] == 'and':
            for part in self._expression[1:]:
                if not part(record):
                    return False
            return True
        elif self._expression[0] == 'or':
            all_false = False
            for part in self._expression[1:]:
                if part(record):
                    return True
                else:
                    all_false = True
            return not all_false
        elif self._expression[0] == 'true':
            return True
        elif self._expression[0] == 'false':
            return False
        return False

    def _get_value(self, record, path):
        if isinstance(path, str) and ('.' in path or ('[' in path and ']' in path)):
            return record.get(path)
        elif isinstance(path, list):
            return record.get(path)
        else:
            return path


class RecordsFilter(object):
    """The :class:`~polymatheia.filter.RecordsFilter` provides a records filter iteration container.

    It allows iterating over all :class:`~polymatheia.data.NavigableDict` that match the given filter expression.
    Filtering is performed using a :class:`~polymatheia.filter.Filter`.
    """

    def __init__(self, records, expression):
        """Create a new :class:`~polymatheia.filter.RecordsFilter`.

        :param records: The source records to iterate over and filter.
        :param expression: The filter expression to apply
        :type expression: ``tuple`` or :class:`~polymatheia.filter.Filter`
        """
        self._records = records
        self._expression = expression

    def __iter__(self):
        """Return a new class:`~polymatheia.filter.RecordsFilterIterator` as the iterator."""
        return RecordsFilterIterator(self._records, self._expression)


class RecordsFilterIterator(object):
    """The :class:`~polymatheia.filter.RecordsFilterIterator` provides a records filter iterator.

    It allows iterating over all :class:`~polymatheia.data.NavigableDict` that match the given filter expression.
    Filtering is performed using a :class:`~polymatheia.filter.Filter`.
    """

    def __init__(self, records, expression):
        """Create a new :class:`~polymatheia.filter.RecordsFilterIterator`.

        :param records: The source records to iterate over and filter.
        :param expression: The filter expression to apply
        :type expression: ``tuple`` or :class:`~polymatheia.filter.Filter`
        """
        self._it = iter(records)
        if isinstance(expression, Filter):
            self._expression = expression
        else:
            self._expression = Filter(expression)

    def __iter__(self):
        """Return this class:`~polymatheia.filter.RecordsFilterIterator` as the iterator."""
        return self

    def __next__(self):
        """Return the next :class:`~polymatheia.data.NavigableDict` that matches the filter.

        :return: The next record that matches the filter
        :rtype: :class:`~polymatheia.data.NavigableDict`
        :raises StopIteration: If no more records are available
        """
        record = next(self._it)
        while not self._expression(record):
            record = next(self._it)
        return record
