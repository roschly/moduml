from typing import List
from setuptools import setup, find_packages

def get_requirements() -> List[str]:
    pip_packages = []
    with open("requirements.txt") as fh:
        for line in fh.readlines():
            pip_packages.append(line)
    return pip_packages

setup(
    name='moduml',
    description='UML-inspired diagrams of python modules and packages.',
    url='https://github.com/roschly/moduml',
    author='roschly',
    entry_points={
        'console_scripts': [
            'moduml = moduml.__main__:main',
        ]
    },
    packages=find_packages(),
    install_requires=get_requirements()
)