from typing import List
from setuptools import setup, find_packages


setup(
    name='moduml',
    description='UML-inspired diagrams of python modules and packages.',
    url='https://github.com/roschly/moduml',
    download_url='https://github.com/roschly/moduml/archive/refs/tags/v0.1.1.tar.gz',
    author='roschly',
    entry_points={
        'console_scripts': [
            'moduml = moduml.__main__:main',
        ]
    },
    packages=find_packages(),
    install_requires=[
        'astroid',
        'networkx',
        'pydot',
    ]
)