# नेक्सी के साथ एक नोट्स ऐप बनाएं, भाग 9: नोट्स को पृष्ठांकित करें

भाग 9 एक समय में पांच नोट्स दिखाता है, अगले और पिछले पृष्ठों के लिंक के साथ, यूआरएल के `page` से पढ़ा जाता है: `/notes?page=2`।

**शुरू करने से पहले:** [भाग 8](edit-and-delete.md) का ऐप।

## एक पेज के लिए डेटाबेस से पूछें

`OFFSET` पहले के पन्नों के नोट्स को छोड़ देता है, `LIMIT` पांच को छोड़ देता है। पांच से अधिक एक के लिए पूछना, निःशुल्क बताता है कि अगला पृष्ठ मौजूद है या नहीं:

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


def change_note(note_id: int, text: str) -> bool:
    with Session(engine) as session:
        note = session.get(Note, note_id)
        if note is None:
            return False
        note.text = text
        session.commit()
    return True


def remove_note(note_id: int) -> bool:
    with Session(engine) as session:
        note = session.get(Note, note_id)
        if note is None:
            return False
        session.delete(note)
        session.commit()
    return True


PAGE_SIZE = 5


def notes_page(number: int) -> tuple[list[Note], bool]:
    """One page of notes, oldest first, and whether a page comes after it."""
    with Session(engine) as session:
        query = select(Note).order_by(Note.id).offset((number - 1) * PAGE_SIZE).limit(PAGE_SIZE + 1)
        found = list(session.exec(query))
    return found[:PAGE_SIZE], len(found) > PAGE_SIZE
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


def change_note(note_id: int, text: str) -> bool:
    with Session(engine) as session:
        note = session.get(Note, note_id)
        if note is None:
            return False
        note.text = text
        session.commit()
    return True


def remove_note(note_id: int) -> bool:
    with Session(engine) as session:
        note = session.get(Note, note_id)
        if note is None:
            return False
        session.delete(note)
        session.commit()
    return True


PAGE_SIZE = 5


def notes_page(number: int) -> tuple[list[Note], bool]:
    """One page of notes, oldest first, and whether a page comes after it."""
    with Session(engine) as session:
        query = select(Note).order_by(Note.id).offset((number - 1) * PAGE_SIZE).limit(PAGE_SIZE + 1)
        found = list(session.exec(query))
    return found[:PAGE_SIZE], len(found) > PAGE_SIZE
```
<!-- /router -->

## यूआरएल से पेज नंबर पढ़ें

क्वेरी स्ट्रिंग का `page` विज़िटर द्वारा भेजा गया पाठ है: कोई भी चीज़ जो सकारात्मक संख्या नहीं है वह पहले पृष्ठ पर वापस आ जाती है, इसलिए `/notes?page=abc` अभी भी उत्तर देता है।

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from nexy import useSearchParams
from src.notes import notes_page

params = useSearchParams()
error = params.get("error", "")
asked = params.get("page", "1")
number = max(int(asked), 1) if asked.isdigit() else 1
found = notes_page(number)
notes = found[0]
more = found[1]
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
from nexy import useSearchParams
from src.notes import notes_page

params = useSearchParams()
error = params.get("error", "")
asked = params.get("page", "1")
number = max(int(asked), 1) if asked.isdigit() else 1
found = notes_page(number)
notes = found[0]
more = found[1]
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

  <nav class="note-pages" aria-label="Pages of notes">
    {% if number > 1 %}<a href="/notes?page={{ number - 1 }}" rel="prev">Newer</a>{% endif %}
    {% if more %}<a href="/notes?page={{ number + 1 }}" rel="next">Older</a>{% endif %}
  </nav>
</section>
```
<!-- /router -->

`rel="prev"` और `rel="next"` ब्राउज़रों और खोज इंजनों को बताते हैं कि पेज एक-दूसरे का अनुसरण कैसे करते हैं, और `aria-label` स्क्रीन रीडर के लिए लिंक को नाम देते हैं।

जब तक पाँच से अधिक न हो जाएँ तब तक नोट जोड़ें: सूची पाँच पर रुकती है, एक **पुराना** लिंक के साथ। यह `/notes?page=2` की ओर ले जाता है, जिसमें एक **नया** लिंक है।

## आपने क्या सीखा

- `offset` और `limit` एक पृष्ठ पढ़ें; एक पंक्ति और माँगने से पता चलता है कि क्या कोई अन्य पृष्ठ अनुसरण करता है।
- `useSearchParams()` पढ़ता है `?page=`; उपयोग करने से पहले विज़िटर से प्राप्त मूल्य की जाँच की जाती है।
- `rel="prev"` और `rel="next"` ब्राउज़र, क्रॉलर और स्क्रीन रीडर के लिए पेजों को लिंक करते हैं।

## अगले चरण

- [इकाई 3, भाग 10: एक खाता बनाएं और साइन इन करें](accounts.md)
- [SQLite](../databases/sqlite.md): इन-मेमोरी डेटाबेस पर इंडेक्स, प्रैग्मा और परीक्षण
