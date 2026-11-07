# नेक्सी के साथ एक नोट्स ऐप बनाएं, भाग 2: पेज और लेआउट

भाग 2 उस पृष्ठ को जोड़ता है जो नोट्स को सूचीबद्ध करता है, और दिखाता है कि लेआउट इसे HTML दस्तावेज़ में कैसे लपेटता है।

**शुरू करने से पहले:** [भाग 1](create-the-project.md) का प्रोजेक्ट, जिसमें `nexy dev` चल रहा है।

## नोट्स पृष्ठ जोड़ें

<!-- router:fbr,custom -->
एक पृष्ठ `src/routes/` के अंतर्गत एक फ़ाइल है, और इसका पथ इसका यूआरएल है। नोट्स पेज बनाएं:

```nexy filename="src/routes/notes/index.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for note in notes %}
    <li>{{ note }}</li>
    {% endfor %}
  </ul>
</section>
```

`notes/index.nexy` उत्तर `/notes`।
<!-- /router -->

<!-- router:modular -->
एक नियंत्रक एक URL का उत्तर देता है और एक दृश्य लौटाता है। नोट्स को अपना स्वयं का फ़ोल्डर दें, इस दृश्य के साथ:

```nexy filename="src/apps/notes/notes_view.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for note in notes %}
    <li>{{ note }}</li>
    {% endfor %}
  </ul>
</section>
```

और नियंत्रक जो इसे `/notes` पर प्रस्तुत करता है:

```python filename="src/apps/notes/notes_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews

LAYOUT = "src/apps/layout.nexy"


@Controller("/notes")
class NotesController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/notes/notes_view.nexy")})
```

एक नियंत्रक केवल तभी उत्तर देता है जब कोई मॉड्यूल इसे सूचीबद्ध करता है। इसे रूट मॉड्यूल में जोड़ें:

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .app_controller import AboutController, AppController
from .notes.notes_controller import NotesController


@Module()
class AppModule:
    controllers = [AppController, AboutController, NotesController]
```
<!-- /router -->

खोलें <http://localhost:3000/notes>: आपको दो गोलियां दिखनी चाहिए। दो `---` लाइनों के बीच का भाग Python है, जो सर्वर पर चलता है; बाकी Jinja2 टैग जैसे `{% for %}` और `{{ note }}` के साथ HTML है।

## लेआउट बदलें

<!-- router:fbr,custom -->
`src/routes/layout.nexy` HTML दस्तावेज़ का स्वामी है: `<html>`, `<head>` और `<body>`। नेक्सी इसमें प्रत्येक पृष्ठ को लपेटता है, जहां वह `{{children | safe}}` लिखता है।
<!-- /router -->
<!-- router:modular -->
`src/apps/layout.nexy` HTML दस्तावेज़ का स्वामी है: `<html>`, `<head>` और `<body>`। नियंत्रक दृश्य को `children` के रूप में पास करके अपना दृश्य इसमें लपेट देता है।
<!-- /router -->

लेआउट खोलें और लाइन `<title>Nexy App</title>` को इसमें बदलें:

```html
<title>Notes</title>
```

सहेजें: ब्राउज़र का टैब अब प्रत्येक पृष्ठ पर *नोट्स* पढ़ता है।

## पेजों को हेडर के नीचे जगह दें

लेआउट का हेडर निश्चित है: यह विंडो के शीर्ष पर, पृष्ठ पर रहता है। स्टार्टर के पन्ने इसके नीचे अपना स्थान निर्धारित करते हैं; नोट्स ऐप के पेज उसके लिए एक क्लास साझा करते हैं, `app-page`, जिसे ट्यूटोरियल का प्रत्येक पेज अपनी सामग्री के आसपास रखता है। इसे `src/globale.css` के अंत में जोड़ें, प्रत्येक पृष्ठ पर स्टाइलशीट पहले से ही लोड होती है:

```css
/* The pages of the notes app: one readable column below the fixed header. */
.app-page {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  max-width: 42rem;
  margin: 0 auto;
  padding: 8rem 1.5rem 5rem;
}

.app-page h1 {
  font-size: 2rem;
}

.app-page form {
  display: flex;
  flex-wrap: wrap;
  align-items: end;
  gap: 0.5rem;
}

.app-page label {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.app-page input:not([type="hidden"]) {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-second);
  border-radius: 0.375rem;
  background: var(--background);
}

.app-page button {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  background: var(--foreground);
  color: var(--background);
  cursor: pointer;
}

.app-page a {
  text-decoration: underline;
}
```

Tailwind, जिसे स्टार्टर उपयोग करता है, फॉर्म फ़ील्ड की सीमाओं को हटा देता है: ये नियम उन्हें वापस दे देते हैं, ताकि अगले भागों के फॉर्म देखे जा सकें।

## आपने क्या सीखा

<!-- router:fbr,custom -->
- `src/routes/` के अंतर्गत एक `.nexy` फ़ाइल एक पृष्ठ है; इसका फ़ोल्डर और नाम इसका यूआरएल है।
- रूट `layout.nexy` HTML दस्तावेज़ में प्रत्येक पृष्ठ को लपेटता है।
<!-- /router -->
<!-- router:modular -->
- एक नियंत्रक एक यूआरएल का उत्तर देता है और `useViews` के साथ एक `.nexy` दृश्य प्रस्तुत करता है; एक मॉड्यूल इसे सूचीबद्ध करता है।
- लेआउट भी एक दृश्य है: नियंत्रक पृष्ठ दृश्य को `children` के रूप में पास करता है।
<!-- /router -->
- एक `.nexy` फ़ाइल Python के बीच `---` है, फिर HTML के साथ Jinja2 है।
- `src/globale.css` प्रत्येक पृष्ठ द्वारा साझा की जाने वाली शैलियों को धारण करता है, जैसे कि `app-page`।

## अगले चरण

- [भाग 3: गतिशील मार्ग और एक एपीआई](dynamic-routes.md)
- [.nexy फ़ाइलें](../views/nexy/README.md): प्रॉप्स, घटक और शैलियाँ
