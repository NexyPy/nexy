# إنشاء تطبيق ملاحظات باستخدام Nexy، الجزء 5: تخزين الملاحظات في SQLite

ينقل الجزء الخامس الملاحظات من قاموس Python إلى قاعدة بيانات SQLite، مع نموذج وترحيل وملاحظتين للبدء بهما، وتقرأها الصفحات من هناك.

**قبل أن تبدأ:** تطبيق [الجزء الرابع](components.md).

## قم بتثبيت ORM وأداة الترحيل

```bash
uv add sqlmodel alembic
```

[SQLModel](https://sqlmodel.tiangolo.com/) يصف الجدول كفئة Python، و Alembic يحول التغييرات على تلك الفئات إلى عمليات ترحيل. لا يتم تغليف Nexy أيضًا: يمكنك استخدامها كما هي.

## افتح قاعدة البيانات

عنوان قاعدة البيانات موجود في `.env`، في جذر المشروع. `nx migrate` ويقوم التطبيق بقراءتها من هناك:

```bash filename=".env"
DATABASE_URL=sqlite:///dev.db
```

`sqlite:///dev.db` هو ملف، `dev.db`، بجوار `nexyconfig.py`: SQLite لا يحتاج إلى خادم. احتفظ بـ `.env` خارج Git: فهو يحتوي على أسرار قاعدة بيانات حقيقية.

المحرك هو الاتصال بقاعدة البيانات. يقرأ `DATABASE_URL`، مع نفس الملف كافتراضي عندما يكون المتغير غير مضبوط:

```python filename="src/configs/db.py"
import os

from dotenv import load_dotenv
from sqlmodel import create_engine

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL", "sqlite:///dev.db"))
```

## وصف ملاحظة

<!-- router:fbr,custom -->
```python filename="src/models/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
```
<!-- /router -->

<!-- router:modular -->
يعيش النموذج مع الميزة التي ينتمي إليها، بجانب وحدة التحكم الخاصة به:

```python filename="src/apps/notes/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
```
<!-- /router -->

`table=True` يجعل الفصل جدولاً، `note`. يتم توفير `id` بواسطة قاعدة البيانات عند حفظ ملاحظة.

## قم بإنشاء الجدول بالترحيل

```bash
nx migrate --init
nx migrate -m "create notes"
nx migrate --upgrade
```

`--init` يكتب المجلد `alembic/` ويوجهه نحو النموذج الخاص بك. `-m` يقارن النموذج بقاعدة البيانات ويكتب الترحيل الذي ينشئ الجدول؛ `--upgrade` يديره. قم بتغيير النموذج لاحقًا، وقم بتشغيل الأمرين الأخيرين مرة أخرى، وسيتبعك الجدول.

## قراءة الملاحظات من قاعدة البيانات

تحتفظ وظائف `src/notes.py` بأسمائها، وبالتالي تتغير الصفحات قليلاً: فهي الآن تفتح جلسة، وتقوم بالاستعلام عن الجدول، وتعيد كائنات `Note` بدلاً من السلاسل.

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

## أضف ملاحظتين لتبدأ بهما

يملأ البرنامج النصي الأساسي قاعدة بيانات فارغة، لذا تبدأ كل نسخة جديدة من المشروع بشيء لإظهاره:

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

عند بدء التشغيل، يقوم Nexy باستيراد كل وحدة من `src/` للعثور على إجراءات [الجزء 6](create-a-note.md). `if __name__ == "__main__":` يحتفظ ببذرة الأمر أعلاه: يتم استيراده بواسطة التطبيق، ويحدد الملف فقط `seed`، ولا يمس أي شيء.

## إظهار الملاحظات من قاعدة البيانات

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

فتح <http://localhost:3000/notes>: نفس الورقتين، اقرأ الآن من `dev.db`. أعد تشغيل `nexy dev`، وما زالوا هناك.

## ما تعلمته

- SQLModel يصف الجدول كفئة؛ المحرك الموجود في `src/configs/db.py` يفتح قاعدة البيانات.
- `nx migrate` يكتب ويدير الترحيلات: `--init` مرة واحدة، ثم `-m` و `--upgrade` لكل تغيير.
- تستدعي الصفحات ووحدات التحكم وظائف Python عادية تستعلم عن قاعدة البيانات: لا يضيف Nexy أي طبقة.

## الخطوات التالية

- [الجزء السادس: إنشاء ملاحظة من النموذج](create-a-note.md)
- [SQLite](../databases/sqlite.md): البراغماتية والوصول غير المتزامن والاختبارات على قاعدة بيانات في الذاكرة
