#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='BunnyPy',
    version='0.0.1',
    description='Lightweight Python Web Framework',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author='IvanLuLyf',
    author_email='me@ivanlu.cn',
    url='https://github.com/ivanlulyf/bunnypy',
    py_modules=['bunny'],
    scripts=['bunny.py'],
    license='MIT',
    platforms='any',
    classifiers=['Operating System :: OS Independent',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: MIT License',
                 'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
                 'Topic :: Internet :: WWW/HTTP :: WSGI',
                 'Topic :: Software Development :: Libraries :: Application Frameworks',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7',
                 ],
)
