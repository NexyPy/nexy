# Nexy کے ساتھ ایک نوٹس ایپ بنائیں، حصہ 4: اجزاء

حصہ 4 ہر نوٹ کو دوبارہ قابل استعمال جزو میں بدل دیتا ہے، ایک `.nexy` فائل جسے آپ Python نام کی طرح درآمد کرتے ہیں اور HTML ٹیگ کی طرح استعمال کرتے ہیں۔

**اس سے پہلے کہ آپ شروع کریں:** [پارٹ 3](dynamic-routes.md) کی ایپ۔

## جز لکھیں۔

ایک جزو راستوں سے باہر ایک `.nexy` فائل ہے۔ اس کے پرپس کا اعلان `prop[...]` کے ساتھ کیا جاتا ہے، اور کال کرنے والا انہیں صفات کے طور پر منتقل کرتا ہے:

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

کارڈ استعمال کرنے والے ہر صفحے کے ساتھ `<style>` بلاک بھیجا جاتا ہے۔ اس کا دائرہ کار نہیں ہے: `.note` پورے صفحے کے لیے ایک کلاس ہے، اس لیے کسی جزو کے ناموں کی کلاسیں دیں جو صرف یہ استعمال کرتا ہے۔

## اسے فہرست میں استعمال کریں۔

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

`@/` حصہ 1 کا درآمدی عرف ہے: یہ `src/` کی طرف اشارہ کرتا ہے۔ فائل کا نام جزو کا نام ہے، پاسکل کیس میں: `NoteCard.nexy` برآمدات `NoteCard`۔

کھولیں <http://localhost:3000/notes>: ہر نوٹ اب ایک کارڈ ہے۔

## جو آپ نے سیکھا۔

- راستوں سے باہر ایک `.nexy` فائل ایک جزو ہے۔ اس کی `prop[...]` صفات ہیں۔
- `from "@/components/x.nexy" import X` اسے درآمد کرتا ہے۔ `<X />` اسے پیش کرتا ہے۔
- ایک `<style>` بلاک کا دائرہ کار نہیں ہے: اس کے بعد کسی جزو کی کلاسز کا نام دیں۔

## اگلے اقدامات

- [حصہ 5: نوٹوں کو SQLite](store-the-notes.md) میں محفوظ کریں
- [اجزاء](../views/nexy/components.md): `Image`، `Link` اور بلٹ ان مددگار
