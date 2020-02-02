import sys
import setuptools
from os import path
from setuptools.command.test import test as TestCommand

import object_pool

here = path.abspath(path.dirname(__file__))


class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        errcode = tox.cmdline(self.test_args)
        sys.exit(errcode)


with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name="py-object-pool",
    version=object_pool.__version__,
    author="Durai Pandian",
    author_email="dduraipandian@gmail.com",
    description="Object pool creation library",
    long_description=open('README.rst').read(),
    url="https://github.com/dduraipandian/object_pool",
    packages=setuptools.find_packages(exclude=("tests",)),
    package_dir={'object_pool': 'object_pool'},
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
    ],
    keywords='Object pool creation library',
    python_requires='>=3.6',
    tests_require=['tox'],
    cmdclass={'test': Tox},
    zip_safe=False,
    include_package_data=True,
)
