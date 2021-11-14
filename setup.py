# -*- coding: utf-8 -*-
from setuptools import setup
from morpheus import __version__

setup(
    name='morpheus',
    version=__version__,
    description="Backend for the morpheus visualization",
    packages=['morpheus',],
    license='MIT',
    install_requires = [
        'pyyaml==5.4',
        'GitPython==3.1.12',
        'flask==1.1.2',
        'flask-cors==3.0.9',
        'sqlalchemy==1.3',
        'flask-restx==0.5.1',
        'python-dotenv==0.15.0'
    ],
    tests_require = [
        'pytest'
    ],
    entry_points = {
        'console_scripts': [
            'matrix=morpheus.matrix:main',
        ]
    }
)

