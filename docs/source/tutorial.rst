.. _tutorial:


Tutorial
========

In this tutorial you will learn about how to use the `django-mptt2` package which implements `nested sets <https://en.wikipedia.org/wiki/Nested_set_model>`_ for your django models.
This documentation will not provide additional information about what is the best tree implementation for databases. You have to decide what soulution fits the best for your use case.


Set up your Model
-----------------

If you installed `django-mptt2` as described inside the :ref:`install` section, you can extend you existing models by inheritance from  :class:`Node <mptt2.models.Node>`:

.. code-block:: python

   from django.db import models
   from mptt2.models import Node

   class Genre(Node):
      name = models.CharField(max_length=50, unique=True)


.. note::

   You can also import the  :class:`Node <mptt2.models.Node>` model with different naming: ``from mptt2.models import Node as MPTTNode``

All additional fields to housekeeping the nested set tree for the given ``Genre`` model are added if you `migrate <https://docs.djangoproject.com/en/4.2/topics/migrations/#workflow>`_ the changes:

.. code-block:: bash

   $ python manage.py makemigrations
   $ python manage.py migrate

.. note::

   See :class:`Node <mptt2.models.Node>` model for more details about the fields which were added.


Create a new tree
-----------------

To create a new tree you just need to construct a node which shall be the root node:

.. code-block:: python

   from project.models import Genre

   rock = Genre(name="Rock")
   rock.insert_at() # it will become the root node without target parameter

   metal = Genre(name="Metal")
   metal.insert_at(target=rock) # it will become the last child from rock

   alternative = Genre(name="Alternative")
   alternative.insert_at(target=rock) # it will become the last child from rock, the right sibling of metal


.. note:: 

   :class:`Tree <mptt2.models.Tree>` objects are created if no target is passed.


Moving nodes
------------

You can move nodes by using the ``move_to`` function on a node instance:


.. code-block:: python
   
   from mptt2.enums import Position

   alternative.move_to(target=metal, position=Position.FIRST_CHILD)