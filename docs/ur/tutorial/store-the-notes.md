# Nexy کے ساتھ ایک نوٹس ایپ بنائیں، حصہ 5: نوٹوں کو SQLite میں اسٹور کریں۔

حصہ 5 نوٹوں کو Python لغت سے ایک SQLite ڈیٹا بیس میں منتقل کرتا ہے، جس میں ایک ماڈل، ایک منتقلی اور شروع کرنے کے لیے دو نوٹس ہوتے ہیں، اور صفحات انہیں وہاں سے پڑھتے ہیں۔

**اس سے پہلے کہ آپ شروع کریں:** [پارٹ 4](components.md) کی ایپ۔

## ORM اور مائیگریشن ٹول انسٹال کریں۔

```bash
uv add sqlmodel alembic
```

[SQLModel](https://sqlmodel.tiangolo.com/) ایک ٹیبل کو Python کلاس کے طور پر بیان کرتا ہے، اور Alembic ان کلاسوں میں ہونے والی تبدیلیوں کو منتقلی میں بدل دیتا ہے۔ Nexy بھی نہیں لپیٹتا ہے: آپ انہیں جیسے ہیں استعمال کرتے ہیں۔

## ڈیٹا بیس کھولیں۔

ڈیٹا بیس کا پتہ پروجیکٹ کی جڑ میں `.env` میں جاتا ہے۔ `nx migrate` اور ایپ دونوں نے اسے وہاں سے پڑھا:

```bash filename="env"
DATABASE_URL=sqlite:///dev.db
```

`sqlite:///dev.db` ایک فائل ہے، `dev.db`، `nexyconfig.py` کے آگے: SQLite کو سرور کی ضرورت نہیں ہے۔ `.env` کو گٹ سے دور رکھیں: یہ ایک حقیقی ڈیٹا بیس کے راز رکھتا ہے۔

انجن ڈیٹا بیس سے کنکشن ہے۔ یہ پڑھتا ہے `DATABASE_URL`، اسی فائل کے ساتھ بطور ڈیفالٹ جب متغیر سیٹ نہ ہو:

```python filename="src/configs/db.py"
import os

from dotenv import load_dotenv
from sqlmodel import create_engine

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL", "sqlite:///dev.db"))
```

## ایک نوٹ بیان کریں۔

<!-- router:fbr,custom -->
```python filename="src/models/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
```
<!-- /router -->

<!-- router:modular -->
ماڈل اس خصوصیت کے ساتھ رہتا ہے جس سے اس کا تعلق ہے، اس کے کنٹرولر کے ساتھ:

```python filename="src/apps/notes/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
```
<!-- /router -->

`table=True` کلاس کو ایک میز بناتا ہے، `note`۔ جب کوئی نوٹ محفوظ کیا جاتا ہے تو ڈیٹا بیس کے ذریعہ `id` دیا جاتا ہے۔

## ہجرت کے ساتھ ٹیبل بنائیں

```bash
nx migrate --init
nx migrate -m "create notes"
nx migrate --upgrade
```

`--init` `alembic/` فولڈر لکھتا ہے اور اسے آپ کے ماڈل کی طرف اشارہ کرتا ہے۔ `-m` ماڈل کا ڈیٹا بیس سے موازنہ کرتا ہے اور ہجرت لکھتا ہے جو ٹیبل بناتا ہے۔ `--upgrade` اسے چلاتا ہے۔ ماڈل کو بعد میں تبدیل کریں، آخری دو کمانڈز کو دوبارہ چلائیں، اور ٹیبل مندرجہ ذیل ہے۔

## ڈیٹا بیس سے نوٹس پڑھیں

`src/notes.py` کے افعال اپنے نام رکھتے ہیں، اس لیے صفحات بہت کم بدلتے ہیں: اب وہ سیشن کھولتے ہیں، ٹیبل سے استفسار کرتے ہیں، اور تاروں کی بجائے `Note` اشیاء واپس کرتے ہیں۔

<!-- router:fbr,custom -->
```python filename="src/notes.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.note_model import Note


def all_notes() -> list[Note]:
    with Session(engine) as session:
        return list(session.exec(select(Note).order_by(Note.id)))


def find(note_id: int) -> Note | None:
    with Session(engine) as session:
        return session.get(Note, note_id)
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/notes.py"
from sqlmodel import Session, select

from src.apps.notes.note_model import Note
from src.configs.db import engine


def all_notes() -> list[Note]:
    with Session(engine) as session:
        return list(session.exec(select(Note).order_by(Note.id)))


def find(note_id: int) -> Note | None:
    with Session(engine) as session:
        return session.get(Note, note_id)
```
<!-- /router -->

## شروع کرنے کے لیے دو نوٹ شامل کریں۔

ایک بیج اسکرپٹ ایک خالی ڈیٹا بیس کو بھرتا ہے، لہذا پروجیکٹ کی ہر نئی کاپی کچھ دکھانے کے ساتھ شروع ہوتی ہے:

<!-- router:fbr,custom -->
```python filename="src/seed.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.note_model import Note


def seed() -> None:
    with Session(engine) as session:
        if session.exec(select(Note)).first() is None:
            session.add_all([Note(text="Buy milk"), Note(text="Ship Nexy")])
            session.commit()


if __name__ == "__main__":
    seed()
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/seed.py"
from sqlmodel import Session, select

from src.apps.notes.note_model import Note
from src.configs.db import engine


def seed() -> None:
    with Session(engine) as session:
        if session.exec(select(Note)).first() is None:
            session.add_all([Note(text="Buy milk"), Note(text="Ship Nexy")])
            session.commit()


if __name__ == "__main__":
    seed()
```
<!-- /router -->

```bash
python -m src.seed
```

آغاز پر، Nexy [حصہ 6](create-a-note.md) کے ایکشنز کو تلاش کرنے کے لیے `src/` کے ہر ماڈیول کو درآمد کرتا ہے۔ `if __name__ == "__main__":` مندرجہ بالا کمانڈ کے لیے بیج رکھتا ہے: ایپ کے ذریعے درآمد کردہ، فائل صرف `seed` کی وضاحت کرتی ہے، اور کچھ بھی نہیں چھوتی۔

## ڈیٹا بیس سے نوٹس دکھائیں۔

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import all_notes

notes = all_notes()
---
<section class="app-page">
  <h1>Notes</h1>
  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}
</section>
```

```nexy filename="src/routes/notes/[id].nexy"
---
from nexy import notFound
from src.notes import find

id: prop[int]
note = find(id)
if note is None:
    notFound()
---
<section class="app-page">
  <h1>{{ note.text }}</h1>
  <a href="/notes">All notes</a>
</section>
```

```python filename="src/routes/api/notes.py"
from src.notes import all_notes


async def GET():
    return [note.model_dump() for note in all_notes()]
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import all_notes

notes = all_notes()
---
<section class="app-page">
  <h1>Notes</h1>
  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}
</section>
```

```python filename="src/apps/notes/notes_controller.py"
from nexy import notFound
from nexy.decorators import Controller
from nexy.hooks import useViews
from src.notes import all_notes, find

LAYOUT = "src/apps/layout.nexy"


def page(view: str, **context: object):
    return useViews(LAYOUT, context={"children": useViews(view, context=context)})


@Controller("/notes")
class NotesController:
    async def get(self):
        return page("src/apps/notes/notes_view.nexy")


@Controller("/notes/{id}")
class NoteController:
    async def get(self, id: int):
        note = find(id)
        if note is None:
            notFound()
        return page("src/apps/notes/note_view.nexy", text=note.text)


@Controller("/api/notes")
class NotesApiController:
    async def get(self) -> list[dict]:
        return [note.model_dump() for note in all_notes()]
```
<!-- /router -->

کھولیں <http://localhost:3000/notes>: وہی دو کارڈ، اب `dev.db` سے پڑھیں۔ دوبارہ شروع کریں `nexy dev`، اور وہ ابھی تک موجود ہیں۔

## جو آپ نے سیکھا۔

- SQLModel ایک میز کو کلاس کے طور پر بیان کرتا ہے۔ `src/configs/db.py` میں انجن ڈیٹا بیس کو کھولتا ہے۔
- `nx migrate` لکھتے ہیں اور ہجرت چلاتے ہیں: `--init` ایک بار، پھر `-m` اور `--upgrade` فی تبدیلی۔
- صفحات اور کنٹرولرز سادہ Python فنکشنز کو کال کرتے ہیں جو ڈیٹا بیس سے استفسار کرتے ہیں: Nexy کوئی پرت نہیں ڈالتا۔

## اگلے اقدامات

- [حصہ 6: فارم سے ایک نوٹ بنائیں](create-a-note.md)
- [SQLite](../databases/sqlite.md): pragmas، async رسائی اور ان میموری ڈیٹا بیس پر ٹیسٹ
