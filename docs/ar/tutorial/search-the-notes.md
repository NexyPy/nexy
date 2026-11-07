# أنشئ تطبيق ملاحظات باستخدام Nexy، الجزء 13: ابحث في الملاحظات أثناء الكتابة

يضيف الجزء 13 مربع بحث فوق الملاحظات: تقوم جزيرة React بتصفية كل ملاحظة للمستخدم عند كل ضغطة على المفتاح، في المتصفح، دون طلب من الخادم.

**قبل أن تبدأ:** تطبيق [الجزء 12](password-reset.md). تم إنشاء المشروع باستخدام React في [الجزء 1](create-the-project.md)، لذلك تم تثبيت React بالفعل.

## جزيرة، ولماذا هنا

تظل بقية الصفحة بتنسيق HTML مقدمًا بواسطة الخادم: القائمة والنماذج وصفحات الملاحظات. فقط مربع البحث هو الذي يحتاج إلى المتصفح، لذا فإن مربع البحث فقط هو React. هذه عبارة عن *جزيرة*: مكون عميل واحد داخل صفحة خادم، يتم جعله تفاعليًا من تلقاء نفسه.

## مكون البحث

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

React يكتب `{note.text}` نصاً: ملاحظة `<b>x</b>` تظهر بين قوسين، دون `| e` للإضافة.

`found` يتم حسابه فقط بمجرد كتابة شيء ما، وهذا مهم للبناء: `nx build` يعرض كل جزيرة مرة واحدة بتنسيق HTML، مع العناصر النائبة بدلاً من دعائمها. يحصل المكون الذي يقرأ خاصية القائمة أثناء العرض الأول على عنصر نائب بدلاً من القائمة، ولا يشحن HTML. يقرأ هذا `notes` فقط بعد الضغط على المفتاح، لذلك يعرض الإصدار مربع البحث الخاص به وتعرضه الصفحة قبل تشغيل أي JavaScript.

`aria-live="polite"` يجعل قارئ الشاشة يقرأ النتائج عندما تتغير، دون مقاطعة.

## ضع الجزيرة على الصفحة

تقوم الصفحة بتمرير الملاحظات كدعم: قائمة من القواميس، والتي يحولها Nexy إلى JSON للمتصفح. يتم إدخال كل ملاحظة، وليس الخمس فقط في الصفحة الحالية، لذا فإن البحث يغطيها جميعًا:

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

`from "@/components/NoteSearch.tsx" import NoteSearch` يستورد مكون React إلى صفحة `.nexy`؛ تقوم العلامة بتمرير سماتها كدعائم. `notes="{{ searchable }}"` يمرر القائمة Python نفسها، وليس سلسلة. `directive="client:idle"` يجعل الجزيرة تفاعلية بمجرد أن لا يكون لدى المتصفح أي شيء أكثر إلحاحًا للقيام به.

افتح <http://localhost:3000/notes> واكتب بضعة أحرف من الملاحظة: تظهر الملاحظات المطابقة أسفل المربع عند كل ضغطة على المفتاح. قم بمسح الصندوق، وستختفي النتائج.

> [!NOTE]
> الدعائم الخاصة بالجزيرة تسافر في الصفحة، مثل JSON. إرسال كل ملاحظة يناسب بضع مئات منهم؛ للآلاف، ابحث على الخادم بدلاً من ذلك، باستخدام استعلام ومرشح `LIKE`.

## ما تعلمته

- الجزيرة هي مكون عميل داخل صفحة الخادم: هنا، React لمربع البحث فقط.
- تقوم صفحة `.nexy` باستيرادها عن طريق المسار وتمرير قيم Python كدعائم، متسلسلة إلى JSON.
- يعرض البناء جزيرة مرة واحدة، مع عناصر نائبة لدعائمها: قراءة دعائم القائمة بعد العرض الأول، وتشحن الجزيرة HTML.

## الخطوات التالية

- [الجزء 14: ضع علامة على الملاحظة دون إعادة تحميل الصفحة](tick-a-note.md)
- [الجزر والماء](../rendering/islands.md): التوجيهات والدعائم والقيود
