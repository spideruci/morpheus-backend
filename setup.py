#/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup
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
        'pyyaml==5.3.1', 
        'numpy==1.19.0',
        'flask==1.1.2',
        'flask-cors==3.0.8',
        'scikit-learn==0.23.2',
        'docker==4.*'
    ],
    tests_require = [
        'pytest'
    ],
    entry_points = {
        'console_scripts': [
            'tacoco-runner=spidertools.runners.tacoco_cli:main',
            'pluperfect=spidertools.runners.pluperfect_cli:main',
            'spider-serve=spidertools.runners.server_cli:main',
            'spider-runner=spidertools.runners.docker_cli:main',
        ]
    }
)
