# नेक्सी के साथ एक नोट्स ऐप बनाएं, भाग 3: गतिशील मार्ग और एक एपीआई

भाग 3 प्रत्येक नोट को अपना स्वयं का URL, `/notes/1` देता है, और `/api/notes` पर JSON के समान नोट्स प्रस्तुत करता है, दोनों एक Python मॉड्यूल से पढ़े जाते हैं।

**शुरू करने से पहले:** [भाग 2](pages-and-layouts.md) का ऐप।

## नोट्स को एक मॉड्यूल में रखें

पेज और एपीआई एक ही सूची पढ़ेंगे। इसे अपने स्वयं के एक मॉड्यूल में ले जाएं, एक फ़ंक्शन के साथ जो एक नोट ढूंढता है:

```python filename="src/notes.py"
NOTES = {1: "Buy milk", 2: "Ship Nexy"}


def find(note_id: int) -> str | None:
    return NOTES.get(note_id)
```

## प्रत्येक नोट को उसके पृष्ठ से लिंक करें

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
---
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for id, text in notes %}
    <li><a href="/notes/{{ id }}">{{ text }}</a></li>
    {% endfor %}
  </ul>
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for id, text in notes %}
    <li><a href="/notes/{{ id }}">{{ text }}</a></li>
    {% endfor %}
  </ul>
</section>
```
<!-- /router -->

## प्रति नोट एक पृष्ठ जोड़ें

<!-- router:fbr,custom -->
कोष्ठक में एक फ़ोल्डर या फ़ाइल नाम यूआरएल का एक खंड है: `[id].nexy` उत्तर `/notes/1`, `/notes/2`, और खंड को एक प्रोप के रूप में पृष्ठ पर भेजता है। `id: prop[int]` इसे एक संख्या में बदल देता है, इसलिए `/notes/abc` पृष्ठ चलने से पहले `404` उत्तर देता है।

```nexy filename="src/routes/notes/[id].nexy"
---
from nexy import notFound
from src.notes import find

id: prop[int]
text = find(id)
if text is None:
    notFound()
---
<section class="app-page">
  <h1>{{ text }}</h1>
  <a href="/notes">All notes</a>
</section>
```
<!-- /router -->

<!-- router:modular -->
नियंत्रक के पथ में एक `{id}` यूआरएल का एक खंड है, जो उस नाम के तहत विधि को पास किया जाता है। `id: int` इसे एक संख्या में बदल देता है, इसलिए `/notes/abc` विधि चलने से पहले `404` का उत्तर देता है।

```nexy filename="src/apps/notes/note_view.nexy"
---
text: prop[str]
---
<section class="app-page">
  <h1>{{ text }}</h1>
  <a href="/notes">All notes</a>
</section>
```
<!-- /router -->

`notFound()` अनुरोध को `404` के साथ रोकता है: एक नोट जो मौजूद नहीं है, एक यूआरएल की तरह उत्तर देता है जो मौजूद नहीं है।

## नोट्स को JSON के रूप में परोसें

<!-- router:fbr,custom -->
`src/routes/` के अंतर्गत एक `.py` फ़ाइल एक एपीआई रूट है। HTTP विधि के नाम पर प्रत्येक फ़ंक्शन उस विधि का उत्तर देता है:

```python filename="src/routes/api/notes.py"
from src.notes import NOTES


async def GET():
    return [{"id": id, "text": text} for id, text in NOTES.items()]
```
<!-- /router -->

<!-- router:modular -->
नोट्स के तीन नियंत्रक, एक फ़ाइल में। HTTP विधि के नाम पर प्रत्येक विधि उस विधि का उत्तर देती है:

```python filename="src/apps/notes/notes_controller.py"
from nexy import notFound
from nexy.decorators import Controller
from nexy.hooks import useViews
from src.notes import NOTES, find

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
        text = find(id)
        if text is None:
            notFound()
        return page("src/apps/notes/note_view.nexy", text=text)


@Controller("/api/notes")
class NotesApiController:
    async def get(self) -> list[dict]:
        return [{"id": id, "text": text} for id, text in NOTES.items()]
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .app_controller import AboutController, AppController
from .notes.notes_controller import NoteController, NotesApiController, NotesController


@Module()
class AppModule:
    controllers = [AppController, AboutController, NotesController, NoteController, NotesApiController]
```
<!-- /router -->

तीन यूआरएल जांचें:

- <http://localhost:3000/notes/1> दिखाता है *दूध खरीदें*;
- <http://localhost:3000/notes/9> उत्तर *पेज नहीं मिला*;
- `curl http://localhost:3000/api/notes` प्रिंट करता है `[{"id":1,"text":"Buy milk"},{"id":2,"text":"Ship Nexy"}]`।

एपीआई अपनी स्कीमा के साथ <http://localhost:3000/docs> पर सूचीबद्ध है।

## आपने क्या सीखा

<!-- router:fbr,custom -->
- `[id].nexy` एक गतिशील खंड है; `id: prop[int]` इसे पढ़ता है और परिवर्तित करता है।
- `src/routes/` के अंतर्गत एक `.py` फ़ाइल JSON का उत्तर देती है, प्रति HTTP विधि में एक फ़ंक्शन।
<!-- /router -->
<!-- router:modular -->
- `{id}` नियंत्रक के पथ में एक गतिशील खंड है; `id: int` इसे परिवर्तित करता है।
- एक नियंत्रक विधि जो डेटा उत्तर JSON लौटाती है; वह जो लौटाता है `useViews` एक पृष्ठ का उत्तर देता है।
<!-- /router -->
- `notFound()` उत्तर `404` कहीं से भी; एक साझा मॉड्यूल पेजों और एपीआई को चरणबद्ध रखता है।

## अगले चरण

- [भाग 4: घटक](components.md)
- [अपवाद और त्रुटियाँ](../reference/exceptions.md): `notFound`, `redirect` और अन्य निकास
