
from tortoise import fields
from tortoise.models import Model


class TodoModel(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=200)
    done = fields.BooleanField(default=False)

    class Meta:
        table = "todos"
