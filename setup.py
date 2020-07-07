#!/usr/bin/env python
# coding: utf-8

'''
@author: Shuai Li
@license: (C) Copyright 2015-2020, Shuai Li.
@contact: li.shuai@wustl.edu
@IDE: pycharm
@file: setup.py
@time: 7/7/20 21:46
@desc:
'''


import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='ThaiAddressParser',
    version='1.0.0',
    author='Shuai Li',
    author_email='li.shuai@wustl.edu',
    url='https://github.com/HandsomeBrotherShuaiLi/ThaiAddressParser',
    description="Thailand Address Parser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=['bs4','requests','tqdm'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)