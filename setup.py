#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='drf_util',
    version='0.0.20',
    description='Django Rest Framework Utils',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='EBS Integrator',
    author_email='office@ebs-integrator.com',
    url='https://github.com/EnterpriseBusinessSolutions/drf-util',
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Utilities',
    ],
    python_requires=">=3.4",
    install_requires=[
        'Django>=1.11',
        'djangorestframework',
        'python-dateutil',
        'elasticsearch',
    ],
    license='MIT',
)
