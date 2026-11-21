"""The menu of the docs: its sections, its pages in reading order, and the pages around one."""

from dataclasses import dataclass
from pathlib import Path

ROUTES = Path(__file__).resolve().parents[1] / "routes"


@dataclass(frozen=True)
class Page:
    title: str
    url: str

    @property
    def file(self) -> Path:
        """The Markdown file that answers this address."""
        path = self.url.removeprefix("/")
        return ROUTES / (f"{path}/index.md" if path == "docs" else f"{path}.md")


@dataclass(frozen=True)
class Section:
    title: str
    pages: tuple[Page, ...]


SECTIONS = (
    Section(
        "Get started",
        (
            Page("Introduction", "/docs"),
            Page("Installation", "/docs/installation"),
            Page("Quick start", "/docs/quick-start"),
            Page("Configuration", "/docs/configuration"),
        ),
    ),
    Section(
        "Commands",
        (
            Page("backup", "/docs/commands/backup"),
            Page("restore", "/docs/commands/restore"),
            Page("prune", "/docs/commands/prune"),
        ),
    ),
    Section(
        "Guides",
        (
            Page("Schedule backups", "/docs/guides/schedule"),
            Page("Encryption", "/docs/guides/encryption"),
        ),
    ),
    Section(
        "Reference",
        (
            Page("Exit codes", "/docs/reference/exit-codes"),
            Page("Questions", "/docs/faq"),
        ),
    ),
)

PAGES = [page for section in SECTIONS for page in section.pages]


def neighbours(url: str) -> tuple[Page | None, Page | None]:
    """The page before and the page after this one, in the order of the menu."""
    urls = [page.url for page in PAGES]
    if url not in urls:
        return None, None
    at = urls.index(url)
    before = PAGES[at - 1] if at > 0 else None
    after = PAGES[at + 1] if at + 1 < len(PAGES) else None
    return before, after
