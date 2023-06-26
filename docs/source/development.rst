Development
===========

Please feel free to contribute to this project. The following list describes just the basics to start development.


1.  Clone the project
---------------------

You can clone the current development version from github:

.. code-block:: bash

    $ git clone https://github.com/jokiefer/django-mptt2



2.  Install python dependencies
-------------------------------

Dependencies in this project are organized by seperated requirement files under the ``.requirements`` folder.

To install all dependencies to contribute to this project run the command below:

.. code-block:: bash

    $ pip install -r requirements.txt

.. note::

    Run the above command from the root of the project folder.

3.  Install javascript dependencies
-----------------------------------

The javascript dependencies in this project are organized by the ``package.json`` and ``package-lock.json`` files.

To install all dependencies to contribute to this project run the command below:

.. code-block:: bash

    $ npm install

.. note::

    Run the above command from the root of the project folder.

After that npm will install the ``node_modules`` and move the `sorable lib <https://github.com/SortableJS/Sortable>`_ to the mptt2 static folder.


4.  Running tests
-----------------

As other django based projects we test it with the default django `test command <https://docs.djangoproject.com/en/4.2/topics/testing/overview/#running-tests>`_.

.. code-block:: bash

    $ python manage.py test

.. note::

    Run the above command from the root of the project folder.


5. Build docs
-------------

The documentation are build with `sphinx <https://sphinx-tutorial.readthedocs.io/cheatsheet/#cheat-sheet>`_.

To build the docs local change to the ``docs`` subfolder and run the command below.

.. code-block:: bash

    $ make html

The documentation is present under the subfolder ``build/index.html``

