# content of conftest.py
import pytest
import os

collect_ignore = ["setup.py"]
collect_ignore.append("docs/conf.py")


@pytest.fixture(autouse=True)
def tempdir_doctest_file(doctest_namespace, tmpdir):
    doctest_namespace['tmpdir'] = os.path.join(str(tmpdir), "")
    print(os.path.join(str(tmpdir), ""))
