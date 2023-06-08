Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

[Unreleased] - 202x-xx-xx
-------------------------

Fixed
~~~~~
* manager access for instance subfunctions: `get_children`, `get_descendants`, `get_ancestors`, `get_family`, get_siblings`, `move_to`, `insert_at`

[0.1.0] - 2023-04-29
--------------------

Added
~~~~~

* implement an abstract django model `Node` to provide `insert_at`, `move_to` and some basic tree functionality onside the model instance.
* implement a default django manager `TreeManager` to provide tree functionality to keep the nested sets up to date on moving or inserting nodes.
* implement some basic Q objects to reuse the queries easier. By using the inherited Q objects, it is not possible to use django <4.2, cause the negated object is a shallow copy. All versions bellow will construct the object new without passing the original arguments. So it will raise a TypeError. See `code <https://github.com/django/django/commit/845667f2d1eb7063c568764a01fc9ee633ec5817#diff-fd68084e8b9b4f7bfd0df330a70f792633b28109d07b3df6609f2fb019d0f0f7L82>`_ for more information.
       
            

[unreleased]: https://github.com/jokiefer/django-mptt2/compare/v0.1.0...HEAD
[0.0.1]: https://github.com/jokiefer/django-mptt2/releases/tag/v0.1.0
