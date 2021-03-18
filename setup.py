import codecs

from setuptools import setup

plugin_file = "flake8_test_name.py"


def get_version():
    with open(plugin_file) as f:
        for line in f:
            if line.startswith("__version__"):
                return eval(line.split("=")[-1])


def get_prefix():
    with open(plugin_file) as f:
        for line in f:
            if line.startswith("CODE_PREFIX"):
                return eval(line.split("=")[-1])


def get_long_description():
    with codecs.open("README.rst", "r", "utf-8") as f:
        return f.read()


INSTALL_REQUIRES = ["flake8"]
TESTS_REQUIRES = ["pytest", "mock", "pytest-cov"]

setup(
    name="flake8-test-name",
    version=get_version(),
    description="Invalid test name checker, plugin for flake8",
    long_description=get_long_description(),
    long_description_content_type="text/x-rst",
    keywords="flake8 test name convention",
    maintainer="Bastien Gerard",
    maintainer_email="bast.gerard@gmail.com",
    url="https://github.com/bagerard/flake8-test-name",
    license="MIT License",
    py_modules=["flake8_test_name"],
    zip_safe=False,
    entry_points={
        "flake8.extension": [
            "{prefix} = flake8_test_name:MyFlake8Plugin".format(prefix=get_prefix()),
        ],
    },
    install_requires=INSTALL_REQUIRES,
    tests_require=TESTS_REQUIRES,
    setup_requires=["pytest-runner"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
    ],
)
