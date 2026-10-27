"""What a build reports: the files that compiled, were skipped or failed, and why."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BuildError:
    path: str
    message: str
    line: int | None = None
    column: int | None = None
    type: str = "Exception"
    hint: str | None = None

    def format(self) -> str:
        if self.line is not None:
            col = self.column if self.column is not None else 0
            base = f"{self.path}:{self.line}:{col} - [{self.type}] {self.message}"
        else:
            base = f"{self.path} - [{self.type}] {self.message}"
        return f"{base}\n  Fix: {self.hint}" if self.hint else base


@dataclass
class BuildResult:
    success: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    errors: dict[str, BuildError] = field(default_factory=dict)
