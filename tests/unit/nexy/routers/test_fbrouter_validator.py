import pytest

from nexy.modules.routers.fbrouter.validator import RouteValidator


def _handler_with_id(user_id: str) -> None:  # noqa: ARG001
    return None


def _handler_without_params() -> None:
    return None


def test_extract_path_params_reads_names_and_types() -> None:
    assert RouteValidator.extract_path_params("/a/{user_id}/b/{slug:int}") == {
        "user_id",
        "slug",
    }


def test_extract_path_params_without_params_is_empty() -> None:
    assert RouteValidator.extract_path_params("/about") == set()


def test_validate_sig_rejects_missing_parameter() -> None:
    with pytest.raises(RuntimeError, match="missing parameters: user_id"):
        RouteValidator.validate_sig(_handler_without_params, "/u/{user_id}", "GET")


def test_validate_sig_accepts_matching_signature() -> None:
    RouteValidator.validate_sig(_handler_with_id, "/u/{user_id}", "GET")


def test_validate_sig_skips_non_introspectable_handler() -> None:
    RouteValidator.validate_sig(int, "/u/{user_id}", "GET")
