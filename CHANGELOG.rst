===================
libcflib Change Log
===================

.. current developments

v0.0.2
====================

**Fixed:**

* Fixed version number bumping in setup.py.




v0.0.1
====================

**Added:**

* Pandas is now an optional dependency, for faster JSON load times.
* New ``ChannelGraph`` model for representing the graph for a given channel.
* Database ``DB`` object has new ``channel_graphs`` attribute, which is a
  collection of all channel graphs.
* Added dependency on ``lazyasd``.
* Packages now have an ``arches`` attribute, which is a set of all of the
  architechures that package has been built for.


**Changed:**

* Packages now know how to load all of their data and do so lazily.
* ``model`` module renamed to ``models``.


**Fixed:**

* Added a closing paren to ``Package`` repr string.
* Fixed failing request handler tests




