.. _install:


Installation
============

Adding **django-mptt2** to your project is simple as installing other django apps.


1. Install python package
-------------------------

.. code-block:: bash

   $ pip install django-mptt2


2. Provide mptt2 to your django project
---------------------------------------

Add ``mptt2`` to the `INSTALLED_APPS <https://docs.djangoproject.com/en/4.2/ref/settings/#installed-apps>`_ setting of your settings.py:


.. code-block:: python

   INSTALLED_APPS = [
      # other apps
      "mptt2"
   ]


