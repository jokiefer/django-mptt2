django-mptt2
============
Based on the idea of the unmaintained `django-mptt <https://github.com/django-mptt/django-mptt>`_ package i implemented this new code base to replace it.

Cause no other package fits all of my use cases, which are primary in fast reading tree's from the database, i started working on this project.

There is an alternative to this package, called `django-treebeard <https://pypi.org/project/django-treebeard/>`_, which implements nested sets as well, but without a parent foreignkey.


Quick-Start
-----------

Install it as any other django app to your project:

.. code-block:: bash

    $ pip install django-mptt2

Add `django-mptt2` to `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = [
        # other apps
        "mptt2"
    ]

Inheritance from the abstract `mptt2.models.Node` Model:

.. code-block:: python

    from django.db import models
    from mptt2.models import 
    
    class Genre(Node)
        name = models.CharField(max_length=50, unique=True)


Adding nodes:

.. code-block:: python

    from project.models import Genre

    rock = Genre(name="Rock")
    rock.insert_at() # it will become the root node without target parameter

    metal = Genre(name="Metal")
    metal.insert_at(target=rock) # it will become the last child from rock 

    alternative = Genre(name="Alternative")
    alternative.insert_at(target=rock) # it will become the last child from rock, the right sibling of metal


For full usage description, please read the tutorial section.