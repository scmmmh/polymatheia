"""The classes in the :mod:`~polymatheia.data` package handle data input and output."""
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
                        pass
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
                if element not in tmp:
                    tmp[element] = NavigableDict({})
                if isinstance(tmp, list):
                    tmp = tmp[int(element)]
                else:
                    tmp = tmp[element]

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


def xml_to_navigable_dict(node):
    r"""Convert the XML node to a dictionary.

    Child ``node``\ s are returned as keys of the dictionary. Where a ``node`` occurs multiple times, the key returns
    a list of dictionaries for the children. This means that the ordering information in the original XML document is
    **lost**. All attributes are available via the ``_attrib`` key. The ``node``\ 's text is available via the
    ``_text`` key and any text that directly follows the ``node`` is available via the ``_tail`` key.

    :param node: The XML node to convert
    :type node: ``~lxml.etree.Element`
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
