# إنشاء تطبيق ملاحظات باستخدام Nexy، الجزء 4: المكونات

يحول الجزء الرابع كل ملاحظة إلى مكون قابل لإعادة الاستخدام، وهو ملف `.nexy` تستورده مثل اسم Python وتستخدمه مثل علامة HTML.

**قبل أن تبدأ:** تطبيق [الجزء 3](dynamic-routes.md).

## اكتب المكون

المكون هو ملف `.nexy` خارج المسارات. تُعلن دعائمها بـ `prop[...]`، ويمررها المستدعي كصفات:

```nexy filename="src/components/NoteCard.nexy"
---
id: prop[int]
text: prop[str]
---
<article class="note">
  <a href="/notes/{{ id }}">{{ text }}</a>
</article>

<style>
  .note { padding: 0.75rem 1rem; border: 1px solid #ddd; border-radius: 0.5rem; }
</style>
```

يتم إرسال الكتلة `<style>` مع كل صفحة تستخدم البطاقة. لم يتم تحديد نطاقها: `.note` هي فئة واحدة للصفحة بأكملها، لذا قم بإعطاء فئات أسماء المكونات التي تستخدمها فقط.

## استخدامه في القائمة

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  {% for id, text in notes %}
  <NoteCard id="{{ id }}" text="{{ text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  {% for id, text in notes %}
  <NoteCard id="{{ id }}" text="{{ text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

`@/` هو الاسم المستعار للاستيراد للجزء 1: يشير إلى `src/`. اسم الملف هو اسم المكون، في PascalCase: `NoteCard.nexy` يصدر `NoteCard`.

فتح <http://localhost:3000/notes>: كل ملاحظة أصبحت الآن بطاقة.

## ما تعلمته

- الملف `.nexy` الموجود خارج المسارات هو مكون؛ `prop[...]` هي صفاته.
- `from "@/components/x.nexy" import X` يستورده؛ `<X />` يجعله.
- لم يتم تحديد نطاق الكتلة `<style>`: قم بتسمية فئات المكون بعدها.

## الخطوات التالية

- [الجزء الخامس: تخزين الملاحظات في SQLite](store-the-notes.md)
- [المكونات](../views/nexy/components.md): `Image`، `Link` والمساعدين المدمجين
