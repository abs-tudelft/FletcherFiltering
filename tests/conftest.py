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
