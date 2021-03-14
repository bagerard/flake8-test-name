import unittest


def module_invalid_test_function_sample():
    return


def test_module_invalid_function_sample():
    return


def test__module_valid_function_sample():
    return


class MyTestClass:
    def im_invalid(self):
        pass

    def test_im_invalid(self):
        pass

    def test__im_valid(self):
        pass


class MyTestClass(unittest.TestCase):
    def im_invalid(self):
        pass

    def test_im_invalid(self):
        pass

    def test__im_valid(self):
        pass