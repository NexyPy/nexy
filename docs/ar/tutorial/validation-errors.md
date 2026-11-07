# إنشاء تطبيق ملاحظات باستخدام Nexy، الجزء 7: إظهار أخطاء التحقق من الصحة

يرفض الجزء 7 ملاحظة فارغة أو طويلة جدًا، ويوضح السبب أعلى النموذج، في نفس الصفحة، بدون JavaScript.

**قبل أن تبدأ:** تطبيق [الجزء السادس](create-a-note.md).

## نوعان من الأخطاء

ترفض تلميحات النوع الخاصة بالإجراء بالفعل شكلاً خاطئًا: النموذج الذي لا يحتوي على حقل `text` يجيب على `422` قبل تشغيل `create_note`. القاعدة الخاصة بالقيمة نفسها، مثل "ليست فارغة"، هي القاعدة التي يمكنك كتابتها في الإجراء.

## تحقق من الملاحظة في الإجراء

يؤدي الفشل إلى إعادة الزائر إلى القائمة مع ذكر السبب في عنوان URL؛ يعود النجاح إلى القائمة بدونه:

```python filename="src/actions/notes.py"
from urllib.parse import urlencode

from nexy.decorators import Action
from nexy.http import RedirectResponse
from src.notes import add_note

MAX_LENGTH = 200


def back(error: str = "") -> RedirectResponse:
    query = f"?{urlencode({'error': error})}" if error else ""
    return RedirectResponse(f"/notes{query}", status_code=303)


@Action
async def create_note(text: str) -> RedirectResponse:
    text = text.strip()
    if not text:
        return back("A note cannot be blank.")
    if len(text) > MAX_LENGTH:
        return back(f"A note is at most {MAX_LENGTH} characters.")
    add_note(text)
    return back()
```

`303` يخبر المتصفح بتحميل الصفحة التالية بـ `GET`، لذلك لا يؤدي التحديث إلى نشر النموذج مرة أخرى.

## أظهر السبب أعلى النموذج

`useSearchParams()` يقرأ سلسلة الاستعلام للطلب الحالي:

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from nexy import useSearchParams
from src.notes import all_notes

notes = all_notes()
error = useSearchParams().get("error", "")
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
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from nexy import useSearchParams
from src.notes import all_notes

notes = all_notes()
error = useSearchParams().get("error", "")
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
</section>
```
<!-- /router -->

`| e` يفلت من الرسالة: سلسلة الاستعلام تأتي من الزائر، لذلك لا يتم كتابتها أبدًا في الصفحة بتنسيق HTML. `role="alert"` يجعل قارئ الشاشة يعلن ذلك.

`required` و `maxlength` يتيحان للمتصفح إيقاف معظم الأخطاء قبل مغادرتها. يتحقق الإجراء مرة أخرى: ليس من الضروري أن يأتي الطلب من النموذج الخاص بك.

أضف ملاحظة مكونة من ثلاث مسافات: تظهر القائمة مع *لا يمكن أن تكون الملاحظة فارغة.* أعلى النموذج.

## ما تعلمته

- ترفض تلميحات الكتابة الشكل الخاطئ باستخدام `422`؛ القواعد المتعلقة بالقيمة تذهب في الإجراء.
- يمكن للإجراء الإجابة بـ `RedirectResponse`؛ `303` بعد النموذج يتجنب المشاركة الثانية.
- `useSearchParams()` يقرأ سلسلة الاستعلام، ويهرب `| e` مما أرسله الزائر.

## الخطوات التالية

- [الجزء 8: تعديل وحذف ملاحظة](edit-and-delete.md)
- [الاستثناءات والأخطاء](../reference/exceptions.md): كل حالة يمكن للإجراء والصفحة الإجابة عليها
