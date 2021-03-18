Test Name function validator (Flake8 plugin)
============================================

![example workflow](https://github.com/bagerard/flake8-test-name/actions/workflows/github-actions/badge.svg)



.. image:: http://codecov.io/github/bagerard/flake8-illegal-import/coverage.svg?branch=master
   :alt: Coverage Status
   :target: http://codecov.io/github/bagerard/flake8-illegal-import?branch=master

An extension for `Flake8 <https://pypi.python.org/pypi/flake8>`_ to make sure
that certain packages aren't imported in a directory


Plugin for Flake8
-----------------

When both Flake8 and ``flake8-illegal-import`` are installed, the plugin
is available in ``flake8``::

  $ flake8 --version
  3.6.0 (flake8-illegal-import: 0.1.0, […]


Parameters
----------

This module requires 2 parameters:
--illegal-import-dir={path}
--illegal-import-packages={pkg1},{pkg2}

E.g usage::

  $ flake8 ./sample.py --illegal-import-dir=./ --illegal-import-packages=os --select=II101

>>/home/.../test/sample.py:14:1: II101 importing this package is forbidden in this directory (os)


Error codes
-----------

This plugin is using the following error codes:

+---------------------------------------------------------------------+
| Presence of forbidden imports                                       |
+-------+-------------------------------------------------------------+
| II101 | importing this package is forbidden in this directory {pkg} |
+-------+-------------------------------------------------------------+


Operation
---------

The plugin will go through all imports and find out if forbidden packages
are imported in the given directory


Changes
-------

0.1.0 - 2019-01-XX
``````````````````
* Initial release
