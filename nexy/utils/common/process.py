import shutil
import subprocess


def run_tool(tool: str, args: list[str]) -> int | None:
    """Run *tool* with *args*, streaming output; None when it is not on PATH."""
    exe = shutil.which(tool)
    if not exe:
        return None
    return subprocess.run([exe, *args], check=False).returncode
