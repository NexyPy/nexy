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


def get_client_port(default: int = 5173) -> int:
    n = _read_port_file("__nexy__/client.port")
    if n is None:
        n = _read_port_file("__nexy__/vite.port")
    return n if n is not None else default


def network_ip() -> str:
    """The address of this machine on the local network, or loopback when it has none."""
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(("8.8.8.8", 80))
        return str(probe.getsockname()[0])
    except OSError:
        return "127.0.0.1"
    finally:
        probe.close()


def resolve_ports(host: str, base_port: int, with_client: bool = True) -> tuple[int, int]:
    """The server port, then the client port after it (0 when there is no client)."""
    server_port = find_available_port(base_port, host)
    client_port = find_available_port(server_port + 1, host) if with_client else 0
    return server_port, client_port
