# नेक्सी के साथ एक नोट्स ऐप बनाएं, भाग 13: जैसे ही आप टाइप करें नोट्स खोजें

भाग 13 नोट्स के ऊपर एक खोज बॉक्स जोड़ता है: एक React द्वीप ब्राउज़र में, सर्वर से बिना किसी अनुरोध के, प्रत्येक कुंजी दबाने पर उपयोगकर्ता के प्रत्येक नोट को फ़िल्टर करता है।

**शुरू करने से पहले:** [भाग 12](password-reset.md) का ऐप। प्रोजेक्ट React के साथ [भाग 1](create-the-project.md) में बनाया गया था, इसलिए React पहले से ही इंस्टॉल है।

## एक द्वीप, और यहाँ क्यों

शेष पृष्ठ सर्वर द्वारा प्रस्तुत HTML रहता है: सूची, प्रपत्र, नोट्स के पृष्ठ। केवल खोज बॉक्स को ब्राउज़र की आवश्यकता है, इसलिए केवल खोज बॉक्स React है। वह एक *द्वीप* है: एक सर्वर पेज के अंदर एक क्लाइंट घटक, जो अपने आप ही इंटरैक्टिव बन जाता है।

## खोज घटक

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

React `{note.text}` को पाठ के रूप में लिखता है: एक नोट `<b>x</b>` अपने कोष्ठक दिखाता है, जिसमें जोड़ने के लिए कोई `| e` नहीं है।

`found` की गणना केवल तभी की जाती है जब कुछ टाइप किया जाता है, और यह निर्माण के लिए मायने रखता है: `nx build` प्रत्येक द्वीप को एक बार HTML में प्रस्तुत करता है, इसके प्रॉप्स के बजाय प्लेसहोल्डर के साथ। एक घटक जो उस पहले रेंडर के दौरान एक सूची प्रोप को पढ़ता है, उसे सूची के बजाय एक प्लेसहोल्डर मिलता है, और कोई HTML नहीं भेजता है। यह केवल एक कुंजी दबाने के बाद ही `notes` पढ़ता है, इसलिए बिल्ड अपने खोज बॉक्स को प्रस्तुत करता है और पृष्ठ इसे किसी भी JavaScript चलने से पहले दिखाता है।

`aria-live="polite"` जब परिणाम बदलते हैं तो स्क्रीन रीडर उन्हें बिना किसी रुकावट के पढ़ता है।

## द्वीप को पृष्ठ पर रखें

पेज नोट्स को एक प्रोप के रूप में पास करता है: शब्दकोशों की एक सूची, जिसे नेक्सी ब्राउज़र के लिए JSON में बदल देता है। प्रत्येक नोट अंदर जाता है, न केवल वर्तमान पृष्ठ के पांच, इसलिए खोज उन सभी को कवर करती है:

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

`from "@/components/NoteSearch.tsx" import NoteSearch` एक React घटक को `.nexy` पृष्ठ में आयात करता है; टैग अपनी विशेषताओं को प्रॉप्स के रूप में पास करता है। `notes="{{ searchable }}"` Python सूची को ही पास करता है, किसी स्ट्रिंग को नहीं। `directive="client:idle"` जब ब्राउज़र के पास करने के लिए अधिक जरूरी कुछ नहीं होता है तो यह द्वीप को इंटरैक्टिव बना देता है।

<http://localhost:3000/notes> खोलें और एक नोट के कुछ अक्षर टाइप करें: प्रत्येक कुंजी दबाने पर मेल खाने वाले नोट बॉक्स के नीचे दिखाई देते हैं। बॉक्स साफ़ करें, और परिणाम चले जाएंगे।

> [!NOTE]
> किसी द्वीप के प्रॉप्स पृष्ठ में JSON के रूप में यात्रा करते हैं। प्रत्येक नोट भेजना उनमें से कुछ सौ को शोभा देता है; हजारों लोगों के लिए, इसके बजाय, एक क्वेरी और एक `LIKE` फ़िल्टर के साथ सर्वर पर खोजें।

## आपने क्या सीखा

- एक द्वीप एक सर्वर पेज के अंदर एक क्लाइंट घटक है: यहां, React केवल खोज बॉक्स के लिए।
- एक `.nexy` पृष्ठ इसे पथ द्वारा आयात करता है और Python मानों को JSON में क्रमबद्ध करके प्रॉप्स के रूप में पास करता है।
- बिल्ड एक द्वीप को एक बार प्रस्तुत करता है, इसके प्रॉप्स के लिए प्लेसहोल्डर्स के साथ: पहले रेंडर के बाद सूची प्रॉप्स पढ़ें, और द्वीप HTML भेजता है।

## अगले चरण

- [भाग 14: पृष्ठ को पुनः लोड किए बिना नोट पर टिक करें](tick-a-note.md)
- [द्वीप और जलयोजन](../rendering/islands.md): निर्देश, सहारा और सीमाएँ
