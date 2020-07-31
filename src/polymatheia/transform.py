r"""The :mod:`~polymatheia.transform` module implements a number of transform classes.

All transform classes use the following transform expression language and are designed to work with
:class:`~polymatheia.data.NavigableDict`. Each transform is structured as follows:
``('operator', 'parameter'[, 'parameter', ...])``. The number of parameters depends on the operator:

* Static: ``('static', target, value)``: The static ``value`` is stored at the location specified by the dotted
  path ``target``.
* Copy: ``('copy', target, source)``: The value specified by the dotted path ``source`` is stored at the location
  specified by the dotted path ``target``.
* Split: ``('split', target, splitter, source): The value specified by the dotted path ``source`` is split and
  stored at the location specified by the dotted path ``target``. If the value is a ``list``, then the list is split
  into its elements. If the value is a ``str``, then it is split using ``splitter`. Because this will produce more
  than one value in the transformation result, the ``target`` can contain the string ``{}``, which is replaced with
  the index of each split value (starting at 1).
* Combine: ``('combine', target, source1, ...)``: The values specified by the dotted paths ``source1`` (and optionally
  ``source2``, ``source3``,...) are combined into a list and stored at the location specified by the dotted path
  ``target``.
* Join: ``('join', target, joiner, source1, ...)``: The values specified by the dotted paths ``source1`` (and
  optionally ``source2``, ``source3``,...) are joined by the ``joiner`` and the result stored at the location specified
  by the dotted path ``target``. If only one ``source`` is specified, this is treated as a ``list`` and the values of
  the ``list`` joined using ``joiner``. If multiple ``source``\ s are specified, then the values returned by each
  dotted ``source`` path are returned.
* sequence: ``('sequence', expression1, expression2, ...)``: Applies the transform expressions in sequence. When using
  the sequence transformation, this should be the only transformation being applied, otherwise the results cannot be
  guaranteed.
"""
from polymatheia.data import NavigableDict


class Transform(object):
    """The :class:`~polymatheia.transform.Transform` is a callable transformation for :class:`~polymatheia.data.NavigableDict`."""  # noqa: E501

    def __init__(self, mappings):
        """Create a new :class:`~polymatheia.transform.Transform`.

        :param mappings: The mappings that are applied when the :class:`~polymatheia.transform.Transform` is called
        :type mappings: ``list``
        """
        self._mappings = []
        for mapping in mappings:
            if mapping[0] == 'sequence':
                self._mappings.append(('sequence', *[Transform([m]) for m in mapping[1:]]))
            else:
                self._mappings.append(mapping)

    def __call__(self, record):
        """Transform the ``record`` according to the mappings of this :class:`~polymatheia.transform.Transform`.

        :param record: The record to transform
        :type record: :class:`~polymatheia.data.NavigableDict`
        :return: The transformed record
        :rtype: :class:`~polymatheia.data.NavigableDict`
        """
        result = NavigableDict({})
        for mapping in self._mappings:
            if mapping[0] == 'copy':
                result.set(mapping[1], record.get(mapping[2]))
            elif mapping[0] == 'static':
                result.set(mapping[1], mapping[2])
            elif mapping[0] == 'split':
                value = record.get(mapping[3])
                if value:
                    if isinstance(value, str):
                        for idx, part in enumerate(value.split(mapping[2])):
                            result.set(mapping[1].format(idx + 1), part)
                    elif isinstance(value, list):
                        for idx, part in enumerate(value):
                            result.set(mapping[1].format(idx + 1), part)
            elif mapping[0] == 'combine':
                result.set(mapping[1], [record.get(path) for path in mapping[2:]])
            elif mapping[0] == 'join':
                if len(mapping) == 4:
                    value = record.get(mapping[3])
                    if value:
                        result.set(mapping[1], mapping[2].join(value))
                else:
                    result.set(mapping[1], mapping[2].join([record.get(path) for path in mapping[3:]]))
            elif mapping[0] == 'sequence':
                tmp = record
                for part in mapping[1:]:
                    result = part(tmp)
                    tmp = result
        return result


class RecordsTransform(object):
    """The :class:`~polymatheia.transform.RecordsTransform` provides a record transformation iterator.

    The actual transformation is performed using a :class:`~polymatheia.transform.Transform` that is applied to
    each record in the source iterator.
    """

    def __init__(self, records, mappings):
        """Create a new :class:`~polymatheia.transform.RecordsTransform`.

        :param records: The source records to iterate over and transform
        :param mappings: The mappings that are applied to each record
        :type mappings: ``list``
        """
        self._it = iter(records)
        self._transform = Transform(mappings)

    def __iter__(self):
        """Return this class:`~polymatheia.transform.RecordsTransform` as the iterator."""
        return self

    def __next__(self):
        """Transform and return the next :class:`~polymatheia.data.NavigableDict` record.

        :return: The transformed record
        :rtype: :class:`~polymatheia.data.NavigableDict`
        :raises StopIteration: If no more records are available
        """
        return self._transform(next(self._it))
