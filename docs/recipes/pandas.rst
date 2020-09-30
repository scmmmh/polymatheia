Exporting Data to Pandas
========================

Polymatheia supports exporting records into a Pandas :class:`~pandas.DataFrame` for further analysis / visualisation.
To write records to a :class:`~pandas.DataFrame` use the :class:`~polymatheia.data.writer.PandasDFWriter`:

.. sourcecode:: python

    from polymatheia.data.writer import PandasDFWriter

    records = [
        {
            'id': 1,
            'name': 'Test Person',
            'age': 32
        },
        {
            'id': 2,
            'name': 'Another Test Person',
            'age': 19
        },
        {
            'id': 3,
            'name': 'Final Person',
            'age': 64
        }
    ]
    writer = PandasDFWriter()
    df = writer.write(records)

.. important::

    Records that are written to a Pandas :class:`~pandas.DataFrame` must not contain any nested data, as demonstrated
    in the example above. Any reader can also be passed to :meth:`~polymatheia.data.writer.PandasDFWriter.write`,
    however the records provided by that reader must not contain any nested data.

    You can use the :doc:`transformation functionality <transforming>` to convert a nested structure into a a simple
    structure ready for use with :meth:`~polymatheia.data.writer.PandasDFWriter.write`.
