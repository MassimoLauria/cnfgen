# content of conftest.py
import pytest
import os
import importlib

collect_ignore = ["setup.py"]
collect_ignore.append("docs/conf.py")

# Map rst files to the package they require
REQUIREMENTS = {
    "docs/graphs.rst": "networkx",
}


@pytest.fixture(autouse=True)
def tempdir_doctest_file(doctest_namespace, tmpdir):
    doctest_namespace['tmpdir'] = os.path.join(str(tmpdir), "")
    print(os.path.join(str(tmpdir), ""))


def pytest_ignore_collect(collection_path, config):
    rel = str(collection_path.relative_to(config.rootdir))
    required = REQUIREMENTS.get(rel)
    if required:
        try:
            importlib.import_module(required)
        except ImportError:
            return True  # True means "ignore this file"
