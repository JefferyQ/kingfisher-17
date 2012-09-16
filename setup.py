#!/usr/bin/env python

from distutils.core import setup


setup(
    name='kingfisher',
    version='0.1',
    description='A DNS server',
    long_description='A DNS server',
    author='Alex Lee',
    author_email='kingfisher@thirdbeat.com',
    maintainer='Alex Lee',
    maintainer_email='kingfisher@thirdbeat.com',
    url='http://kingfisher.thirdbeat.com',
    classifiers=[
    ],
    scripts=['scripts/kingfisher'],
    packages=['kingfisher'],
    requires=[
        'docopt (>= 0.50)',
    ],
)
