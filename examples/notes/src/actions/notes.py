"""The actions of the notes. Each one runs on the Tortoise loop through `arun` (src/configs/db.py)."""

from datetime import datetime

from nexy import notFound
from nexy.decorators import Action
from pydantic import BaseModel

from src.configs.db import arun
from src.models.note_model import NoteModel
from src.services.markdown import excerpt, to_html
from src.services.note_service import NoteService

LONGEST_TITLE = 120
LONGEST_BODY = 20_000


class Summary(BaseModel):
    id: int
    title: str
    excerpt: str
    pinned: bool
    updated_at: datetime


class Note(BaseModel):
    id: int
    title: str
    body: str
    pinned: bool
    updated_at: datetime


class Saved(BaseModel):
    note: Note | None = None  # the note as stored; None when nothing was stored
    problem: str = ""  # why it was not stored


def summary_of(note: NoteModel) -> Summary:
    return Summary(
        id=note.id,
        title=note.title,
        excerpt=excerpt(note.body),
        pinned=note.pinned,
        updated_at=note.updated_at,
    )


def note_of(note: NoteModel | None) -> Note:
    """The note for the page; a 404 when there is none, so a deleted note says so."""
    if note is None:
        notFound()
    return Note(
        id=note.id, title=note.title, body=note.body, pinned=note.pinned, updated_at=note.updated_at
    )


def problem(title: str, body: str) -> str:
    if len(title) > LONGEST_TITLE:
        return f"Keep the title under {LONGEST_TITLE} characters."
    if len(body) > LONGEST_BODY:
        return f"Keep a note under {LONGEST_BODY:,} characters: split it in two."
    return ""


@Action
async def notes(search: str = "") -> list[Summary]:
    """Every note, or the ones that hold `search`: pinned first, then the latest changed."""
    return [summary_of(note) for note in await arun(NoteService.all(search))]


@Action
async def note(note_id: int) -> Note:
    return note_of(await arun(NoteService.find(note_id)))


@Action
async def create_note() -> Note:
    return note_of(await arun(NoteService.create()))


@Action
async def save_note(note_id: int, title: str, body: str) -> Saved:
    """Store what the editor holds, or say why not; the editor calls it while you type."""
    title = title.strip()
    refused = problem(title, body)
    if refused:
        return Saved(problem=refused)
    return Saved(note=note_of(await arun(NoteService.save(note_id, title, body))))


@Action
async def pin_note(note_id: int, pinned: bool) -> Note:
    return note_of(await arun(NoteService.pin(note_id, pinned)))


@Action
async def delete_note(note_id: int) -> bool:
    """True when the note was there to delete."""
    return await arun(NoteService.remove(note_id))


@Action
async def preview(body: str) -> str:
    """The HTML of a Markdown body, for the Preview tab."""
    return to_html(body)
