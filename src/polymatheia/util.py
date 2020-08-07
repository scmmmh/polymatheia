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


def identifier_to_directory_structure(identifier):
    """Convert an identifier into a list for use as a directory structure.

    If the ``identifier`` follows the guidelines for OAI identifiers (oai:domain:localIdentifier), then the resulting
    list is ``[domain, splitLocalIdentifier]``. If not, then the whole ``identifier`` is treated as the
    ``localIdentifier`` and the resulting list is ``[splitIdentifier]``. The local or complete identifier is split
    into 2 character chunks.

    :param identifier: The identifier to split
    :type identifier: ``string``
    :return: The list of directory elements
    :rtype: ``list`` of ``string``
    """
    match = re.fullmatch(r'(?:[^:]+:([^:]+):)?(.+)', identifier)
    if match:
        result = []
        if (match.group(1)):
            result.append(match.group(1))
        local_identifier = match.group(2)
        for idx in range(0, len(local_identifier), 2):
            result.append(local_identifier[idx:idx + 2])
        return result
    else:
        raise Exception('The identifier must contain at least one character')
