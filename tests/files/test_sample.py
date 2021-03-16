import unittest

dummy_lambda = lambda: None


def module_invalid_test_function_sample():
    return


def test_module_invalid_function_sample():
    return


def test__module_valid_function__when_this__then_that():
    return


class MyTestClass:
    def im_invalid(self):
        pass

    def test_im_invalid(self):
        pass

    def test__im_valid__when_this__then_that(self):
        pass


class MyUnitTestClass(unittest.TestCase):
    def im_invalid(self):
        pass

    def test_im_invalid(self):
        pass

    def test__im_valid__when_this__then_that(self):
        pass
