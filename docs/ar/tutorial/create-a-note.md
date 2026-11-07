# إنشاء تطبيق ملاحظات باستخدام Nexy، الجزء 6: إنشاء ملاحظة من نموذج

يضيف الجزء 6 نموذجًا أعلى القائمة: فهو يقوم بالنشر إلى وظيفة Python المميزة بـ `@Action`، والتي تحفظ الملاحظة، ويعود الزائر إلى القائمة مع الملاحظة الجديدة بداخلها.

**قبل البدء:** تطبيق [الجزء الخامس](store-the-notes.md) مع قاعدة البيانات الخاصة به.

## حفظ ملاحظة

أضف وظيفة تحفظ ملاحظة واحدة وتعيدها، بجانب الملاحظتين اللتين تقرأانها:

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

## تحويله إلى إجراء

الإجراء هو Python وظيفة يمكن للمتصفح الاتصال بها. `@Action` بمثابة `POST`، ويتحقق من الإدخال مقابل تلميحات الكتابة، ويقوم بتشغيله:

```python filename="src/actions/notes.py"
from nexy.decorators import Action
from src.notes import add_note


@Action
async def create_note(text: str) -> int:
    return add_note(text).id
```

عند بدء التشغيل، يقوم Nexy باستيراد كل وحدة من `src/` ويقدم الإجراءات التي يجدها: لا يوجد طريق للإعلان عنه لأي جهاز توجيه. `src/actions/` هو المكان الذي يحفظهم فيه هذا البرنامج التعليمي.

## أرسل النموذج إليه

يعرف القالب `.nexy` مسار كل إجراء باسم `__actions_path["name"]`. يتم نشر نموذج HTML عادي هناك، بحيث تعمل الصفحة قبل تحميل أي برنامج نصي:

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

يُسمى المُدخل `text`، مثل المعلمة `create_note`: هكذا يصل إليه الحقل.

## إظهار الملاحظة كنص، وليس بتنسيق HTML

من الآن فصاعدا، الملاحظة هي ما يكتبه الزائر. يكتب القالب `.nexy` القيمة كما هي، لذلك سيتم تشغيل الملاحظة `<script>…</script>` في متصفح كل من يفتح القائمة. `| e` يفلت منه: `<` يصبح `&lt;`، وتظهر الملاحظة كنص.

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

الهروب من كل قيمة تأتي من الزائر أو من قاعدة البيانات. `| safe` يفعل العكس: احتفظ به لـ HTML الذي كتبته بنفسك.

## جربه

اكتب *اقرأ المستندات* ثم اضغط على **إضافة**. يحفظ الإجراء الملاحظة، ثم يجيب `303` مرة أخرى على `/notes`، ويعرض المتصفح القائمة مرة أخرى، مع الملاحظة الثالثة في الأسفل.

## ما تعلمته

- `@Action` يحول الدالة Python إلى نقطة نهاية `POST`، مع تلميحات نوعها كمدخل.
- نموذج ينشر إليه عبر `__actions_path["name"]`، بدون JavaScript، ويعود بـ `303`.
- أسماء حقول النموذج هي أسماء معلمات الإجراء.
- `| e` يظهر ما كتبه الزائر كنص: هروب من كل قيمة لم تأت منك.

## الخطوات التالية

- [الجزء السابع: إظهار أخطاء التحقق](validation-errors.md)
- [الإجراءات](../guides/actions.md): المكالمات المكتوبة من المتصفح والأخطاء والأمان
