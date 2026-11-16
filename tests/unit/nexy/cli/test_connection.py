"""What `nx new` says about the connection before it downloads packages, in uv's words."""

from nexy.helpers.common.network import Connection
from nexy.modules.cli.init.connection import is_usable


def test_no_connection_is_a_warning(capsys):
    is_usable(Connection(False, None, None))
    assert capsys.readouterr().out.startswith("warning: No connection")


def test_no_connection_gives_a_hint_to_install_later(capsys):
    is_usable(Connection(False, None, None))
    assert capsys.readouterr().out.splitlines()[1].startswith("hint: When you are online")


def test_a_slow_connection_is_a_warning(capsys):
    is_usable(Connection(True, 900.0, 20.0))
    assert "warning: Slow connection" in capsys.readouterr().out


def test_a_good_connection_is_one_plain_line(capsys):
    is_usable(Connection(True, 30.0, 3000.0))
    assert capsys.readouterr().out.startswith("Connection: 30 ms")
