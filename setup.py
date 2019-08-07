#  Copyright (c) 2019 Erwin de Haan. All rights reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#  This file is part of the FletcherFiltering project

from setuptools import setup, find_packages
import importlib

def find_version(
        package_name: str, version_module_name: str = 'settings',
        version_variable_name: str = '__version__') -> str:
    """Simulate behaviour of "from package_name.settings import __version__", and return VERSION."""
    version_module = importlib.import_module(
        '{}.{}'.format(package_name.replace('-', '_'), version_module_name))
    return getattr(version_module, version_variable_name)

setup(
    name='FletcherFiltering',
    version=find_version('fletcherfiltering'),
    # packages=['fletcherfiltering', 'fletcherfiltering.codegen', 'fletcherfiltering.codegen.exceptions',
    #           'fletcherfiltering.codegen.transformations', 'fletcherfiltering.codegen.transformations.helpers'],
    package_dir={'': 'src'},
    package_data={'': ['**/template.*']},
    include_package_data=True,
    url='https://github.com/EraYaN/FletcherFiltering',
    license='',
    author='Erwin de Haan',
    author_email='',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    description='',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: C++',
        'Topic :: Education',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Compilers',
        'Topic :: Software Development :: Pre-processors',
        'Topic :: Utilities'
    ],
    install_requires=[
        'moz-sql-parser @ git+https://github.com/EraYaN/moz-sql-parser@object-ast',
        'typed-ast',
        'pyarrow',
        'numpy',
        'horast',
        'astunparse',
        'typed-astunparse',
        'transpyle[cpp] @ git+https://github.com/EraYaN/transpyle@cpp-unparsing-extensions',
    ],
    setup_requires=[
        "pytest-runner"
    ],
    tests_require=[
        "pytest",
        "pytest-cov",
        "pytest-print",
        "pytest-progress",
        "mysql-connector-python",
        "lipsum",
        "bitstring"
    ],
    packages=find_packages('./src')
)
