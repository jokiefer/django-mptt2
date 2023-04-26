.. _tutorial:


Tutorial
========

In this tutorial you will learn about how to use the `django-mptt2` package which implements `nested sets <https://en.wikipedia.org/wiki/Nested_set_model>`_ for your django models.
This documentation will not provide additional information about what is the best tree implementation for databases. You have to decide what soulution fits the best for your use case.


Set up your Model
-----------------

If you installed `django-mptt2` as described inside the :ref:`install` section, you can extend you existing models by inheritance from ``Node``:

.. code-block:: python

   from django.db import models
   from mptt2.models import Node

   class Genre(Node):
      name = models.CharField(max_length=50, unique=True)


.. note::

   You can also import the ``Node`` model with different naming: ``from mptt2.models import Node as MPTTNode``

All additional fields to housekeeping the nested set tree for the given ``Genre`` model are added.