import unittest

dummy_lambda = lambda: None


def module_invalid_test_function_sample():
    return


def test_invalid_module_sample():
    return


def test_funkyconvention_function_is_valid():
    return


class MyTestClass:
    def foo(self):
        pass

    def test_invalid_method_sample(self):
        pass

    def test_test_funkyconvention_method_is_valid(self):
        pass


class MyUnitTestClass(unittest.TestCase):
    def foo_unittest(self):
        pass

    def test_invalid_unittest_method_sample(self):
        pass

    def test_funkyconvention_unittest_method_is_valid(self):
        pass
