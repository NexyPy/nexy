from nexy.__version__ import __version__


def test_version_is_string() -> None:
    assert isinstance(__version__, str)


def test_version_not_empty() -> None:
    assert len(__version__) > 0


def test_version_matches_semver() -> None:
    import re
    assert re.match(r"^\d+\.\d+\.\d+", __version__)
