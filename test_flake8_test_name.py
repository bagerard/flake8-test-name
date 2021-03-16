import ast
import os
from collections import namedtuple

import flake8
import mock
import pytest
from flake8.options.manager import OptionManager
from flake8_test_name import (
    Flake8Argparse,
    MyFlake8Plugin,
    format_code,
    resolve_path,
    MyVisitor,
    check_test_func_name,
)

curr_dir_path = os.path.dirname(os.path.realpath(__file__))
SAMPLE_FILE_PATH = curr_dir_path + "/tests/files/test_sample.py"
SAMPLE_FILE_DIR = os.path.dirname(SAMPLE_FILE_PATH)

SysArgs = namedtuple("SysArgs", "illegal_import_dir")


def get_tree(filename):
    with open(filename, "rb") as f:
        return compile(f.read(), filename, "exec", ast.PyCF_ONLY_AST, True)


def get_tree_from_str(pycode, filename="test.py"):
    return compile(pycode, filename, "exec", ast.PyCF_ONLY_AST, True)


class TestModuleUtils:
    def test__resolve_path_absolute(self):
        assert resolve_path("/tmp") == "/tmp"

    def test__resolve_path_relative(self):
        assert resolve_path("./tmp") == os.path.abspath("./tmp")

    def test__resolve_path_expand(self):
        assert resolve_path("~/tmp") == os.path.expanduser("~/tmp")

    def test__format_code(self):
        assert format_code(302) == "TN302"

    @pytest.mark.parametrize(
        "func_name",
        [
            "test_method__when__then",
            "test__protectedmethod__when__then",
            "test___privatemethod__when__then",
            "test_method__when_blabla__then_blabla",
            "test__method__when_blabla__then_blabla",
        ],
    )
    def test_check_test_func_name__valid_test_name__return_true(self, func_name):
        assert check_test_func_name(func_name) is True

    @pytest.mark.parametrize(
        "func_name",
        [
            "garbage",
            "garbage_method",
            "test_myfunc_shouldpass",
            "test__myfunc__shouldpass_when_this",
            "test___myfunc__shouldpass_when_that__",
        ],
    )
    def test_check_test_func_name__invalid_test_name__return_false(self, func_name):
        assert check_test_func_name(func_name) is False


class TestFlake8Optparse:
    def test__add_options(self):
        flake8_opt_mgr = OptionManager(prog="flake8", version=flake8.__version__,)
        plugin = Flake8Argparse(None, SAMPLE_FILE_PATH)
        plugin.add_options(flake8_opt_mgr)
        assert len(flake8_opt_mgr.options) == 2

    def test__parse_options(self):
        flake8_opt_mgr = OptionManager(prog="flake8", version=flake8.__version__)
        plugin = Flake8Argparse(None, SAMPLE_FILE_PATH)
        args = SysArgs(illegal_import_dir=SAMPLE_FILE_DIR)
        plugin.parse_options(flake8_opt_mgr, args, extra_args=None)
        assert plugin.illegal_import_dir == args.illegal_import_dir


class TestMyVisitor:
    def test_valid_func_name(self):
        code_snippet = "import garbage\n\ndef test__im_a_valid_method__when_this__then_that():\n    pass"
        tree = get_tree_from_str(code_snippet)
        visitor = MyVisitor()
        visitor.visit(tree)

        assert not visitor.stats

    def test_invalid_func_name(self):
        code_snippet = "import garbage\n\ndef test_im_not_a_valid_method():\n    pass"
        tree = get_tree_from_str(code_snippet)
        visitor = MyVisitor()
        visitor.visit(tree)

        assert len(visitor.stats) == 1
        node, func_name = visitor.stats[0]
        assert node.lineno == 3
        assert func_name == "test_im_not_a_valid_method"


class TestMyFlake8Plugin:
    def test__get_invalid_test_methods__no_match(self):
        code_snippet = "import garbage\n\ndef test__im_a_valid_method__when_this__then_that():\n    pass"
        tree = get_tree_from_str(code_snippet)

        invalid_methods = list(MyFlake8Plugin.get_invalid_test_methods(tree))
        assert not invalid_methods

    def test__get_invalid_test_methods__match(self):
        code_snippet = "import garbage\n\ndef test_im_an_valid_method():\n    pass"
        tree = get_tree_from_str(code_snippet)

        invalid_methods = list(MyFlake8Plugin.get_invalid_test_methods(tree))
        assert invalid_methods

    def test__run(self):
        tree = get_tree(SAMPLE_FILE_PATH)
        args = SysArgs(illegal_import_dir="./")

        checker = MyFlake8Plugin(tree, SAMPLE_FILE_PATH)
        checker.parse_options(None, args, None)

        expected = [
            (
                10,
                0,
                "TN101 bad test function name (test_module_invalid_function_sample)",
                MyFlake8Plugin,
            ),
            (22, 4, "TN101 bad test function name (test_im_invalid)", MyFlake8Plugin),
            (33, 4, "TN101 bad test function name (test_im_invalid)", MyFlake8Plugin),
        ]
        res = list(checker.run())
        assert res == expected

    # @mock.patch("flake8_illegal_import.MyFlake8Plugin.report")
    # def test__run__no_package_name(self, reporter):
    #     tree = get_tree(SAMPLE_FILE_PATH)
    #     args = SysArgs(illegal_import_dir="/tmp")
    #
    #     checker = ImportChecker(tree, SAMPLE_FILE_PATH)
    #     checker.parse_options(None, args, None)
    #     resp = list(checker.run())
    #     assert len(resp) == 0
    #     reporter.assert_called_once_with("No illegal import package set - skip checks")
    #
    # @mock.patch("flake8_illegal_import.MyFlake8Plugin.report")
    # def test__run__dir_not_exist(self, reporter):
    #     tree = get_tree(SAMPLE_FILE_PATH)
    #     args = SysArgs(illegal_import_dir="./non-exist")
    #
    #     checker = ImportChecker(tree, SAMPLE_FILE_PATH)
    #     checker.parse_options(None, args, None)
    #     resp = list(checker.run())
    #     assert len(resp) == 0
    #     reporter.assert_called_once()
    #     assert (
    #         "WARNING: Directory configured does not exist:"
    #         in reporter.call_args_list[0][0][0]
    #     )
