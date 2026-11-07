# Nexy کے ساتھ ایک نوٹس ایپ بنائیں، حصہ 7: توثیق کی غلطیاں دکھائیں۔

حصہ 7 ایک ایسے نوٹ سے انکار کرتا ہے جو خالی یا بہت لمبا ہے، اور ظاہر کرتا ہے کہ فارم کے اوپر، اسی صفحہ پر، پھر بھی JavaScript کے بغیر۔

**شروع کرنے سے پہلے:** [حصہ 6](create-a-note.md) کی ایپ۔

## دو قسم کی غلطیاں

ایکشن کے قسم کے اشارے پہلے ہی غلط شکل سے انکار کرتے ہیں: `create_note` چلنے سے پہلے `text` فیلڈ کے جوابات `422` کے بغیر ایک فارم۔ قدر کے بارے میں ایک اصول، جیسے کہ "خالی نہیں"، آپ کو ایکشن میں لکھنا ہے۔

## ایکشن میں نوٹ چیک کریں۔

ناکامی وزیٹر کو URL میں وجہ کے ساتھ فہرست میں واپس بھیج دیتی ہے۔ کامیابی اس کے بغیر فہرست میں واپس آتی ہے:

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

`303` براؤزر کو اگلے صفحہ کو `GET` کے ساتھ لوڈ کرنے کو کہتا ہے، اس لیے ریفریش فارم کو دوسری بار پوسٹ نہیں کرتا ہے۔

## فارم کے اوپر وجہ دکھائیں۔

`useSearchParams()` موجودہ درخواست کی استفسار کی تار پڑھتا ہے:

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

`| e` پیغام سے بچ جاتا ہے: استفسار کی تار وزیٹر کی طرف سے آتی ہے، اس لیے اسے صفحہ میں HTML کے طور پر کبھی نہیں لکھا جاتا۔ `role="alert"` اسکرین ریڈر کو اس کا اعلان کرتا ہے۔

`required` اور `maxlength` براؤزر کو زیادہ تر غلطیوں کو چھوڑنے سے پہلے روکنے دیں۔ ایکشن دوبارہ چیک کرتا ہے: درخواست آپ کے فارم سے آنی ضروری نہیں ہے۔

تین خالی جگہوں کا ایک نوٹ شامل کریں: فہرست فارم کے اوپر *ایک نوٹ خالی نہیں ہوسکتا۔* کے ساتھ واپس آتی ہے۔

## جو آپ نے سیکھا۔

- قسم کے اشارے `422` کے ساتھ غلط شکل سے انکار کرتے ہیں۔ قدر کے بارے میں اصول ایکشن میں ہیں۔
- ایک عمل `RedirectResponse` کے ساتھ جواب دے سکتا ہے۔ `303` ایک فارم کے بعد دوسری پوسٹ سے گریز کرتا ہے۔
- `useSearchParams()` سوال کی تار پڑھتا ہے، اور `| e` اس سے بچ جاتا ہے جو وزیٹر نے بھیجا تھا۔

## اگلے اقدامات

- [حصہ 8: ایک نوٹ میں ترمیم اور حذف کریں](edit-and-delete.md)
- [مستثنیات اور غلطیاں](../reference/exceptions.md): ہر اسٹیٹس ایک ایکشن اور ایک صفحہ جواب دے سکتا ہے۔
