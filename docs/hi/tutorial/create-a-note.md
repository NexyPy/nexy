# नेक्सी के साथ एक नोट्स ऐप बनाएं, भाग 6: एक फॉर्म से एक नोट बनाएं

भाग 6 सूची के ऊपर एक फॉर्म जोड़ता है: यह `@Action` चिह्नित Python फ़ंक्शन पर पोस्ट करता है, जो नोट को सहेजता है, और विज़िटर नए नोट के साथ सूची में वापस आ जाता है।

**शुरू करने से पहले:** [भाग 5](store-the-notes.md) का ऐप, अपने डेटाबेस के साथ।

## एक नोट सहेजें

एक फ़ंक्शन जोड़ें जो एक नोट को सहेजता है और उसे पढ़ने वाले दो के बगल में लौटाता है:

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

## इसे एक क्रिया में बदलें

एक्शन एक Python फ़ंक्शन है जिसे ब्राउज़र कॉल कर सकता है। `@Action` इसे `POST` के रूप में कार्य करता है, प्रकार संकेतों के विरुद्ध इनपुट की जांच करता है, और इसे चलाता है:

```python filename="src/actions/notes.py"
from nexy.decorators import Action
from src.notes import add_note


@Action
async def create_note(text: str) -> int:
    return add_note(text).id
```

स्टार्टअप पर, नेक्सी `src/` के प्रत्येक मॉड्यूल को आयात करता है और उसे मिलने वाली क्रियाओं को प्रस्तुत करता है: किसी भी राउटर के लिए घोषित करने का कोई मार्ग नहीं है। `src/actions/` वह जगह है जहां यह ट्यूटोरियल उन्हें रखता है।

## इसमें फॉर्म पोस्ट करें

एक `.nexy` टेम्प्लेट प्रत्येक क्रिया के पथ को `__actions_path["name"]` के रूप में जानता है। एक सादा HTML फॉर्म वहां पोस्ट होता है, इसलिए पेज किसी भी स्क्रिप्ट के लोड होने से पहले काम करता है:

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

इनपुट को `text` नाम दिया गया है, `create_note` के पैरामीटर की तरह: इस प्रकार फ़ील्ड उस तक पहुंचता है।

## नोट को टेक्स्ट के रूप में दिखाएँ, HTML के रूप में नहीं

अब से, नोट वह है जो आगंतुक ने टाइप किया है। एक `.nexy` टेम्प्लेट एक मान वैसे ही लिखता है, इसलिए एक नोट `<script>…</script>` सूची खोलने वाले प्रत्येक व्यक्ति के ब्राउज़र में चलेगा। `| e` इससे बच जाता है: `<` `&lt;` बन जाता है, और नोट पाठ के रूप में दिखाई देता है।

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

विज़िटर या डेटाबेस से आने वाले प्रत्येक मान से बचें। `| safe` इसका विपरीत करता है: इसे HTML के लिए रखें जिसे आपने स्वयं लिखा है।

## इसे आज़माएं

*दस्तावेज़ पढ़ें* टाइप करें और **जोड़ें** दबाएँ। एक्शन नोट को सहेजता है, फिर `303` को वापस `/notes` पर उत्तर देता है, और ब्राउज़र नीचे तीसरे नोट के साथ फिर से सूची दिखाता है।

## आपने क्या सीखा

- `@Action` एक Python फ़ंक्शन को `POST` एंडपॉइंट में बदल देता है, इसके प्रकार को इनपुट के रूप में संकेत देता है।
- एक फॉर्म इसे `__actions_path["name"]` के माध्यम से पोस्ट करता है, बिना JavaScript के साथ, और `303` के साथ वापस आता है।
- प्रपत्र के फ़ील्ड नाम क्रिया के पैरामीटर नाम हैं।
- `| e` दिखाता है कि विज़िटर ने टेक्स्ट के रूप में क्या टाइप किया है: हर उस मान से बचें जो आपकी ओर से नहीं आया है।

## अगले चरण

- [भाग 7: सत्यापन त्रुटियां दिखाएं](validation-errors.md)
- [क्रियाएँ](../guides/actions.md): ब्राउज़र से टाइप की गई कॉल, त्रुटियाँ और सुरक्षा
