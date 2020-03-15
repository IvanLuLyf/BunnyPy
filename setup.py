#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

import bunnypy

setup(
    name='BunnyPy',
    version=bunnypy.__version__,
    description='Lightweight Python Web Framework',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    author='IvanLuLyf',
    author_email='me@ivanlu.cn',
    url='https://github.com/ivanlulyf/bunnypy',
    packages=find_packages(),
    # py_modules=['bunnypy'],
    # scripts=['bunnypy/bunnypy.py'],
    include_package_data=True,
    # package_data={'bunnypy/asset': ['asset/*.html']},
    license='MIT',
    platforms='any',
    classifiers=['Operating System :: OS Independent',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: MIT License',
                 'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
                 'Topic :: Internet :: WWW/HTTP :: WSGI',
                 'Topic :: Software Development :: Libraries :: Application Frameworks',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7',
                 ],
)
