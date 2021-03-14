"""Extension for flake8 to reject tests that don't follow a certain convention"""
import ast
import os.path

__version__ = '0.1.0'


CODE_PREFIX = "TN"


def format_code(code):
    return '{}{}'.format(CODE_PREFIX, code)


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
            "--illegal-import-dir", type="str", default="./",
            parse_from_config=True,
            help="Directory to consider when looking for illegal import",
        )

        option_manager.add_option(
            "--illegal-import-packages", type="str", parse_from_config=True,
            help="Set packages that are not allowed in directory",
        )

    @classmethod
    def parse_options(cls, option_manager, options, extra_args):
        cls.illegal_import_dir = resolve_path(options.illegal_import_dir)
        illegal_import_packages = options.illegal_import_packages or ""
        cls.illegal_import_packages = [pkg for pkg in illegal_import_packages.split(',') if pkg]    # Allows for "package," as option


class MyVisitor(ast.NodeVisitor):

    def __init__(self, *args, **kwargs):
        super(ast.NodeVisitor, self).__init__(*args, **kwargs)
        self.stats = []

    @staticmethod
    def is_valid_name(func_name):
        return func_name.startswith("test__")

    def visit_FunctionDef(self, node):
        if not self.is_valid_name(node.name):
            self.stats.append((node, node.name))


class ImportChecker(Flake8Argparse):

    version = __version__
    name = 'illegal-import'

    ERRORS = {
        101: 'bad test function name ({func_name})',
    }

    def _generate_error(self, node, code, func_name):
        msg = '{0} {1}'.format(format_code(code), self.ERRORS[code])
        msg = msg.format(func_name=func_name)
        return node.lineno, node.col_offset, msg, type(self)

    @staticmethod
    def get_invalid_test_methods(tree):
        visitor = MyVisitor()
        visitor.visit(tree)

        for node, func_name in visitor.stats:
            yield node, func_name

    def report(self, msg):
        print(msg)

    @staticmethod
    def is_in_test_dir(file_path):
        return "tests/" in file_path

    def run(self):
        if not self.is_in_test_dir(self.filename):
            print(f'File not in the tests dir {self.filename}')
            # File not concerned by the restriction
            return

        banned_packages = set(self.illegal_import_packages)

        for node, func_name in ImportChecker.get_invalid_test_methods(self.tree):
            yield self._generate_error(node, 101, func_name=func_name)
