"""Every read and write of the notes. The actions of `src/actions/notes.py` call nothing else."""

from tortoise.expressions import Q

from src.models.note_model import NoteModel


class NoteService:
    @staticmethod
    async def all(search: str = "") -> list[NoteModel]:
        """The notes whose title or body holds `search`: pinned first, then the latest changed."""
        query = NoteModel.all()
        words = search.strip()
        if words:
            query = query.filter(Q(title__icontains=words) | Q(body__icontains=words))
        return await query.order_by("-pinned", "-updated_at", "-id")

    @staticmethod
    async def find(note_id: int) -> NoteModel | None:
        return await NoteModel.get_or_none(id=note_id)

    @staticmethod
    async def create() -> NoteModel:
        return await NoteModel.create()

    @staticmethod
    async def save(note_id: int, title: str, body: str) -> NoteModel | None:
        note = await NoteModel.get_or_none(id=note_id)
        if note is not None:
            note.title, note.body = title, body
            await note.save()
        return note

    @staticmethod
    async def pin(note_id: int, pinned: bool) -> NoteModel | None:
        note = await NoteModel.get_or_none(id=note_id)
        if note is not None:
            note.pinned = pinned
            await note.save(update_fields=["pinned"])
        return note

    @staticmethod
    async def remove(note_id: int) -> bool:
        return await NoteModel.filter(id=note_id).delete() > 0
