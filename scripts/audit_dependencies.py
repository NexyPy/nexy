"""Run the dependency audit locally against the frozen lock envelope.

CI remains authoritative; this script exists so the same gate can be replayed
on a workstation. It retries transient PyPI failures only: an actual advisory
is never retried and never hidden.
"""

import re
import subprocess
import sys

EXPORT = [
    "uv",
    "export",
    "--frozen",
    "--no-emit-project",
    "--format",
    "requirements.txt",
    "-o",
    "requirements-audit.txt",
]
AUDIT = [
    "-m",
    "pip_audit",
    "-r",
    "requirements-audit.txt",
    "--disable-pip",
    "--strict",
    "--timeout",
    "60",
    "--ignore-vuln",
    "PYSEC-2022-252",
]
NETWORK_ERROR = re.compile(
    r"timed? ?out|timeout|connection (?:reset|refused|aborted)|temporary failure|name or service",
    re.IGNORECASE,
)
ATTEMPTS = 3


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=False, capture_output=True, text=True)


def main() -> int:
    export = _run(EXPORT)
    if export.returncode != 0:
        sys.stderr.write(export.stderr)
        return export.returncode

    for attempt in range(1, ATTEMPTS + 1):
        result = _run([sys.executable, *AUDIT])
        sys.stdout.write(result.stdout)
        sys.stderr.write(result.stderr)
        if result.returncode == 0:
            return 0
        combined = f"{result.stdout}\n{result.stderr}"
        if attempt == ATTEMPTS or not NETWORK_ERROR.search(combined):
            return result.returncode
        print(f"[audit] transient network failure, retrying ({attempt}/{ATTEMPTS})")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
