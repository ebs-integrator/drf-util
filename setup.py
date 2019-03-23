#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='drf_utils',
    version='0.0.3',
    description='Django Rest Framework Utils',
    author='EBS',
    author_email='office@ebs-integrator.com',
    url='https://git2.devebs.net/ebs-platform/drf-utils',
    packages=[
        'drf_utils',
    ],
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
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
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
    license='BSD',
)
