===================
libcflib Change Log
===================

.. current developments

v0.0.7
====================

**Fixed:**

* Fixes to the name argument of the Artifact model, so that it respects a
  canonical form better.

**Authors:**

* Anthony Scopatz



v0.0.6
====================

**Added:**

* ``rest.RequestHandlers`` may now provide a ``defaults`` dict.
* ``rest.RequestHandlers`` may now provide a ``converters`` dict.
* The REST service will now update the graph periodically.

**Changed:**

* The ``Artifact`` model now includes a ``spec`` field that contains
  information about the artifact itself.

**Fixed:**

* Fixes to ``harvest_pkgs`` utility.

**Authors:**

* Anthony Scopatz
* Christopher J. Wright



v0.0.5
====================

**Added:**

* New ``libcflib.models.artifact_key()`` function for sorting artifacts.
* New ``libcflib.models.Package.latest_artifact()`` method for finding
  the most recent artifact for a package.

**Changed:**

* ``ChannelGraph`` now correctly loads artifact names.

**Fixed:**

* Fixed some Model attribute getting/setting for nested models.



v0.0.4
====================

**Added:**

* Implemented db.search().

* Schemas contain key telling whoosh if a field should be stored.

* Preloader indexes artifacts.

* Script to index artifacts not currently in index.
* New REST API for searching the database.

**Changed:**

* When creating a whoosh index, an indexname is supplied so multiple indexes can exist in the same directory.

* When indexing document, ignore fields not present in schema rather than raise an error.
* Pulling updates to libcfgraph is now more robust, and should not require
  human intervention ever.
* New simple search for searching artifacts uses ``grep``, ``head``, and ``tail``.

**Removed:**

* Removed Whoosh, as it is deprecated, so that we may start fresh!



v0.0.3
====================

**Added:**

* Updating versions will now push up the new app to the servers




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




