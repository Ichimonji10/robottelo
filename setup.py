#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

with open('README.rst', 'r') as f:
    README = f.read()

setup(
    name='robottelo',
    version='0.1.0',
    description='Robottelo is a test suite which exercises The Foreman.',
    long_description=README,
    author=u'Satellite QE Team',
    url='https://github.com/SatelliteQE/robottelo',
    packages=find_packages(exclude=['tests*']),
    package_data={'': ['LICENSE']},
    include_package_data=True,
    install_requires=[
        'cachetools',
        'cryptography',
        'fauxfactory',
        'inflector',
        # 'nailgun',
        'blinker',
        'numpy',
        'paramiko',
        'pygal',
        'pytest',
        'python-bugzilla',
        'PyYAML',
        'requests',
        'selenium<2.49',
        'six',
        'unittest2',
    ],
    license='GNU GPL v3.0',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux'
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ),
)
