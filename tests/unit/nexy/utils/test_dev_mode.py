"""Dev mode: the Vite port to proxy, only for the application `nexy dev` serves."""

from nexy.helpers.server.dev_mode import vite_proxy_port


def test_vite_proxy_port_is_none_when_vite_disabled(nexy_project, tmp_path, monkeypatch) -> None:
    nexy_project("useVite = False")
    (tmp_path / "vite.config.ts").write_text("", encoding="utf-8")
    monkeypatch.setenv("NEXY_DEV_SERVER", "1")
    assert vite_proxy_port() is None


def test_vite_proxy_port_is_none_outside_dev_mode(tmp_path, monkeypatch) -> None:
    (tmp_path / "__nexy__").mkdir()
    (tmp_path / "vite.config.ts").write_text("", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("NEXY_DEV_SERVER", raising=False)
    assert vite_proxy_port() is None


def test_vite_proxy_port_is_none_in_production(tmp_path, monkeypatch) -> None:
    (tmp_path / "__nexy__").mkdir()
    (tmp_path / "__nexy__" / "nexy.prod").write_text("", encoding="utf-8")
    (tmp_path / "vite.config.ts").write_text("", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("NEXY_DEV_SERVER", "1")
    assert vite_proxy_port() is None


def test_vite_proxy_port_is_none_without_vite_config(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("NEXY_DEV_SERVER", "1")
    assert vite_proxy_port() is None


def test_vite_proxy_port_reads_client_port(tmp_path, monkeypatch) -> None:
    (tmp_path / "__nexy__").mkdir()
    (tmp_path / "vite.config.ts").write_text("", encoding="utf-8")
    (tmp_path / "__nexy__" / "client.port").write_text("5199", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("NEXY_DEV_SERVER", "1")
    assert vite_proxy_port() == 5199
