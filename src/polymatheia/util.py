"""Utility classes and functions."""
import re


class NavigableDict(dict):
    """The :class:`~polymatheia.util.NavigableDict` is a ``dict`` subclass that allows access via dot notation.

    >>> test = NavigableDict(one='1')
    >>> test.one
    1
    >>> test['one']
    1

    The :class:`~polymatheia.util.NavigableDict` works like a ``dict`` in any other respect.
    """

    def __init__(self, *args, **kwargs):
        """Initialise the :class:`~polymatheia.util.NavigableDict`, ensuring that data is coerced."""
        self.update(*args, **kwargs)

    def __getattr__(self, key):
        """Retrieve the value with the given ``key``.

        :return: The value for the ``key``
        :raises KeyError: If no value exists for ``key``
        """
        return self[key]

    def __setattr__(self, key, value):
        """Set the ``value`` for ``key``.

        This method automatically coerces any ``dict`` ``value`` into :class:`~polymatheia.util.NavigableDict`.

        :param key: The key to set the value for
        :type key: ``string``
        :param value: The value to set
        """
        if isinstance(value, dict):
            if isinstance(value, NavigableDict):
                self[key] = value
            else:
                self[key] = NavigableDict(value)
        else:
            self[key] = value

    def __delattr__(self, key):
        """Delete the value with the given ``key``.

        :raises KeyError: If no value exists for ``key``
        """
        del self[key]

    def update(self, *args, **kwargs):
        """Update the content of this :class:`~polymatheia.util.NavigableDict`.

        Any ``dict`` passed will be coerced into :class:`~polymatheia.util.NavigableDict`
        """
        for key, value in dict(*args, **kwargs).items():
            setattr(self, key, value)


def namespace_mapping(identifier, namespaces):
    """Get the namespace-mapped version of the ``identifier``.

    If the ``identifier`` has a namespace, then this is looked up in the ``namespaces`` dictionary. If the namespace
    is found, then it returns text in the format ``ns_localName``.

    :param identifier: The identifier to map
    :type identifier: ``string``
    :param namespaces: Namespaces to use for mapping
    :type namespaces: ``dict``
    """
    if namespaces:
        match = re.fullmatch(r'(?:\{([^}]+)\})?(.+)', identifier)
        if match:
            if match.group(1) in namespaces:
                if namespaces[match.group(1)]:
                    return f'{namespaces[match.group(1)]}_{match.group(2)}'
                else:
                    return match.group(2)
    return identifier


def xml_to_navigable_dict(node):
    r"""Convert the XML node to a dictionary.

    Child ``node``\ s are returned as keys of the dictionary. Where a ``node`` occurs multiple times, the key returns
    a list of dictionaries for the children. This means that the ordering information in the original XML document is
    **lost**. All attributes are available via the ``_attrib`` key. The ``node``\ 's text is available via the
    ``_text`` key and any text that directly follows the ``node`` is available via the ``_tail`` key.

    :param node: The XML node to convert
    :type node: ``~lxml.etree.Element`
    :return: The dictionary representation of the XML node
    :rtype: :class:`~polymatheia.util.NavigableDict`
    """
    namespaces = dict([(v, k) for k, v in node.nsmap.items()])
    tmp = {'_text': node.text,
           '_tail': node.tail,
           '_attrib': {}}
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
