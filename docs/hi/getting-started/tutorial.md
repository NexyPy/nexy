# ट्यूटोरियल: 10 मिनट में नोट्स पेज बनाएं

आप एक प्रोजेक्ट बनाएंगे, एक पेज जोड़ेंगे, एक Python एंडपॉइंट जोड़ेंगे, उनके बीच डेटा साझा करेंगे, और उत्पादन के लिए निर्माण करेंगे। आप एक पृष्ठ और JSON के रूप में परोसे गए नोट्स की एक सूची के साथ समाप्त होते हैं।

नेक्सी में नए हैं? पहले [त्वरित शुरुआत](quick-start.md) करें: इसमें तीन मिनट लगते हैं।

```diagram filename="संपूर्ण ट्यूटोरियल एक पंक्ति में"
uvx nexy new notes ──► edit layout ──► add page ──► add endpoint ──► share data ──► nx build ──► nx start
```

## 1. प्रोजेक्ट बनाएं

```bash
uvx nexy new notes
cd notes
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

`uvx` [uv](https://docs.astral.sh/uv/) के साथ आता है और केवल प्रोजेक्ट बनाता है। इसके बाद प्रत्येक कमांड प्रोजेक्ट के वर्चुअल वातावरण के अंदर चलता है (या `uv run nexy dev` के रूप में)।

फ़ाइल-आधारित राउटर, एक वेब प्रोजेक्ट और कोई भी क्लाइंट फ़्रेमवर्क (या कोई नहीं) चुनें। खुला
<http://localhost:3000>. लंबे चरण अपनी अवधि के साथ एक पंक्ति प्रिंट करते हैं, जैसा कि `uv` करता है।

<!-- router:modular -->
फ़ाइल-आधारित राउटर प्रॉम्प्ट का उत्तर `No`: `nx new` मॉड्यूलर राउटर को `src/routes/` के बजाय `src/apps/` में रखता है।
<!-- /router -->

<!-- router:custom -->
पृष्ठों के लिए फ़ाइल-आधारित राउटर प्रॉम्प्ट का उत्तर `Yes` दें, फिर अपने मौजूदा `APIRouter` को `nexyconfig.py` में माउंट करें: दोनों राउटर सह-अस्तित्व में हैं।
<!-- /router -->

## 2. लेआउट संपादित करें

<!-- router:fbr,custom -->
`src/routes/layout.nexy` HTML दस्तावेज़ का स्वामी है (React क्लाइंट रूटिंग के साथ यह `layout.tsx` है)। `<title>` बदलें:

```nexy
<title>Notes</title>
```

सहेजें: ब्राउज़र पुनः लोड होता है. [लेआउट](../routing/fbr/layouts/README.md) देखें।
<!-- /router -->

<!-- router:modular -->
नियंत्रक दृश्य के चारों ओर `src/apps/layout.nexy` प्रस्तुत करता है, और वह फ़ाइल HTML दस्तावेज़ का स्वामी है। `<title>` बदलें:

```nexy
<title>Notes</title>
```

सहेजें: ब्राउज़र पुनः लोड होता है. [नियंत्रक से दृश्य](../routing/modular/README.md#views-from-a-controller) देखें।
<!-- /router -->

## 3. एक पेज जोड़ें

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<h1>Notes</h1>
<ul>
  {% for note in notes %}
  <li>{{ note }}</li>
  {% endfor %}
</ul>
```

खोलें <http://localhost:3000/notes>: आपको दो गोलियां दिखनी चाहिए। इसे `/notes` पर परोसा जाता है। `---` के बीच का भाग Python है, शेष भाग Jinja2 है।
<!-- /router -->

<!-- router:modular -->
एक नियंत्रक एक दृश्य लौटाता है। बनाएं `src/apps/notes_view.nexy`:

```nexy filename="src/apps/notes_view.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<h1>Notes</h1>
<ul>
  {% for note in notes %}
  <li>{{ note }}</li>
  {% endfor %}
</ul>
```

`src/apps/app_controller.py` में मार्ग घोषित करें और नियंत्रक को मॉड्यूल में जोड़ें:

```python filename="src/apps/app_controller.py"
@Controller("/notes")
class NotesController:
    async def get(self):
        return useViews("src/apps/layout.nexy", context={
            "children": useViews("src/apps/notes_view.nexy"),
        })
```

```python filename="src/apps/app_module.py"
from .app_controller import AppController, NotesController

controllers = [AppController, NotesController]
```

खोलें <http://localhost:3000/notes>: आपको दो गोलियां दिखनी चाहिए। `---` के बीच का भाग Python है, शेष भाग Jinja2 है।
<!-- /router -->

## 4. एक समापनबिंदु जोड़ें

<!-- router:fbr,custom -->
```python filename="src/routes/api/notes.py"
async def GET():
    return [{"id": 1, "text": "Buy milk"}]
```

```bash
curl http://localhost:3000/api/notes
```

आपको `[{"id":1,"text":"Buy milk"}]` मिलना चाहिए। फ़ंक्शन का नाम HTTP विधि है। इंटरएक्टिव एपीआई दस्तावेज़ `/docs` पर हैं।
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/app_controller.py"
@Controller("/api/notes")
class NotesApiController:
    async def get(self):
        return [{"id": 1, "text": "Buy milk"}]
```

`src/apps/app_module.py` में `NotesApiController` को `controllers` में जोड़ें, फिर चलाएँ:

```bash
curl http://localhost:3000/api/notes
```

आपको `[{"id":1,"text":"Buy milk"}]` मिलना चाहिए। विधि का नाम HTTP विधि है. इंटरएक्टिव एपीआई दस्तावेज़ `/docs` पर हैं।
<!-- /router -->

## 5. डेटा साझा करें

सूची को Python मॉड्यूल में ले जाएं और दोनों फ़ाइलों में इसका उपयोग करें:

```python filename="src/notes.py"
NOTES = ["Buy milk", "Ship Nexy"]
```

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes.nexy"
---
from src.notes import NOTES as notes
---
```

```python filename="src/routes/api/notes.py"
from src.notes import NOTES


async def GET():
    return [{"id": i, "text": text} for i, text in enumerate(NOTES, start=1)]
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes_view.nexy"
---
from src.notes import NOTES as notes
---
```

```python filename="src/apps/app_controller.py"
from src.notes import NOTES


@Controller("/api/notes")
class NotesApiController:
    async def get(self):
        return [{"id": i, "text": text} for i, text in enumerate(NOTES, start=1)]
```
<!-- /router -->

## 6. बनाएं और परोसें

```bash
nx build
nx start
```

`nx build` प्रत्येक चरण को उसकी अवधि के साथ प्रिंट करता है। `nx start` संकलित आउटपुट को Uvicorn के साथ प्रस्तुत करता है: रनटाइम पर कोई नोड प्रक्रिया नहीं।

## आगे कहाँ

- [रूटिंग](../routing/README.md): गतिशील खंड और समूह
- [क्रियाएँ](../guides/actions.md): किसी फॉर्म से या क्लाइंट से Python को कॉल करें
- [परीक्षण](../guides/testing.md): परीक्षण पृष्ठ और समापन बिंदु
- [तैनाती](../deployment/README.md): कंटेनर और रिवर्स प्रॉक्सी
