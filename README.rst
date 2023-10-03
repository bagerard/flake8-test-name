Test Name function validator (Flake8 plugin)
============================================

.. image:: https://github.com/bagerard/flake8-test-name/actions/workflows/github-actions.yml/badge.svg
   :alt: Build status
   :target: https://github.com/bagerard/flake8-test-name/actions/workflows/github-actions.yml

.. image:: https://coveralls.io/repos/github/bagerard/flake8-test-name/badge.svg
   :alt: Coverage Status
   :target: https://coveralls.io/github/bagerard/flake8-test-name

An extension for `Flake8 <https://github.com/PyCQA/flake8>`_ to make sure
that test function name follows a given convention


Plugin for Flake8
-----------------

When both Flake8 and ``flake8-test-name`` are installed, the plugin
will show up when displaying the version of ``flake8``:

.. code:: bash

  $ flake8 --version
  3.6.0 (flake8-test-name: 0.1.2, […]


Operation
---------

The hook assumes that your:

- test files are matching :code:`test_.*.py`
- test functions are starting with :code:`test_`

Any function matching these 2 conditions will be validated against your custom validator

Parameters
----------

This module can be configured in 2 ways.
First option is a regex using :code:`--test-func-name-validator-regex`:

.. code:: bash

  $ flake8 myproject/tests/sample.py --test-func-name-validator-regex="test_funky_convention_.*" --select=TN101

  >> myproject/tests/sample.py:14:1: TN101 test function name does not match the convention (test_invalid_method_sample)



Second option is with a python module containing a method named :code:`test_function_name_validator`.
Assuming you have a funky_validator.py file with the following content:

.. code:: python

    def test_function_name_validator(func_name: str):
        return func_name.startswith("test_funkyconvention")

You can then configure it using :code:`--test-func-name-validator-module`:

.. code:: bash

    $ flake8 myproject/tests/sample.py --test-func-name-validator-module=./funky_validator.py --select=TN101

    >> myproject/tests/sample.py:14:1: TN101 test function name does not match the convention (test_invalid_method_sample)

Error codes
-----------

This plugin is using the following error codes:

+----------------------------------------------------------------+
| Code  | Error                                                  |
+-------+--------------------------------------------------------+
| TN101 | TN101 test function name does not match the convention |
+-------+--------------------------------------------------------+


Changes
-------

0.1.6 - 2023-10-03
``````````````````
* fix in options parser for flake8 > 6.0

0.1.5 - 2021-03-21
``````````````````
* minor refactoring and doc improvement

0.1.1 - 2021-03-19
``````````````````
* Initial release
