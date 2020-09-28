"""This is the main package for the Polymatheia library."""
try:
    from importlib.metadata import version
    __version__ = version('polymatheia')
except Exception:
    import pkg_resources
    __version__ = pkg_resources.get_distribution('polymatheia').version
