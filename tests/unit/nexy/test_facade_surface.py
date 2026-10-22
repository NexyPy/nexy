import nexy


def test_all_exports_resolve() -> None:
    for name in nexy.__all__:
        if name == "app":
            continue  # deployment contract, covered by the dedicated test
        assert getattr(nexy, name) is not None, f"nexy.{name}"


def test_app_stays_declared_as_deployment_contract() -> None:
    # `nexy.app:app` is the uvicorn target of every generated project. It is
    # resolved through the import-system submodule fallback (importing the
    # facade attribute would build the AppServer singleton), so the surface
    # guard only asserts the declaration, not an attribute.
    assert "app" in nexy.__all__
