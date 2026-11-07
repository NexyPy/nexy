# Nexy کے ساتھ ایک نوٹس ایپ بنائیں، حصہ 13: جیسے جیسے آپ ٹائپ کرتے ہیں نوٹس تلاش کریں۔

حصہ 13 نوٹس کے اوپر ایک سرچ باکس کا اضافہ کرتا ہے: ایک React جزیرہ براؤزر میں ہر کلید دبانے پر صارف کے ہر نوٹ کو فلٹر کرتا ہے، سرور سے کوئی درخواست نہیں ہوتی۔

**شروع کرنے سے پہلے:** [پارٹ 12](password-reset.md) کی ایپ۔ پروجیکٹ React کے ساتھ [حصہ 1](create-the-project.md) میں بنایا گیا تھا، اس لیے React پہلے سے ہی انسٹال ہے۔

## ایک جزیرہ، اور یہاں کیوں؟

باقی صفحہ سرور کے ذریعہ پیش کردہ HTML رہتا ہے: فہرست، فارم، نوٹس کے صفحات۔ صرف سرچ باکس کو براؤزر کی ضرورت ہے، اس لیے صرف سرچ باکس React ہے۔ یہ ایک *جزیرہ* ہے: سرور کے صفحے کے اندر ایک کلائنٹ کا جزو، خود ہی انٹرایکٹو بنا۔

## تلاش کا جزو

```tsx filename="src/components/NoteSearch.tsx"
import { useState } from "react"

type Note = { id: number; text: string }

export default function NoteSearch({ notes }: { notes: Note[] }) {
  const [query, setQuery] = useState("")
  const words = query.trim().toLowerCase()
  const found = words ? notes.filter((note) => note.text.toLowerCase().includes(words)) : []
  return (
    <section className="note-search" aria-label="Search the notes">
      <label>
        Search
        <input type="search" value={query} onChange={(event) => setQuery(event.target.value)} />
      </label>
      <div aria-live="polite">
        {words && found.length === 0 && <p>No note matches “{query}”.</p>}
        {found.length > 0 && (
          <ul>
            {found.map((note) => (
              <li key={note.id}>
                <a href={`/notes/${note.id}`}>{note.text}</a>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  )
}
```

React متن کے طور پر `{note.text}` لکھتے ہیں: ایک نوٹ `<b>x</b>` اس کے بریکٹ دکھاتا ہے، جس میں کوئی `| e` شامل نہیں ہوتا۔

`found` کا شمار صرف ایک بار کیا جاتا ہے جب کچھ ٹائپ کیا جاتا ہے، اور یہ تعمیر کے لیے اہمیت رکھتا ہے: `nx build` ہر جزیرے کو ایک بار ایچ ٹی ایم ایل میں پیش کرتا ہے، اس کے پروپس کے بجائے پلیس ہولڈرز کے ساتھ۔ ایک جزو جو اس پہلے رینڈر کے دوران ایک فہرست سہارا پڑھتا ہے اسے فہرست کے بجائے پلیس ہولڈر ملتا ہے، اور کوئی HTML نہیں بھیجتا ہے۔ یہ کلید دبانے کے بعد ہی `notes` پڑھتا ہے، اس لیے بلڈ اپنا سرچ باکس پیش کرتا ہے اور صفحہ کسی بھی JavaScript کے چلنے سے پہلے اسے دکھاتا ہے۔

`aria-live="polite"` اسکرین ریڈر کو بغیر کسی مداخلت کے نتائج پڑھنے پر مجبور کرتا ہے۔

## جزیرے کو صفحہ پر رکھیں

صفحہ نوٹوں کو ایک سہارے کے طور پر پاس کرتا ہے: لغات کی ایک فہرست، جسے Nexy براؤزر کے لیے JSON میں بدل دیتا ہے۔ ہر نوٹ اندر جاتا ہے، نہ صرف موجودہ صفحہ کے پانچ، لہذا تلاش ان سب کا احاطہ کرتی ہے:

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from "@/components/NoteSearch.tsx" import NoteSearch
from nexy import useSearchParams
from src.guard import signed_in_user
from src.notes import all_notes, notes_page

user_id = signed_in_user()
params = useSearchParams()
error = params.get("error", "")
asked = params.get("page", "1")
number = max(int(asked), 1) if asked.isdigit() else 1
found = notes_page(user_id, number)
notes = found[0]
more = found[1]
searchable = [{"id": note.id, "text": note.text} for note in all_notes(user_id)]
---
<section class="app-page">
  <h1>Notes</h1>

  <form method="post" action="{{ __actions_path['sign_out'] }}">
    <button type="submit">Sign out</button>
  </form>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <NoteSearch notes="{{ searchable }}" directive="client:idle" />

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" maxlength="200" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% else %}
  <p>No notes yet: write the first one above.</p>
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
from "@/components/NoteSearch.tsx" import NoteSearch
from nexy import useSearchParams
from src.guard import signed_in_user
from src.notes import all_notes, notes_page

user_id = signed_in_user()
params = useSearchParams()
error = params.get("error", "")
asked = params.get("page", "1")
number = max(int(asked), 1) if asked.isdigit() else 1
found = notes_page(user_id, number)
notes = found[0]
more = found[1]
searchable = [{"id": note.id, "text": note.text} for note in all_notes(user_id)]
---
<section class="app-page">
  <h1>Notes</h1>

  <form method="post" action="{{ __actions_path['sign_out'] }}">
    <button type="submit">Sign out</button>
  </form>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <NoteSearch notes="{{ searchable }}" directive="client:idle" />

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" maxlength="200" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% else %}
  <p>No notes yet: write the first one above.</p>
  {% endfor %}

  <nav class="note-pages" aria-label="Pages of notes">
    {% if number > 1 %}<a href="/notes?page={{ number - 1 }}" rel="prev">Newer</a>{% endif %}
    {% if more %}<a href="/notes?page={{ number + 1 }}" rel="next">Older</a>{% endif %}
  </nav>
</section>
```
<!-- /router -->

`from "@/components/NoteSearch.tsx" import NoteSearch` ایک React جز کو `.nexy` صفحہ میں درآمد کرتا ہے۔ ٹیگ اپنی صفات کو پرپس کے طور پر منتقل کرتا ہے۔ `notes="{{ searchable }}"` خود Python فہرست کو پاس کرتا ہے، کوئی تار نہیں۔ `directive="client:idle"` جزیرے کو ایک بار انٹرایکٹو بنا دیتا ہے جب براؤزر کے پاس کرنے کے لیے کچھ زیادہ ضروری نہیں ہوتا ہے۔

کھولیں <http://localhost:3000/notes> اور نوٹ کے چند حروف ٹائپ کریں: مماثل نوٹ ہر کلید دبانے پر باکس کے نیچے دکھائے جاتے ہیں۔ باکس کو صاف کریں، اور نتائج چلے جائیں گے۔

> [!NOTE]
> صفحہ میں جزیرے کے سفر کے پروپس، JSON کے بطور۔ ہر نوٹ بھیجنا ان میں سے چند سو کے مطابق ہوتا ہے۔ ہزاروں کے لیے، اس کے بجائے سرور پر تلاش کریں، ایک سوال اور `LIKE` فلٹر کے ساتھ۔

## جو آپ نے سیکھا۔

- ایک جزیرہ سرور کے صفحے کے اندر کلائنٹ کا جزو ہوتا ہے: یہاں، React صرف تلاش کے خانے کے لیے۔
- ایک `.nexy` صفحہ اسے راستے سے درآمد کرتا ہے اور Python قدروں کو پروپس کے طور پر، JSON کو سیریلائز کرتا ہے۔
- یہ تعمیر ایک بار جزیرے کو پیش کرتی ہے، اس کے پرپس کے لیے پلیس ہولڈرز کے ساتھ: پہلے رینڈر کے بعد فہرست پرپس پڑھیں، اور جزیرہ HTML بھیجتا ہے۔

## اگلے اقدامات

- [حصہ 14: صفحہ کو دوبارہ لوڈ کیے بغیر نوٹ پر نشان لگائیں](tick-a-note.md)
- [جزائر اور ہائیڈریشن](../rendering/islands.md): ہدایات، سہارے اور حدود
