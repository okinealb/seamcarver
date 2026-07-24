from importlib.metadata import version

import seamcarver


def test_version_matches_distribution():
    assert seamcarver.__version__ == version("seamcarver")
