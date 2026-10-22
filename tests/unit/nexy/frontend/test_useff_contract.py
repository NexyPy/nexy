from nexy.modules.frontend.vite_entry import frameworks_of, normalize_ff


class _FF:
    def __init__(self, name: str) -> None:
        self.name = name


def test_normalize_wraps_single_framework() -> None:
    ff = _FF("react")

    assert normalize_ff(ff) == [ff]


def test_normalize_filters_none_from_list() -> None:
    ff = _FF("react")

    assert normalize_ff([None, ff]) == [ff]


def test_normalize_empty_list_stays_empty() -> None:
    assert normalize_ff([]) == []


def test_frameworks_of_lowercases_names() -> None:
    assert frameworks_of([_FF("React"), None]) == {"react"}
