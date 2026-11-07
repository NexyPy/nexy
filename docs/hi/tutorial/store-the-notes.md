# नेक्सी के साथ एक नोट्स ऐप बनाएं, भाग 5: नोट्स को SQLite में संग्रहीत करें

भाग 5 नोट्स को Python शब्दकोश से SQLite डेटाबेस में ले जाता है, जिसमें एक मॉडल, एक माइग्रेशन और शुरू करने के लिए दो नोट्स होते हैं, और पेज उन्हें वहां से पढ़ते हैं।

**शुरू करने से पहले:** [भाग 4](components.md) का ऐप।

## ORM और माइग्रेशन टूल इंस्टॉल करें

```bash
uv add sqlmodel alembic
```

[SQLModel](https://sqlmodel.tiangolo.com/) एक तालिका को Python वर्ग के रूप में वर्णित करता है, और Alembic उन वर्गों में परिवर्तनों को माइग्रेशन में बदल देता है। नेक्सी भी लपेटता नहीं है: आप उन्हें वैसे ही उपयोग करते हैं जैसे वे हैं।

## डेटाबेस खोलें

डेटाबेस का पता प्रोजेक्ट के मूल में `.env` में जाता है। `nx migrate` और ऐप दोनों ने इसे वहां से पढ़ा:

```bash filename=".env"
DATABASE_URL=sqlite:///dev.db
```

`sqlite:///dev.db` एक फ़ाइल है, `dev.db`, `nexyconfig.py` के बगल में: SQLite को किसी सर्वर की आवश्यकता नहीं है। `.env` को Git से बाहर रखें: इसमें वास्तविक डेटाबेस के रहस्य मौजूद हैं।

इंजन डेटाबेस से कनेक्शन है. यह `DATABASE_URL` पढ़ता है, जब वेरिएबल अनसेट होता है तो डिफ़ॉल्ट फ़ाइल उसी फ़ाइल के साथ होती है:

```python filename="src/configs/db.py"
import os

from dotenv import load_dotenv
from sqlmodel import create_engine

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL", "sqlite:///dev.db"))
```

## एक नोट का वर्णन करें

<!-- router:fbr,custom -->
```python filename="src/models/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
```
<!-- /router -->

<!-- router:modular -->
मॉडल अपने नियंत्रक के बगल में उस सुविधा के साथ रहता है जिससे वह संबंधित है:

```python filename="src/apps/notes/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
```
<!-- /router -->

`table=True` कक्षा को एक तालिका बनाता है, `note`। जब कोई नोट सहेजा जाता है तो `id` डेटाबेस द्वारा दिया जाता है।

## माइग्रेशन के साथ तालिका बनाएं

```bash
nx migrate --init
nx migrate -m "create notes"
nx migrate --upgrade
```

`--init` `alembic/` फ़ोल्डर लिखता है और इसे आपके मॉडल पर इंगित करता है। `-m` मॉडल की तुलना डेटाबेस से करता है और माइग्रेशन लिखता है जिससे तालिका बनती है; `--upgrade` इसे चलाता है। मॉडल को बाद में बदलें, अंतिम दो कमांड फिर से चलाएँ, और तालिका इस प्रकार है।

## डेटाबेस से नोट्स पढ़ें

`src/notes.py` के फ़ंक्शन अपने नाम रखते हैं, इसलिए पृष्ठ थोड़े बदलते हैं: वे अब एक सत्र खोलते हैं, तालिका से पूछताछ करते हैं, और स्ट्रिंग के बजाय `Note` ऑब्जेक्ट लौटाते हैं।

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
```
<!-- /router -->

## आरंभ करने के लिए दो नोट जोड़ें

एक बीज स्क्रिप्ट एक खाली डेटाबेस भरती है, इसलिए प्रोजेक्ट की प्रत्येक नई प्रतिलिपि दिखाने के लिए कुछ के साथ शुरू होती है:

<!-- router:fbr,custom -->
```python filename="src/seed.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.note_model import Note


def seed() -> None:
    with Session(engine) as session:
        if session.exec(select(Note)).first() is None:
            session.add_all([Note(text="Buy milk"), Note(text="Ship Nexy")])
            session.commit()


if __name__ == "__main__":
    seed()
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/seed.py"
from sqlmodel import Session, select

from src.apps.notes.note_model import Note
from src.configs.db import engine


def seed() -> None:
    with Session(engine) as session:
        if session.exec(select(Note)).first() is None:
            session.add_all([Note(text="Buy milk"), Note(text="Ship Nexy")])
            session.commit()


if __name__ == "__main__":
    seed()
```
<!-- /router -->

```bash
python -m src.seed
```

स्टार्टअप पर, नेक्सी `src/` के प्रत्येक मॉड्यूल को [भाग 6](create-a-note.md) की कार्रवाइयों को खोजने के लिए आयात करता है। `if __name__ == "__main__":` उपरोक्त कमांड के लिए बीज रखता है: ऐप द्वारा आयातित, फ़ाइल केवल `seed` को परिभाषित करती है, और कुछ भी नहीं छूती है।

## डेटाबेस से नोट्स दिखाएँ

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import all_notes

notes = all_notes()
---
<section class="app-page">
  <h1>Notes</h1>
  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}
</section>
```

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
  <h1>{{ note.text }}</h1>
  <a href="/notes">All notes</a>
</section>
```

```python filename="src/routes/api/notes.py"
from src.notes import all_notes


async def GET():
    return [note.model_dump() for note in all_notes()]
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
  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}
</section>
```

```python filename="src/apps/notes/notes_controller.py"
from nexy import notFound
from nexy.decorators import Controller
from nexy.hooks import useViews
from src.notes import all_notes, find

LAYOUT = "src/apps/layout.nexy"


def page(view: str, **context: object):
    return useViews(LAYOUT, context={"children": useViews(view, context=context)})


@Controller("/notes")
class NotesController:
    async def get(self):
        return page("src/apps/notes/notes_view.nexy")


@Controller("/notes/{id}")
class NoteController:
    async def get(self, id: int):
        note = find(id)
        if note is None:
            notFound()
        return page("src/apps/notes/note_view.nexy", text=note.text)


@Controller("/api/notes")
class NotesApiController:
    async def get(self) -> list[dict]:
        return [note.model_dump() for note in all_notes()]
```
<!-- /router -->

<http://localhost:3000/notes> खोलें: वही दो कार्ड, अब `dev.db` से पढ़ें। पुनः आरंभ करें `nexy dev`, और वे अभी भी वहीं हैं।

## आपने क्या सीखा

- SQLModel एक तालिका को एक वर्ग के रूप में वर्णित करता है; `src/configs/db.py` में इंजन डेटाबेस खोलता है।
- `nx migrate` माइग्रेशन लिखता और चलाता है: `--init` एक बार, फिर `-m` और `--upgrade` प्रति परिवर्तन।
- पेज और नियंत्रक सादे Python फ़ंक्शंस को कॉल करते हैं जो डेटाबेस को क्वेरी करते हैं: नेक्सी कोई परत नहीं जोड़ता है।

## अगले चरण

- [भाग 6: एक फॉर्म से एक नोट बनाएं](create-a-note.md)
- [SQLite](../databases/sqlite.md): इन-मेमोरी डेटाबेस पर प्रैग्मा, एसिंक एक्सेस और परीक्षण
