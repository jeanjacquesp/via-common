#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#

import sys

import setuptools
from setuptools import setup

CURRENT_PYTHON = sys.version_info[:2]
REQUIRED_PYTHON = (3, 8)

# This check and everything above must remain compatible with Python 2.7.
if CURRENT_PYTHON < REQUIRED_PYTHON:
    sys.stderr.write("""
==========================
Unsupported Python version
==========================
via_common requires Python {}.{}, and you're trying to install it on Python {}.{}.
""".format(*(REQUIRED_PYTHON + CURRENT_PYTHON)))
    sys.exit(1)


long_description = ('via-common is a common package for Project-VIA projects')

setup(
    name='via_common',
    version='0.0.1',
    description='via-common package',
    long_description=open('README.rst').read(),
    maintainer='Pax Syriana Foundation',
    maintainer_email='opensource@paxsyriana.com',
    url='https://project-via.org',
    packages=setuptools.find_packages(include=['via_common', 'via_common.*', 'via_common', 'via_common.*']),
    license='OSI Approved :: Apache Software License',
    install_requires=['', ''],
    package_data={'': ['LICENSE', 'README.md']},
    extras_require={
        '': [''],
        '': ['']
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Communications',
        'Topic :: Internet',
        'Topic :: System :: Networking'
    ],
    zip_safe=True)

