# नेक्सी के साथ एक नोट्स ऐप बनाएं, भाग 4: घटक

भाग 4 प्रत्येक नोट को एक पुन: प्रयोज्य घटक में बदल देता है, एक `.nexy` फ़ाइल जिसे आप Python नाम की तरह आयात करते हैं और एक HTML टैग की तरह उपयोग करते हैं।

**शुरू करने से पहले:** [भाग 3](dynamic-routes.md) का ऐप।

## घटक लिखें

एक घटक मार्गों के बाहर एक `.nexy` फ़ाइल है। इसके प्रॉप्स को `prop[...]` के साथ घोषित किया जाता है, और कॉल करने वाला उन्हें विशेषताओं के रूप में पास करता है:

```nexy filename="src/components/NoteCard.nexy"
---
id: prop[int]
text: prop[str]
---
<article class="note">
  <a href="/notes/{{ id }}">{{ text }}</a>
</article>

<style>
  .note { padding: 0.75rem 1rem; border: 1px solid #ddd; border-radius: 0.5rem; }
</style>
```

`<style>` ब्लॉक कार्ड का उपयोग करने वाले प्रत्येक पृष्ठ के साथ भेजा जाता है। इसका दायरा नहीं है: `.note` पूरे पृष्ठ के लिए एक वर्ग है, इसलिए किसी घटक के वर्गों को ऐसे नाम दें जिनका उपयोग केवल वह करता है।

## इसे सूची में उपयोग करें

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  {% for id, text in notes %}
  <NoteCard id="{{ id }}" text="{{ text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  {% for id, text in notes %}
  <NoteCard id="{{ id }}" text="{{ text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

`@/` भाग 1 का आयात उपनाम है: यह `src/` की ओर इशारा करता है। पास्कलकेस में फ़ाइल नाम घटक नाम है: `NoteCard.nexy` निर्यात `NoteCard`।

<http://localhost:3000/notes> खोलें: प्रत्येक नोट अब एक कार्ड है।

## आपने क्या सीखा

- मार्गों के बाहर एक `.nexy` फ़ाइल एक घटक है; इसके `prop[...]` इसके गुण हैं।
- `from "@/components/x.nexy" import X` इसे आयात करता है; `<X />` इसे प्रस्तुत करता है।
- एक `<style>` ब्लॉक का दायरा नहीं है: इसके बाद एक घटक की कक्षाओं को नाम दें।

## अगले चरण

- [भाग 5: नोट्स को SQLite](store-the-notes.md) में संग्रहीत करें
- [घटक](../views/nexy/components.md): `Image`, `Link` और अंतर्निहित सहायक
