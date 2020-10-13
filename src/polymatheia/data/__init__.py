"""The classes in the :mod:`polymatheia.data` package handle data input and output."""
import json

from polymatheia.util import namespace_mapping


class NavigableDict(dict):
    """The :class:`~polymatheia.data.NavigableDict` is a ``dict`` subclass that allows access via dot notation.

    >>> test = NavigableDict(one='1')
    >>> test.one
    1
    >>> test['one']
    1

    The :class:`~polymatheia.data.NavigableDict` works like a ``dict`` in any other respect.
    """

    def __init__(self, *args, **kwargs):
        """Initialise the :class:`~polymatheia.data.NavigableDict`, ensuring that data is coerced."""
        self.update(*args, **kwargs)

    def __getattr__(self, key):
        """Retrieve the value with the given ``key``.

        :return: The value for the ``key``
        :raises KeyError: If no value exists for ``key``
        """
        return self[key]

    def __setattr__(self, key, value):
        """Set the ``value`` for ``key``.

        This method automatically coerces any ``dict`` ``value`` into :class:`~polymatheia.data.NavigableDict`.

        :param key: The key to set the value for
        :type key: ``string``
        :param value: The value to set
        """
        if isinstance(value, dict):
            if isinstance(value, NavigableDict):
                self[key] = value
            else:
                self[key] = NavigableDict(value)
        elif isinstance(value, list):
            self[key] = [v if isinstance(v, NavigableDict) else
                         NavigableDict(v) if isinstance(v, dict)
                         else v for v in value]
        else:
            self[key] = value

    def __delattr__(self, key):
        """Delete the value with the given ``key``.

        :raises KeyError: If no value exists for ``key``
        """
        del self[key]

    def __str__(self):
        """Return a pretty-printed JSON representation."""
        return json.dumps(self, indent=2)

    def update(self, *args, **kwargs):
        """Update the content of this :class:`~polymatheia.data.NavigableDict`.

        Any ``dict`` passed will be coerced into :class:`~polymatheia.data.NavigableDict`
        """
        for key, value in dict(*args, **kwargs).items():
            setattr(self, key, value)

    def get(self, path, default=None):
        r"""Get the value specified by the ``path``.

        The ``path`` can either be a ``str``, in which case it is split into its component parts. If it is a ``list``
        then it is used as is. The following ``str`` ``path`` structures are supported:

        * ``x``: Get the value with the key ``'x'``
        * ``x.y``: Get the value with the key ``'x'`` and then within that the key ``'y'``
        * ``x.a``: Get the list with the key ``'x'`` and in that returns the ``a``\ -th element in the list
        * ``x[a]``: Get the list with the key ``'x'`` and in that returns the ``a``\ -th element in the list

        In general the ``list`` format is only needed if one of the parts used in the ``path`` contains a ``'.'``,
        ``'['``, or ``']'``.

        This differs from just using attribute access, in how it handles lists. If a value is a list and the next path
        element is not a list index, then it will return a list, applying the remainder of the path to each element
        in the list.

        :param path: The path to get the value for
        :type path: ``str`` or ``[str, ...]``
        :param default: The default value to return if the ``path`` does not identify a value
        :return: The value identified by ``path`` or the ``default`` value
        """
        if isinstance(path, str):
            path = self._split_path(path)
        if len(path) == 1:
            if path[0] in self:
                return self[path[0]]
        elif len(path) > 1:
            if path[0] in self:
                child = self[path[0]]
                if isinstance(child, NavigableDict):
                    return child.get(path[1:], default=default)
                elif isinstance(child, list):
                    try:
                        element = child[int(path[1])]
                        if len(path) == 2:
                            return element
                        elif isinstance(element, NavigableDict):
                            return element.get(path[2:], default=default)
                    except ValueError:
                        result = []
                        for element in child:
                            if isinstance(element, NavigableDict):
                                result.append(element.get(path[1:]))
                            else:
                                result.append(default)
                        return result
                    except IndexError:
                        pass
        return default

    def set(self, path, value):
        r"""Set the ``value`` at the location specified by ``path``.

        The ``path`` can either be a ``str``, in which case it is split into its component parts. If it is a ``list``
        then it is used as is. The following ``str`` ``path`` structures are supported:

        * ``x``: Set the value with the key ``'x'``
        * ``x.y``: Set the value with the key ``'x'`` and then within that the key ``'y'``
        * ``x.a``: Set the list with the key ``'x'`` and in that set the ``a``\ -th element in the list
        * ``x[a]``: Set the list with the key ``'x'`` and in that set the ``a``\ -th element in the list

        In general the ``list`` format is only needed if one of the parts used in the ``path`` contains a ``'.'``,
        ``'['``, or ``']'``.

        :param path: The path to set the value for
        :type path: ``str`` or ``[str, ...]``
        :param value: The value to set
        """
        if isinstance(path, str):
            path = self._split_path(path)
        tmp = self
        for idx, element in enumerate(path):
            if idx == len(path) - 1:
                if isinstance(tmp, list):
                    tmp[int(element)] = value
                else:
                    setattr(tmp, element, value)
            else:
                if isinstance(tmp, list):
                    tmp = tmp[int(element)]
                else:
                    if element not in tmp:
                        tmp[element] = NavigableDict({})
                    tmp = tmp[element]

    def merge(self, other):
        """Merge the ``other`` values.

        Unlike the :meth:`~polymatheia.data.NavigableDict.update` method, this method does not immediately overwrite
        any existing values. Instead if both the new and existing value are :class:`~polymatheia.data.NavigableDict`,
        then the values from the ``other`` :class:`~polymatheia.data.NavigableDict` are merged into the existing
        :class:`~polymatheia.data.NavigableDict`. Similarly, if both the new and existing value are ``list``, then
        the new existing list is extended with the new list. If neither of these conditions hold, then the existing
        value is overwritten by the new value.
        """
        if isinstance(other, dict) and not isinstance(other, NavigableDict):
            other = NavigableDict(other)
        for key, value in other.items():
            if key in self:
                if isinstance(self[key], NavigableDict) and isinstance(value, NavigableDict):
                    self[key].merge(value)
                elif isinstance(self[key], list) and isinstance(value, list):
                    self[key].extend(value)
                else:
                    setattr(self, key, value)
            else:
                setattr(self, key, value)

    def _split_path(self, path):
        """Split the ``path`` into a ``tuple``.

        The ``path`` is split on ``'.'``. Additionally, if list indexes are identified via ``[...]``, then the
        ``path`` is also split on those.

        :param path: The path to split into its parts
        :type path: ``str``
        :return: The ``path`` as a ``tuple``
        :rtype: ``tuple`` of ``str``
        """
        result = []
        tmp = []
        for character in path:
            if character == '.':
                if tmp:
                    result.append(''.join(tmp))
                tmp = []
            elif character == '[':
                if tmp:
                    result.append(''.join(tmp))
                tmp = []
            elif character == ']':
                if tmp:
                    result.append(''.join(tmp))
                tmp = []
            else:
                tmp.append(character)
        if tmp:
            result.append(''.join(tmp))
        return tuple(result)


class NavigableDictIterator(object):
    """The :class:`~polymatheia.data.NavigableDictIterator` maps values to :class:`~polymatheia.data.NavigableDict`.

    If the iterator it wraps returns ``dict`` objects, then these are simply converted into
    :class:`~polymatheia.data.NavigableDict` objects. If a ``mapper`` function is provided, then this function is
    called with each value and it must return a ``dict`` object that is then converted into a
    :class:`~polymatheia.data.NavigableDict` object. Otherwise a :class:`~polymatheia.data.NavigableDict` is returned
    that has a single key ``value``, with the wrapped iterator value.
    """

    def __init__(self, it, mapper=None):
        """Create a new :class:`~polymatheia.data.NavigableDictIterator`.

        :param it: The iterator that provides the values.
        :param mapper: An optional mapping function converting a single iterator value into a ``dict`` object.
        """
        self._it = it
        self._mapper = mapper

    def __iter__(self):
        """Return this :class:`~polymatheia.data.NavigableDictIterator` as the iterator."""
        return self

    def __next__(self):
        """Return the next :class:`~polymatheia.data.NavigableDict`.

        :raises StopIteration: If no more :class:`~polymatheia.data.NavigableDict` are available
        """
        value = next(self._it)
        if self._mapper:
            return NavigableDict(self._mapper(value))
        elif isinstance(value, dict):
            return NavigableDict(value)
        else:
            return NavigableDict({'value': value})


class LimitingIterator(object):
    """The :class:`~polymatheia.data.LimitingIterator` limits the number of records returned from a wrapped iterator."""

    def __init__(self, it, max_records):
        """Create a new :class:`~polymatheia.data.LimitingIterator`.

        :param it: The wrapped iterator.
        :param max_records: The maximum number of records to return.
        :type max_records: ``number``
        """
        self._it = it
        self._max_records = max_records

    def __iter__(self):
        """Return this :class:`~polymatheia.data.LimitingIterator` as the iterator."""
        return self

    def __next__(self):
        """Return the next value.

        :raises StopIteration: If no more values are available
        """
        if self._max_records <= 0:
            raise StopIteration()
        self._max_records = self._max_records - 1
        return next(self._it)


def xml_to_navigable_dict(node):
    r"""Convert the XML node to a dictionary.

    Child ``node``\ s are returned as keys of the dictionary. Where a ``node`` occurs multiple times, the key returns
    a list of dictionaries for the children. This means that the ordering information in the original XML document is
    **lost**. All attributes are available via the ``_attrib`` key. The ``node``\ 's text is available via the
    ``_text`` key and any text that directly follows the ``node`` is available via the ``_tail`` key.

    :param node: The XML node to convert
    :return: The dictionary representation of the XML node
    :rtype: :class:`~polymatheia.data.NavigableDict`
    """
    namespaces = dict([(v, k) for k, v in node.nsmap.items()])
    tmp = {}
    if node.text:
        tmp['_text'] = node.text
    if node.tail:
        tmp['_tail'] = node.tail
    if len(node.attrib) > 0:
        tmp['_attrib'] = {}
    for key, value in node.attrib.items():
        tmp['_attrib'][namespace_mapping(key, namespaces)] = value
    for child in node:
        if namespace_mapping(child.tag, namespaces) in tmp:
            if not isinstance(tmp[namespace_mapping(child.tag, namespaces)], list):
                tmp[namespace_mapping(child.tag, namespaces)] = [tmp[namespace_mapping(child.tag, namespaces)]]
            tmp[namespace_mapping(child.tag, namespaces)].append(xml_to_navigable_dict(child))
        else:
            tmp[namespace_mapping(child.tag, namespaces)] = xml_to_navigable_dict(child)
    return NavigableDict(tmp)
