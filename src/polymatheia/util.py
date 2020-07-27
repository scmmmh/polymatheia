"""Utility classes and functions."""


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
