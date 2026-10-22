import socket
from pathlib import Path

from nexy.helpers.fs.vfs import VFS


def _is_port_available(host: str, port: int) -> bool:
    """
    Checks if a port is free by combining a connection attempt
    and a binding fallback.
    """
    check_host = "127.0.0.1" if host == "0.0.0.0" else host  # nosec B104 - probe never binds

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.02)
        try:
            sock.connect((check_host, port))
            return False
        except (TimeoutError, ConnectionRefusedError):
            pass
        except OSError:
            pass

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        if host != "0.0.0.0":  # nosec B104 - literal comparison, not a bind address
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
            return True
        except OSError:
            return False


def find_available_port(
    start_port: int = 3000,
    host: str = "127.0.0.1",
    max_attempts: int = 1000,
) -> int:
    """Scans ports until an available one is found."""
    h = host or "127.0.0.1"
    for port in range(start_port, start_port + max_attempts):
        if _is_port_available(h, port):
            return port
    raise RuntimeError(f"No available port found on {host} around {start_port}")


def _read_port_file(path: str | Path) -> int | None:
    vfs = VFS()
    path_str = str(path).replace("\\", "/")
    if not vfs.exists(path_str):
        return None
    try:
        txt = vfs.read(path_str).strip()
        n = int(txt)
        return n if n > 0 else None
    except Exception:
        return None


def generate_port(
    host: str, base_port: int | None = None, default_port: int = 3000
) -> tuple[int, int]:
    """Generates server and client ports and saves them to files."""
    run_host = host or "127.0.0.1"
    if base_port is not None and base_port > 0:
        server_port = base_port
    else:
        server_port = find_available_port(default_port, run_host)

    client_port = find_available_port(server_port + 1, run_host)

    vfs = VFS()
    vfs.write("__nexy__/server.port", str(server_port))
    vfs.write("__nexy__/client.port", str(client_port))
    return server_port, client_port


def get_server_port(default: int = 3000) -> int:
    n = _read_port_file("__nexy__/server.port")
    return n if n is not None else default


def get_client_port(default: int = 5173) -> int:
    n = _read_port_file("__nexy__/client.port")
    if n is None:
        n = _read_port_file("__nexy__/vite.port")
    return n if n is not None else default


def get_vite_port(default: int = 5173) -> int:
    return get_client_port(default)


def is_port_open(host: str, port: int, timeout: float = 0.2) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False
