# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
# from morpheus import __name__, __version__

setup(
    name='morpheus',
    version='2.2-dev',
    description="Backend for the morpheus visualization",
    package_dir={"": "src"},
    packages=find_packages(where='src', exclude=['tests']),
    license='MIT',
    install_requires = [
        'jinja2==2.11.3',
        'itsdangerous==1.1.0',
        'werkzeug==2.2.3',
        'pyyaml==5.4',
        'GitPython==3.1',
        'flask==1.1.4',
        'flask-cors==3.0.10',
        'sqlalchemy==1.4',
        'flask-restx==0.5.1',
        'python-dotenv==0.15',
        'tqdm==4.62.3',
        'MarkupSafe==2.0.1',
        'gunicorn==20.1.0'
    ],
    python_requires=">=3.8",
    tests_require = [
        'pytest',
        'tox'
    ],
    entry_points = {
        'console_scripts': [
            'matrix=morpheus.matrix:main',
        ]
    }
)
