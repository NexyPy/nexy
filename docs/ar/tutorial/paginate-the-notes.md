# أنشئ تطبيقًا للملاحظات باستخدام Nexy، الجزء 9: ترقيم الصفحات للملاحظات

يعرض الجزء 9 الملاحظات خمس مرات في كل مرة، مع روابط إلى الصفحات التالية والسابقة، مقروءة من `page` من عنوان URL: `/notes?page=2`.

**قبل أن تبدأ:** تطبيق [الجزء الثامن](edit-and-delete.md).

## اطلب من قاعدة البيانات صفحة واحدة

`OFFSET` يتخطى ملاحظات الصفحات التي قبلها، `LIMIT` يبقي خمسًا. إن طلب أكثر من خمس معلومات مجانًا يوضح ما إذا كانت الصفحة التالية موجودة أم لا:

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


def add_note(text: str) -> Note:
    note = Note(text=text)
    with Session(engine) as session:
        session.add(note)
        session.commit()
        session.refresh(note)
    return note


def change_note(note_id: int, text: str) -> bool:
    with Session(engine) as session:
        note = session.get(Note, note_id)
        if note is None:
            return False
        note.text = text
        session.commit()
    return True


def remove_note(note_id: int) -> bool:
    with Session(engine) as session:
        note = session.get(Note, note_id)
        if note is None:
            return False
        session.delete(note)
        session.commit()
    return True


PAGE_SIZE = 5


def notes_page(number: int) -> tuple[list[Note], bool]:
    """One page of notes, oldest first, and whether a page comes after it."""
    with Session(engine) as session:
        query = select(Note).order_by(Note.id).offset((number - 1) * PAGE_SIZE).limit(PAGE_SIZE + 1)
        found = list(session.exec(query))
    return found[:PAGE_SIZE], len(found) > PAGE_SIZE
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


def add_note(text: str) -> Note:
    note = Note(text=text)
    with Session(engine) as session:
        session.add(note)
        session.commit()
        session.refresh(note)
    return note


def change_note(note_id: int, text: str) -> bool:
    with Session(engine) as session:
        note = session.get(Note, note_id)
        if note is None:
            return False
        note.text = text
        session.commit()
    return True


def remove_note(note_id: int) -> bool:
    with Session(engine) as session:
        note = session.get(Note, note_id)
        if note is None:
            return False
        session.delete(note)
        session.commit()
    return True


PAGE_SIZE = 5


def notes_page(number: int) -> tuple[list[Note], bool]:
    """One page of notes, oldest first, and whether a page comes after it."""
    with Session(engine) as session:
        query = select(Note).order_by(Note.id).offset((number - 1) * PAGE_SIZE).limit(PAGE_SIZE + 1)
        found = list(session.exec(query))
    return found[:PAGE_SIZE], len(found) > PAGE_SIZE
```
<!-- /router -->

## اقرأ رقم الصفحة من عنوان URL

`page` من سلسلة الاستعلام عبارة عن نص يرسله الزائر: أي شيء ليس رقمًا موجبًا يعود إلى الصفحة الأولى، لذلك لا يزال `/notes?page=abc` يجيب.

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from nexy import useSearchParams
from src.notes import notes_page

params = useSearchParams()
error = params.get("error", "")
asked = params.get("page", "1")
number = max(int(asked), 1) if asked.isdigit() else 1
found = notes_page(number)
notes = found[0]
more = found[1]
---
<section class="app-page">
  <h1>Notes</h1>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" maxlength="200" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}

  <nav class="note-pages" aria-label="Pages of notes">
    {% if number > 1 %}<a href="/notes?page={{ number - 1 }}" rel="prev">Newer</a>{% endif %}
    {% if more %}<a href="/notes?page={{ number + 1 }}" rel="next">Older</a>{% endif %}
  </nav>
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from nexy import useSearchParams
from src.notes import notes_page

params = useSearchParams()
error = params.get("error", "")
asked = params.get("page", "1")
number = max(int(asked), 1) if asked.isdigit() else 1
found = notes_page(number)
notes = found[0]
more = found[1]
---
<section class="app-page">
  <h1>Notes</h1>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" maxlength="200" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}

  <nav class="note-pages" aria-label="Pages of notes">
    {% if number > 1 %}<a href="/notes?page={{ number - 1 }}" rel="prev">Newer</a>{% endif %}
    {% if more %}<a href="/notes?page={{ number + 1 }}" rel="next">Older</a>{% endif %}
  </nav>
</section>
```
<!-- /router -->

`rel="prev"` و `rel="next"` يخبران المتصفحات ومحركات البحث بكيفية متابعة الصفحات لبعضها البعض، ويقوم `aria-label` بتسمية الروابط الخاصة بقارئ الشاشة.

أضف ملاحظات حتى يكون هناك أكثر من خمس: القائمة تتوقف عند خمسة، مع رابط **أقدم**. إنه يؤدي إلى `/notes?page=2`، الذي يحتوي على رابط **أحدث** مرة أخرى.

## ما تعلمته

- `offset` و `limit` يقرأان صفحة واحدة؛ إن طلب صف واحد إضافي يشير إلى ما إذا كانت هناك صفحة أخرى تتبعه.
- `useSearchParams()` يقرأ `?page=`؛ يتم فحص القيمة من الزائر قبل استخدامها.
- `rel="prev"` و `rel="next"` يربطان الصفحات الخاصة بالمتصفحات والزواحف وقارئات الشاشة.

## الخطوات التالية

- [الوحدة 3، الجزء 10: إنشاء حساب وتسجيل الدخول](accounts.md)
- [SQLite](../databases/sqlite.md): الفهارس والبراغمات والاختبارات على قاعدة بيانات في الذاكرة
