"""Extension for flake8 to reject tests that don't follow a certain convention"""
import ast
import os.path
import importlib.util
import re

# metadata
__version__ = "0.1.0"
CODE_PREFIX = "TN"


TEST_FUNC_PREFIX = "test_"
TEST_FUNC_NAME_VALIDATOR_METHOD = "test_function_name_validator"


TEST_FUNC_NAME_VALIDATOR_MODULE = os.environ.get("TEST_FUNC_NAME_VALIDATOR_MODULE")


def get_test_func_name_validator():
    def _validator(s):
        raise Exception("NO VALIDATOR")

    if TEST_FUNC_NAME_VALIDATOR_MODULE:
        validator = _get_validator_from_module(TEST_FUNC_NAME_VALIDATOR_MODULE)
    else:
        validator = _validator

    return validator


def _get_validator_from_module(file_path: str):
    try:
        spec = importlib.util.spec_from_file_location(
            "customer_test_func_name_module", file_path
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as e:
        raise Exception(f"Could not load python module {file_path}")
    else:
        try:
            return getattr(module, TEST_FUNC_NAME_VALIDATOR_METHOD)
        except AttributeError:
            raise Exception(
                f"Could not find function ´{TEST_FUNC_NAME_VALIDATOR_METHOD}´ in module {module.__file__}"
            )


def _get_validator_from_regex(regex):
    pattern = re.compile(regex)

    def regex_validator(func_name):
        return pattern.fullmatch(func_name) is not None

    return regex_validator


def format_code(code):
    return f"{CODE_PREFIX}{code}"


def resolve_path(dir_path):
    dir_path = os.path.expanduser(dir_path)
    return os.path.abspath(dir_path)


class Flake8Argparse(object):
    def __init__(self, tree, filename):
        self.tree = tree
        self.filename = resolve_path(filename)

    @classmethod
    def add_options(cls, option_manager):
        option_manager.add_option(
            "--test-func-name-validator-module",
            type="str",
            default=None,
            parse_from_config=True,
            help=f"Path to a python file containing a validator function ´{TEST_FUNC_NAME_VALIDATOR_MODULE}´",
        )
        option_manager.add_option(
            "--test-func-name-validator-regex",
            type="str",
            default=None,
            parse_from_config=True,
            help="Regex to be used as validator",
        )

    @classmethod
    def parse_options(cls, option_manager, options, extra_args):
        cls.test_func_name_validator_module = None
        cls.test_func_name_validator_regex = options.test_func_name_validator_regex

        if options.test_func_name_validator_module:
            cls.test_func_name_validator_module = resolve_path(
                options.test_func_name_validator_module
            )


class MyVisitor(ast.NodeVisitor):
    def __init__(self, validator):
        self.validator = validator
        self.stats = []

    @staticmethod
    def is_test_function(func_name):
        return func_name.startswith(TEST_FUNC_PREFIX)

    def visit_FunctionDef(self, node):
        if not self.is_test_function(node.name):
            return

        if not self.validator(node.name):
            self.stats.append((node, node.name))


class MyFlake8Plugin(Flake8Argparse):

    version = __version__
    name = "illegal-import"

    ERRORS = {
        101: "bad test function name ({func_name})",
    }

    def _generate_error(self, node, code, func_name):
        msg = "{0} {1}".format(format_code(code), self.ERRORS[code])
        msg = msg.format(func_name=func_name)
        return node.lineno, node.col_offset, msg, type(self)

    @staticmethod
    def get_invalid_test_methods(tree, validator):
        visitor = MyVisitor(validator)
        visitor.visit(tree)

        for node, func_name in visitor.stats:
            yield node, func_name

    def report(self, msg):
        print(msg)

    @staticmethod
    def is_in_test_dir(file_path):
        return "tests/" in file_path

    def get_test_func_name_validator(self):
        if self.test_func_name_validator_module:
            return _get_validator_from_module(self.test_func_name_validator_module)
        elif self.test_func_name_validator_regex:
            return _get_validator_from_regex(self.test_func_name_validator_regex)
        else:
            raise Exception("No validator defined")

    def run(self):
        if not self.is_in_test_dir(self.filename):
            return

        test_func_name_validator = self.get_test_func_name_validator()

        for node, func_name in MyFlake8Plugin.get_invalid_test_methods(
            self.tree, validator=test_func_name_validator
        ):
            yield self._generate_error(node, 101, func_name=func_name)
