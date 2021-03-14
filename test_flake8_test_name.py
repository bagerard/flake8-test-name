from __future__ import print_function

import ast
import os
from collections import namedtuple

import mock
import flake8
import pytest
from flake8.options.manager import OptionManager

from flake8_illegal_import import (Flake8Argparse, ImportChecker,
                                   format_code, resolve_path)

curr_dir_path = os.path.dirname(os.path.realpath(__file__))
SAMPLE_FILE_PATH = curr_dir_path + '/tests/files/sample.py'
SAMPLE_FILE_DIR = os.path.dirname(SAMPLE_FILE_PATH)

SysArgs = namedtuple('SysArgs', 'illegal_import_dir illegal_import_packages')


def get_tree(filename):
    with open(filename, 'rb') as f:
        return compile(f.read(), filename, 'exec', ast.PyCF_ONLY_AST, True)


def get_tree_from_str(pycode, filename="test.py"):
    return compile(pycode, filename, 'exec', ast.PyCF_ONLY_AST, True)


class TestModuleUtils:
    def test__resolve_path_absolute(self):
        assert resolve_path('/tmp') == '/tmp'

    def test__resolve_path_relative(self):
        assert resolve_path('./tmp') == os.path.abspath('./tmp')

    def test__resolve_path_expand(self):
        assert resolve_path('~/tmp') == os.path.expanduser('~/tmp')

    def test__format_code(self):
        assert format_code(302) == "II302"


class TestFlake8Optparse():
    def test__add_options(self):
        flake8_opt_mgr = OptionManager(
            prog="flake8",
            version=flake8.__version__,)
        plugin = Flake8Argparse(None, SAMPLE_FILE_PATH)
        plugin.add_options(flake8_opt_mgr)
        assert len(flake8_opt_mgr.options) == 2

    def test__parse_options(self):
        flake8_opt_mgr = OptionManager(
            prog="flake8",
            version=flake8.__version__
        )
        plugin = Flake8Argparse(None, SAMPLE_FILE_PATH)
        args = SysArgs(illegal_import_dir=SAMPLE_FILE_DIR, illegal_import_packages='os,json')
        plugin.parse_options(flake8_opt_mgr, args, extra_args=None)
        assert plugin.illegal_import_dir == args.illegal_import_dir
        assert plugin.illegal_import_packages == ['os', 'json']


class TestImportChecker:
    @pytest.mark.parametrize("code_snippet", [
        "",
        "import os\n",
        "import os as forbidden\n",
        "import os # forbidden\n",
    ])
    def test__get_illegal_imports__no_match(self, code_snippet):
        tree = get_tree_from_str(code_snippet)

        banned_packages = ['forbidden']
        illegals_imports = ImportChecker.get_illegal_imports(tree, banned_packages)
        errors = {node.lineno: pkg_name for node, pkg_name in illegals_imports}

        assert errors == {}

    @pytest.mark.parametrize("code_snippet,expected_errors", [
        (
                "import forbidden\n",
                {1: 'forbidden'}
        ),
        (
                "import forbidden\nimport forbidden\n",
                {1: 'forbidden',
                 2: 'forbidden'}
        ),
        (
                "import forbidden as forbidden\n",
                {1: 'forbidden'}
        ),
        (
                "import forbidden as os\n",
                {1: 'forbidden'}
        ),
        (
                "import os;\nimport json;import forbidden\n",
                {2: 'forbidden'}
        ),
    ])
    def test__get_illegal_imports__import_simple_case(self, code_snippet, expected_errors):
        tree = get_tree_from_str(code_snippet)

        banned_packages = ['forbidden']
        illegals_imports = ImportChecker.get_illegal_imports(tree, banned_packages)
        errors = {node.lineno: pkg_name for node, pkg_name in illegals_imports}

        assert errors == expected_errors

    @pytest.mark.parametrize("code_snippet,expected_errors", [
        (
                "from forbidden import really_forbidden\n",
                {1: 'forbidden'}
        ),
        (
                "from forbidden import really_forbidden as os\n",
                {1: 'forbidden'}
        ),
        (
                "import json, os\nfrom forbidden import really_forbidden",
                {2: 'forbidden'}
        ),
    ])
    def test__get_illegal_imports__importfrom_simple_case(self, code_snippet, expected_errors):
        tree = get_tree_from_str(code_snippet)

        banned_packages = ['forbidden']
        illegals_imports = ImportChecker.get_illegal_imports(tree, banned_packages)
        errors = {node.lineno: pkg_name for node, pkg_name in illegals_imports}

        assert errors == expected_errors

    def test__get_illegal_imports__coma_separated(self):
        code = "import json, forbidden"
        tree = get_tree_from_str(code)

        banned_packages = ['forbidden']
        illegals_imports = ImportChecker.get_illegal_imports(tree, banned_packages)
        errors = {node.lineno: pkg_name for node, pkg_name in illegals_imports}

        assert errors == {1: 'forbidden'}

    def test__run(self):
        tree = get_tree(SAMPLE_FILE_PATH)
        args = SysArgs(illegal_import_dir='./', illegal_import_packages='os,json,abc')

        checker = ImportChecker(tree, SAMPLE_FILE_PATH)
        checker.parse_options(None, args, None)

        expected = [
            (1, 0, 'II101 importing this package is forbidden in this directory (os)', ImportChecker),
            (4, 0, 'II101 importing this package is forbidden in this directory (json)', ImportChecker),
            (5, 0, 'II101 importing this package is forbidden in this directory (abc)', ImportChecker),
            (7, 0, 'II101 importing this package is forbidden in this directory (os)', ImportChecker),
            (8, 0, 'II101 importing this package is forbidden in this directory (os)', ImportChecker),
            (14, 4, 'II101 importing this package is forbidden in this directory (os)', ImportChecker),
            (15, 4, 'II101 importing this package is forbidden in this directory (json)', ImportChecker),
        ]
        res = list(checker.run())
        assert res == expected

    @mock.patch('flake8_illegal_import.ImportChecker.report')
    def test__run__no_package_name(self, reporter):
        tree = get_tree(SAMPLE_FILE_PATH)
        args = SysArgs(illegal_import_dir='/tmp', illegal_import_packages='')

        checker = ImportChecker(tree, SAMPLE_FILE_PATH)
        checker.parse_options(None, args, None)
        resp = list(checker.run())
        assert len(resp) == 0
        reporter.assert_called_once_with('No illegal import package set - skip checks')

    @mock.patch('flake8_illegal_import.ImportChecker.report')
    def test__run__dir_not_exist(self, reporter):
        tree = get_tree(SAMPLE_FILE_PATH)
        args = SysArgs(illegal_import_dir='./non-exist', illegal_import_packages='os')

        checker = ImportChecker(tree, SAMPLE_FILE_PATH)
        checker.parse_options(None, args, None)
        resp = list(checker.run())
        assert len(resp) == 0
        reporter.assert_called_once()
        assert 'WARNING: Directory configured does not exist:' in reporter.call_args_list[0][0][0]
