Test Name function validator (Flake8 plugin)
============================================

![example workflow](https://github.com/bagerard/flake8-test-name/actions/workflows/github-actions/badge.svg)



.. image:: http://codecov.io/github/bagerard/flake8-test-name/coverage.svg?branch=master
   :alt: Coverage Status
   :target: http://codecov.io/github/bagerard/flake8-test-name?branch=master

An extension for `Flake8 <https://pypi.python.org/pypi/flake8>`_ to make sure
that test function name follows a given convention


Plugin for Flake8
-----------------

When both Flake8 and ``flake8-test-name`` are installed, the plugin
will show up when displaying the version of ``flake8``::

  $ flake8 --version
  3.6.0 (flake8-test-name: 0.1.0, […]


Parameters
----------

This module can be configured in 2 ways:
--test-func-name-validator-module={path}
--test-func-name-validator-regex={regex_pattern}

E.g usage::

  $ flake8 myproject/tests/sample.py --test-func-name-validator-regex="test_funky_convention_.*" --select=II101

>>/home/.../tests/sample.py:14:1: TN101 test function name does not match the convention (test_invalid_method_sample)


Error codes
-----------

This plugin is using the following error codes:

+---------------------------------------------------------------------------------------------+
| Presence of forbidden imports                                                               |
+-------+-------------------------------------------------------------------------------------+
| TN101 | TN101 test function name does not match the convention (test_invalid_method_sample) |
+-------+-------------------------------------------------------------------------------------+


Operation
---------

The plugin will go through all files, identify the tests directories, and validate method
starting with "test_" against your validator.


Changes
-------

0.1.0 - 2021-03-xx
``````````````````
* Initial release
