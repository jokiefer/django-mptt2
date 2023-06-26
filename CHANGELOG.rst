Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.


[0.2.0] - 2023-06-26
--------------------

Added
~~~~~

* implement a mptt and draggable django admin site. It uses `SortableJS <https://github.com/SortableJS/Sortable>`_ to recognize drag events.
* implement 


Changed
~~~~~~~

* removes the `queryset.delete()` function from tree managers. In all mptt based admin sites the global possibility to delete objects is replaced by using the delete function on the nodes. Cause of the parent child relation and there cascading delete behaviour all descendants of a node are deleted as well. 


Fixed
~~~~~

* ancestors right value was not updated correctly while running `insert_at` method for last and first child. Fixed by adding the correct `AncestorQuery` to `_calculate_filter_for_insert` function.
* implement a unique checkconstraint name to fix error: 'rgt_gt_lft' is not unique among models. 
* implement a unique related_name to fix error: Add or change a related_name argument to the definition for mptt_tree

[0.1.1] - 2023-06-08
--------------------

Fixed
~~~~~

* manager access for instance subfunctions: `get_children`, `get_descendants`, `get_ancestors`, `get_family`, `get_siblings`, `move_to`, `insert_at`

[0.1.0] - 2023-04-29
--------------------

Added
~~~~~

* implement an abstract django model `Node` to provide `insert_at`, `move_to` and some basic tree functionality onside the model instance.
* implement a default django manager `TreeManager` to provide tree functionality to keep the nested sets up to date on moving or inserting nodes.
* implement some basic Q objects to reuse the queries easier. By using the inherited Q objects, it is not possible to use django <4.2, cause the negated object is a shallow copy. All versions bellow will construct the object new without passing the original arguments. So it will raise a TypeError. See `code <https://github.com/django/django/commit/845667f2d1eb7063c568764a01fc9ee633ec5817#diff-fd68084e8b9b4f7bfd0df330a70f792633b28109d07b3df6609f2fb019d0f0f7L82>`_ for more information.
       
            

[unreleased]: https://github.com/jokiefer/django-mptt2/compare/v0.1.0...HEAD
[0.0.1]: https://github.com/jokiefer/django-mptt2/releases/tag/v0.1.0
