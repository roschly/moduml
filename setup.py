from setuptools import setup, find_packages


setup(
    name='moduml',
    # version='0.1.0',    
    description='UML-inspired diagrams of python modules and packages.',
    url='https://github.com/roschly/moduml',
    author='roschly',
    author_email='',
    entry_points='''
        [console_scripts]
        moduml=moduml.__main__:main
    ''',
    packages=find_packages(include=['moduml', 'moduml.*']),
    install_requires=[
                        'astroid',
                        'networkx',
                        'pydot',
                        'matplotlib',
                     ],
)