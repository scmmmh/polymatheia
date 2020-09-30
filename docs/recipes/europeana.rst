Loading Data from Europeana
===========================

`Europeana`_ is the European aggregator for cultural heritage data and comes with its own metadata schema and a custom
API (application programming interface) for accessing the data. In order to use the API you need to have an API Key,
which you need to apply for `here <https://pro.europeana.eu/page/get-api>`_ before we continue.

.. _`Europeana`: https://www.europeana.eu

Basic queries
-------------

To query Europeana, use the :class:`~polymatheia.data.reader.EuropeanaSearchReader`. You need to provide your api key
and the query you want to run:

.. sourcecode:: python

    from polymatheia.data.reader import EuropeanaSearchReader

    EUROPEANA_API_KEY = 'Put your key here'
    reader = EuropeanaSearchReader(EUROPEANA_API_KEY, 'Python')
    for record in reader:
        print(record)

Complex queries
---------------

Europeana provides full `documentation of the Europeana query language <https://pro.europeana.eu/page/search#basic-search>`_.
Here are just some examples of more complex queries. For example you can use double quotes to ensure the results
contain the query text as-is:

.. sourcecode:: python

    from polymatheia.data.reader import EuropeanaSearchReader

    EUROPEANA_API_KEY = 'Put your key here'
    reader = EuropeanaSearchReader(EUROPEANA_API_KEY, '"Karl Gutzkow"')
    for record in reader:
        print(record.title)

You can also use the boolean operators AND and OR:

.. sourcecode:: python

    from polymatheia.data.reader import EuropeanaSearchReader

    EUROPEANA_API_KEY = 'Put your key here'
    reader = EuropeanaSearchReader(EUROPEANA_API_KEY, 'Karl AND Gutzkow')
    for record in reader:
        print(record.title)

By default the search will run across all fields. To search only within a single field, you can specify the field in
the search query:

.. sourcecode:: python

    from polymatheia.data.reader import EuropeanaSearchReader

    EUROPEANA_API_KEY = 'Put your key here'
    reader = EuropeanaSearchReader(EUROPEANA_API_KEY, 'title:Karl AND title:Gutzkow')
    for record in reader:
        print(record.title)

Result profiles
---------------

The Europeana Search API provides different `levels of detail <https://pro.europeana.eu/page/search#profiles>`_ in the
results. By default it provides the "standard" result profile and for determining what query to use to find the
data-set one is interested in, it is ideal. However, when downloading the data for further processing, the "rich"
profile is generally better, as it provides the maximum level of detail:

.. sourcecode:: python

    from polymatheia.data.reader import EuropeanaSearchReader

    EUROPEANA_API_KEY = 'Put your key here'
    reader = EuropeanaSearchReader(EUROPEANA_API_KEY, 'title:Karl AND title:Gutzkow', profile='rich')
    for record in reader:
        print(record)

Reusability
-----------

All records in the Europeana archive are provided with rights information, specifying what
`use is allowed <https://pro.europeana.eu/page/search#reusability>`_. To restrict the results to, for example, those
where any kind of re-use is possible, use the :code:`reusability` parameter:

.. sourcecode:: python

    from polymatheia.data.reader import EuropeanaSearchReader

    EUROPEANA_API_KEY = 'Put your key here'
    reader = EuropeanaSearchReader(EUROPEANA_API_KEY, 'title:Karl AND title:Gutzkow', reusability='open')
    for record in reader:
        print(record)

The reusability values group together different specific licenses. To filter by a specific license, simply use that
license in the query:

.. sourcecode:: python

    from polymatheia.data.reader import EuropeanaSearchReader

    EUROPEANA_API_KEY = 'Put your key here'
    reader = EuropeanaSearchReader(EUROPEANA_API_KEY, 'title:Karl AND title:Gutzkow AND RIGHTS:"http://creativecommons.org/publicdomain/mark/1.0/"')
    for record in reader:
        print(record)
