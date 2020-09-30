Reading and Writing CSV Data
============================

Polymatheia supports CSV both as an input and output format.

Reading CSV data
----------------

To read records from a CSV file, use the :class:`~polymatheia.data.reader.CSVReader`, passing the filename of the CSV
file to load:

.. sourcecode:: python

    from polymatheia.data.reader import CSVReader

    reader = CSVReader('filename.csv')
    for record in reader:
        print(record)

Each row in the CSV file will become one record and each column a key within that record.

Writing CSV data
----------------

To write records to a CSV file, use the :class:`~polymatheia.data.writer.CSVWriter`, passing the filename to write the
CSV file to:

.. sourcecode:: python

    from polymatheia.data.writer import CSVWriter

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
    writer = CSVWriter('people.csv')
    writer.write(records)

.. important::

    Records that are written to a CSV file must not contain any nested data, as demonstrated in the example above.
    Any reader can also be passed to :meth:`~polymatheia.data.writer.CSVWriter.write`, however the records provided
    by that reader must not contain any nested data.

    You can use the :doc:`transformation functionality <transforming>` to convert a nested structure into a a simple
    structure ready for use with :meth:`~polymatheia.data.writer.CSVWriter.write`.
