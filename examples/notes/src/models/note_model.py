"""The notes. The body is Markdown, kept as it was typed: the page renders it, the table never does."""

from tortoise import fields
from tortoise.models import Model


class NoteModel(Model):
    id = fields.IntField(primary_key=True)
    title = fields.CharField(max_length=120, default="")
    body = fields.TextField(default="")
    pinned = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "notes"
