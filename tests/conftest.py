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

import pkgutil
import inspect
import importlib
from . import queries


pytest_plugins = ("terminal")

def pytest_generate_tests(metafunc):
    if 'test_class' in metafunc.fixturenames:
        query_tests = []
        query_list = [x.name for x in pkgutil.walk_packages(queries.__path__)]
        for query in query_list:
            query_module = importlib.import_module('.queries.{0}'.format(query), 'tests')
            for name, obj in inspect.getmembers(query_module, inspect.isclass):
                if obj.__module__.endswith(query):
                    query_tests.append(obj)

        metafunc.parametrize("test_class", query_tests)
