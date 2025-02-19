from packaging.version import Version

import croniters


def test_version():
    assert croniters.__version__ == croniters.VERSION
    assert isinstance(Version(croniters.__version__), Version)
