# Nexy کے ساتھ ایک نوٹس ایپ بنائیں، حصہ 6: فارم سے ایک نوٹ بنائیں

حصہ 6 فہرست کے اوپر ایک فارم شامل کرتا ہے: یہ نشان زدہ Python فنکشن میں پوسٹ کرتا ہے۔ `@Action`، جو نوٹ کو محفوظ کر لیتا ہے، اور وزیٹر اس میں نئے نوٹ کے ساتھ واپس آ جاتا ہے۔

**اس سے پہلے کہ آپ شروع کریں:** [پارٹ 5](store-the-notes.md) کی ایپ، اس کے ڈیٹا بیس کے ساتھ۔

## ایک نوٹ محفوظ کریں۔

ایک فنکشن شامل کریں جو ایک نوٹ کو محفوظ کرتا ہے اور اسے واپس کرتا ہے، ان دو کے آگے جو انہیں پڑھتے ہیں:

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
```
<!-- /router -->

## اسے ایکشن میں تبدیل کریں۔

ایکشن ایک Python فنکشن ہے جسے براؤزر کال کر سکتا ہے۔ `@Action` اسے `POST` کے طور پر کام کرتا ہے، قسم کے اشارے کے خلاف ان پٹ کو چیک کرتا ہے، اور اسے چلاتا ہے:

```python filename="src/actions/notes.py"
from nexy.decorators import Action
from src.notes import add_note


@Action
async def create_note(text: str) -> int:
    return add_note(text).id
```

اسٹارٹ اپ پر، Nexy `src/` کے ہر ماڈیول کو درآمد کرتا ہے اور اسے ملنے والی کارروائیوں کو پیش کرتا ہے: کسی بھی روٹر کے لیے اعلان کرنے کا کوئی راستہ نہیں ہے۔ `src/actions/` وہ جگہ ہے جہاں یہ ٹیوٹوریل انہیں رکھتا ہے۔

## اس پر فارم پوسٹ کریں۔

ایک `.nexy` ٹیمپلیٹ ہر عمل کے راستے کو `__actions_path["name"]` کے طور پر جانتا ہے۔ ایک سادہ HTML فارم وہاں پوسٹ کرتا ہے، لہذا صفحہ کسی بھی اسکرپٹ کے لوڈ ہونے سے پہلے کام کرتا ہے:

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import all_notes

notes = all_notes()
---
<section class="app-page">
  <h1>Notes</h1>

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}
</section>
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

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

ان پٹ کا نام `text` رکھا گیا ہے، جیسا کہ `create_note` کے پیرامیٹر: اس طرح فیلڈ اس تک پہنچتی ہے۔

## ایک نوٹ کو متن کے طور پر دکھائیں، HTML کے طور پر نہیں۔

اب سے، ایک نوٹ وہی ہے جو وزیٹر ٹائپ کرتا ہے۔ ایک `.nexy` ٹیمپلیٹ ایک قدر لکھتا ہے جیسا کہ یہ ہے، لہذا فہرست کو کھولنے والے ہر شخص کے براؤزر میں ایک نوٹ `<script>…</script>` چلے گا۔ `| e` اس سے بچ جاتا ہے: `<` بن جاتا ہے `&lt;`، اور نوٹ متن کے طور پر ظاہر ہوتا ہے۔

```nexy filename="src/components/NoteCard.nexy"
---
id: prop[int]
text: prop[str]
---
<article class="note">
  <a href="/notes/{{ id }}">{{ text | e }}</a>
</article>

<style>
  .note { padding: 0.75rem 1rem; border: 1px solid #ddd; border-radius: 0.5rem; }
</style>
```

<!-- router:fbr,custom -->
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
  <h1>{{ note.text | e }}</h1>
  <a href="/notes">All notes</a>
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/note_view.nexy"
---
text: prop[str]
---
<section class="app-page">
  <h1>{{ text | e }}</h1>
  <a href="/notes">All notes</a>
</section>
```
<!-- /router -->

وزیٹر یا ڈیٹا بیس سے آنے والی ہر قدر سے بچیں۔ `| safe` اس کے برعکس کرتا ہے: اسے HTML کے لیے رکھیں جو آپ نے خود لکھا ہے۔

## اسے آزمائیں

*دستاویزات پڑھیں* ٹائپ کریں اور دبائیں **شامل کریں**۔ ایکشن نوٹ کو محفوظ کرتا ہے، پھر جواب `303` واپس `/notes` پر دیتا ہے، اور براؤزر فہرست کو دوبارہ دکھاتا ہے، نیچے تیسرے نوٹ کے ساتھ۔

## جو آپ نے سیکھا۔

- `@Action` ایک Python فنکشن کو `POST` اینڈ پوائنٹ میں بدل دیتا ہے، اس کے ٹائپ کے اشارے ان پٹ کے طور پر ہوتے ہیں۔
- ایک فارم اسے `__actions_path["name"]` کے ذریعے پوسٹ کرتا ہے، بغیر JavaScript کے، اور `303` کے ساتھ واپس آتا ہے۔
- فارم کے فیلڈ کے نام ایکشن کے پیرامیٹر کے نام ہیں۔
- `| e` ظاہر کرتا ہے کہ وزیٹر نے متن کے طور پر کیا ٹائپ کیا: ہر اس قدر سے بچیں جو آپ کی طرف سے نہیں آئی ہے۔

## اگلے اقدامات

- [حصہ 7: توثیق کی غلطیاں دکھائیں](validation-errors.md)
- [اعمال](../guides/actions.md): براؤزر سے ٹائپ شدہ کالیں، غلطیاں اور سیکیورٹی
