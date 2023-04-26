Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

[Unreleased]
------------

Added
~~~~~

* implement an abstract django model `Node` to provide some tree functionality onside the model instance.
* implement a default django manager `TreeManager` to provide tree functionality to keep the nested sets up to date on moving or inserting nodes.
* implement some tree bases query objects to reuse the queries easier.

[unreleased]: https://github.com/jokiefer/django-mptt2/compare/v0.0.1...HEAD
[0.0.1]: https://github.com/jokiefer/django-mptt2/releases/tag/v0.0.1