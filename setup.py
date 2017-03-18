#!/usr/bin/env python3

import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass into py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest

        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


requires = ['requests>=2.12.5', 'm3u8>=0.3.1', 'requests_oauthlib>=0.7.0']
test_requirements = ['httmock>=1.2.6', 'pytest>=3.0.6', 'flaky>=3.3.0', 'vcrpy>=1.10.5']


setup(
    name='rt_api',
    version='1.0.1',
    description='Unofficial python client for the Rooster Teeth api',
    author='Nicholas Molloy',
    author_email='nick.a.molloy@gmail.com',
    packages=['rt_api'],
    install_requires=requires,
    license='GPLv3',
    url='https://github.com/NickMolloy/rt_api',
    zip_safe=False,
    classifiers=(
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Multimedia',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ),
    cmdclass={'test': PyTest},
    tests_require=test_requirements,
)
