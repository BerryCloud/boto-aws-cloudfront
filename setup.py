# -*- coding: utf-8 -*-
import os
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='boto_aws_cloudfront',
    version='1.0',
    description='Boto AWS CloudFront wrapper',
    author='Pavel Žák',
    author_email='pavel@berrycloud.cz',
    url='https://github.com/berrycloud/boto-aws-cloudfront/',
    packages=['boto_aws_cloudfront'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    long_description=read('README.md'),
    cmdclass={'test': 'pytest'},
)
