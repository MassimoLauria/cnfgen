# content of conftest.py
import pytest
import os

collect_ignore = ["setup.py"]
collect_ignore.append("docs/conf.py")

@pytest.fixture(autouse=True)
def tempdir_doctest_file(doctest_namespace, tmp_path):
    doctest_namespace['tmp_path'] = os.path.join(tmp_path, "")
    print(tmp_path)
