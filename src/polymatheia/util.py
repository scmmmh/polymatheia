"""Utility classes and functions."""
import re


def namespace_mapping(identifier, namespaces):
    """Get the namespace-mapped version of the ``identifier``.

    If the ``identifier`` has a namespace, then this is looked up in the ``namespaces`` dictionary. If the namespace
    is found, then it returns text in the format ``ns_localName``.

    :param identifier: The identifier to map
    :type identifier: ``string``
    :param namespaces: Namespaces to use for mapping
    :type namespaces: ``dict``
    """
    if namespaces and identifier:
        match = re.fullmatch(r'(?:\{([^}]+)\})?(.+)', identifier)
        if match:
            if match.group(1) in namespaces:
                if namespaces[match.group(1)]:
                    return f'{namespaces[match.group(1)]}_{match.group(2)}'
                else:
                    return match.group(2)
    return identifier
