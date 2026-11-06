# नेक्सी के साथ SQLite का प्रयोग करें

SQLite वह डेटाबेस है जिसका उपयोग एक नया नेक्सी प्रोजेक्ट तब करता है जब `DATABASE_URL` अनसेट होता है: एक फ़ाइल, कोई सर्वर नहीं, और Python का अपना ड्राइवर, SQLModel, SQLAlchemy या टोर्टोइज़-ओआरएम के माध्यम से।

## जब SQLite फिट बैठता है

- विकास, परीक्षण और डेमो: स्थापित करने या शुरू करने के लिए कुछ भी नहीं।
- एक सर्वर और मामूली लेखन वाली साइट: एक ब्लॉग, एक आंतरिक उपकरण, एक छोटी सी दुकान।
- ऐप के साथ रीड-हैवी डेटा भेजा जाता है।

जब कई सर्वर एक साथ लिखते हैं, या जब आपको बड़े पैमाने पर समृद्ध प्रकार और पूर्ण-पाठ खोज की आवश्यकता होती है, तो [PostgreSQL](postgresql.md) चुनें।

## कनेक्शन स्ट्रिंग

```bash filename=".env"
DATABASE_URL=sqlite:///dev.db
```

| यूआरएल | डेटाबेस |
|---|---|
| `sqlite:///dev.db` | `dev.db`, फ़ोल्डर के सापेक्ष `nx dev` चलता है |
| `sqlite:////var/data/app.db` | एक निरपेक्ष पथ: चार स्लैश |
| `sqlite://` | स्मृति में, प्रक्रिया रुकने पर चला जाता है |
| `sqlite+aiosqlite:///dev.db` | वही फ़ाइल, async ड्राइवर के माध्यम से |

## इंजन

जब आप SQLModel चुनते हैं तो `nx new` यह फ़ाइल लिखता है। SQLite के लिए जोड़ने योग्य एक पंक्ति है `check_same_thread`: एक पृष्ठ और एक हैंडलर विभिन्न थ्रेड से इंजन का उपयोग कर सकते हैं।

```python filename="src/configs/db.py"
import os

from dotenv import load_dotenv
from sqlmodel import create_engine

load_dotenv()

engine = create_engine(
    os.getenv("DATABASE_URL", "sqlite:///dev.db"),
    connect_args={"check_same_thread": False},
)
```

## विदेशी कुंजी और वाल

SQLite प्रति कनेक्शन पूछे जाने तक विदेशी कुंजी लागू नहीं करता है। जब कोई लेखक लिखता है तो वाल मोड पाठकों को आगे बढ़ने देता है। दोनों प्रत्येक नए कनेक्शन पर चलने वाले `PRAGMA` हैं, जो इंजन के बगल में स्थापित किए गए हैं:

```python filename="src/configs/db.py"
import os

from dotenv import load_dotenv
from sqlalchemy import event
from sqlmodel import create_engine

load_dotenv()

engine = create_engine(
    os.getenv("DATABASE_URL", "sqlite:///dev.db"),
    connect_args={"check_same_thread": False},
)


@event.listens_for(engine, "connect")
def set_pragmas(connection, _record) -> None:
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()
```

## एक मॉडल

```python filename="src/models/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    done: bool = False
```

## प्रति अनुरोध एक सत्र

एक निर्भरता अनुरोध के लिए एक सत्र खोलती है और उत्तर के बाद इसे बंद कर देती है:

```python filename="src/configs/session.py"
from collections.abc import Iterator

from sqlmodel import Session

from src.configs.db import engine


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
```

## हैंडलर से पढ़ें और लिखें

```python filename="src/routes/api/notes/index.py"
from pydantic import BaseModel
from sqlmodel import Session, select

from nexy.http import Depends, JSONResponse
from src.configs.session import get_session
from src.models.note_model import Note


class NewNote(BaseModel):
    title: str


async def GET(session: Session = Depends(get_session)):
    return session.exec(select(Note)).all()


async def POST(body: NewNote, session: Session = Depends(get_session)):
    note = Note(title=body.title)
    session.add(note)
    session.commit()
    session.refresh(note)
    return JSONResponse(note.model_dump(), status_code=201)
```

## एक पेज से पढ़ें

एक `.nexy` पेज सर्वर पर अपना फ्रंटमैटर चलाता है, इसलिए यह उसी कोड को कॉल कर सकता है। क्वेरी को किसी फ़ंक्शन में रखें: केवल फ्रंटमैटर के शीर्ष स्तर पर निर्दिष्ट नाम ही टेम्पलेट तक पहुंचते हैं।

```python filename="src/services/notes.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.note_model import Note


def open_notes() -> list[Note]:
    with Session(engine) as session:
        return list(session.exec(select(Note).where(Note.done == False)))  # noqa: E712
```

```nexy filename="src/routes/notes.nexy"
---
from src.services.notes import open_notes

notes = open_notes()
---
<ul>
  {% for note in notes %}
  <li>{{ note.title | e }}</li>
  {% endfor %}
</ul>
```

## माइग्रेशन के साथ तालिकाएँ बनाएँ

```bash
nx migrate --init
nx migrate -m "create notes"
nx migrate --upgrade
```

`--init` लिखता है `alembic/env.py`, जो डेटाबेस के साथ तुलना करने वाले मॉडल को आयात करता है। प्रत्येक नए मॉडल मॉड्यूल को वहां आयात करें:

```python filename="एलेम्बिक/env.py"
import src.models.note_model  # noqa: F401
```

SQLite अधिकांश कॉलमों को `ALTER` जगह पर नहीं रखा जा सकता। Alembic का बैच मोड चालू करें, जो `alembic/env.py` की दोनों `context.configure(...)` कॉलों में तालिका की प्रतिलिपि बनाता है:

```python filename="एलेम्बिक/env.py"
context.configure(connection=connection, target_metadata=target_metadata, render_as_batch=True)
```

## `aiosqlite` के साथ एसिंक

```bash
uv add aiosqlite
```

```python filename="src/configs/async_db.py"
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

async_engine = create_async_engine("sqlite+aiosqlite:///dev.db")


async def get_async_session():
    async with AsyncSession(async_engine) as session:
        yield session
```

```python filename="src/routes/api/notes/count.py"
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from nexy.http import Depends
from src.configs.async_db import get_async_session
from src.models.note_model import Note


async def GET(session: AsyncSession = Depends(get_async_session)):
    count = (await session.exec(select(func.count()).select_from(Note))).one()
    return {"count": count}
```

## इन-मेमोरी डेटाबेस पर परीक्षण

`StaticPool` एक कनेक्शन रखता है, इसलिए इन-मेमोरी डेटाबेस पूरे परीक्षण के लिए रहता है। हैंडलर की निर्भरता को उसका उपयोग करने वाले के लिए बदल दिया जाता है:

```python filename="परीक्षण/test_notes.py"
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from nexy.app import app
from src.configs.session import get_session

test_engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
SQLModel.metadata.create_all(test_engine)


def override_session():
    with Session(test_engine) as session:
        yield session


def test_a_note_is_created():
    app.dependency_overrides[get_session] = override_session
    client = TestClient(app)
    client.post("/api/notes", json={"title": "Write the docs"})
    assert client.get("/api/notes").json()[0]["title"] == "Write the docs"
```

## उत्पादन में

- **फ़ाइल को लगातार डिस्क पर रखें।** एक कंटेनर की अपनी फ़ाइल प्रणाली पुनः तैनात करने पर खो जाती है: एक वॉल्यूम माउंट करें और उस पर एक पूर्ण पथ के साथ `DATABASE_URL` को इंगित करें।
- **एक सर्वर, एक फ़ाइल।** SQLite में एक समय में एक लेखक होता है। एक ही मशीन पर काम करने वाले कई `nx start` कर्मचारी वाल के साथ ठीक हैं; कई मशीनें नहीं हैं.
- **** चलते समय इसका बैकअप `sqlite3 app.db ".backup backup.db"` के साथ रखें, फ़ाइल कॉपी के साथ नहीं।

## अगले चरण

- [डेटाबेस](../guides/databases.md)
- [नेक्सी के साथ PostgreSQL का प्रयोग करें](postgresql.md)
- [परीक्षण](../guides/testing.md)
