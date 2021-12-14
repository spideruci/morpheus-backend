# -*- coding: utf-8 -*-
from setuptools import setup
from morpheus import __name__, __version__

setup(
    name=__name__,
    version=__version__,
    description="Backend for the morpheus visualization",
    packages=['morpheus',],
    license='MIT',
    install_requires = [
        'pyyaml==5.4',
        'GitPython==3.1',
        'flask==1.1',
        'flask-cors==3.0.9',
        'sqlalchemy==1.4',
        'flask-restx==0.5.1',
        'python-dotenv==0.15'
    ],
    tests_require = [
        'pytest',
        'tox'
    ],
    entry_points = {
        'console_scripts': [
            f'{__name__}=morpheus.matrix:main',
        ]
    }
)
