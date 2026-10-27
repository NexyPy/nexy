"""Where the skills shipped with Nexy live."""

from __future__ import annotations

from pathlib import Path

import nexy

_MARKER = Path("nexy-principles") / "SKILL.md"


def skills_source() -> Path:
    """The folder that holds the skills: inside an installed wheel, else at a checkout's root."""
    package = Path(nexy.__file__).resolve().parent
    for candidate in (package / "skills", package.parent / "skills"):
        if (candidate / _MARKER).is_file():
            return candidate
    raise FileNotFoundError("The skills shipped with Nexy were not found next to the package.")
