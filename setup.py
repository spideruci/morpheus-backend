#/usr/bin/env python3
# -*- coding: utf-8 -*-
from distutils.core import setup

from spidertools import __version__

setup(
    name='spidertools',
    version=__version__,
    description="A Python3 wrapper library for SpiderLab tools.",
    packages=['spidertools',],
    license='MIT',
    long_description=open('README.md').read(),
    install_requires = [
        'GitPython==3.1.3',
        'pyyaml==5.3.1'
    ],
    entry_points = {
        'console_scripts': [
            'tacoco-runner=spidertools.runners.tacoco_cli:main',
        ]
    }
)
