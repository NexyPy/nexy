# नेक्सी के साथ एक नोट्स ऐप बनाएं, भाग 7: सत्यापन त्रुटियां दिखाएं

भाग 7 एक ऐसे नोट को अस्वीकार करता है जो खाली या बहुत लंबा है, और दिखाता है कि फ़ॉर्म के ऊपर, उसी पृष्ठ पर क्यों, फिर भी JavaScript के बिना।

**शुरू करने से पहले:** [भाग 6](create-a-note.md) का ऐप।

## दो प्रकार की त्रुटियाँ

किसी क्रिया के प्रकार के संकेत पहले से ही गलत आकार को अस्वीकार कर देते हैं: `text` फ़ील्ड के बिना एक फॉर्म `create_note` चलने से पहले `422` का उत्तर देता है। मूल्य के बारे में एक नियम, जैसे "रिक्त नहीं", आपको कार्रवाई में लिखना होगा।

## कार्रवाई में नोट की जाँच करें

विफलता विज़िटर को URL में कारण के साथ सूची में वापस भेज देती है; इसके बिना सफलता सूची में वापस चली जाती है:

```python filename="src/actions/notes.py"
from urllib.parse import urlencode

from nexy.decorators import Action
from nexy.http import RedirectResponse
from src.notes import add_note

MAX_LENGTH = 200


def back(error: str = "") -> RedirectResponse:
    query = f"?{urlencode({'error': error})}" if error else ""
    return RedirectResponse(f"/notes{query}", status_code=303)


@Action
async def create_note(text: str) -> RedirectResponse:
    text = text.strip()
    if not text:
        return back("A note cannot be blank.")
    if len(text) > MAX_LENGTH:
        return back(f"A note is at most {MAX_LENGTH} characters.")
    add_note(text)
    return back()
```

`303` ब्राउज़र को अगले पेज को `GET` के साथ लोड करने के लिए कहता है, इसलिए रिफ्रेश फॉर्म को दूसरी बार पोस्ट नहीं करता है।

## फॉर्म के ऊपर कारण बताएं

`useSearchParams()` वर्तमान अनुरोध की क्वेरी स्ट्रिंग पढ़ता है:

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from nexy import useSearchParams
from src.notes import all_notes

notes = all_notes()
error = useSearchParams().get("error", "")
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
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from nexy import useSearchParams
from src.notes import all_notes

notes = all_notes()
error = useSearchParams().get("error", "")
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
</section>
```
<!-- /router -->

`| e` संदेश से बच जाता है: क्वेरी स्ट्रिंग विज़िटर से आती है, इसलिए इसे पृष्ठ में HTML के रूप में कभी नहीं लिखा जाता है। `role="alert"` एक स्क्रीन रीडर से इसकी घोषणा करवाता है।

`required` और `maxlength` ब्राउज़र को अधिकांश गलतियाँ छोड़ने से पहले उन्हें रोकने देते हैं। कार्रवाई फिर से जांच करती है: अनुरोध आपके फॉर्म से आना जरूरी नहीं है।

तीन स्थानों का एक नोट जोड़ें: सूची फॉर्म के ऊपर *एक नोट खाली नहीं हो सकता.* के साथ वापस आती है।

## आपने क्या सीखा

- टाइप संकेत `422` के साथ गलत आकार को अस्वीकार करते हैं; मूल्य के बारे में नियम कार्रवाई में चलते हैं।
- एक क्रिया `RedirectResponse` के साथ उत्तर दे सकती है; `303` एक फॉर्म के बाद दूसरे पोस्ट से बचा जाता है।
- `useSearchParams()` क्वेरी स्ट्रिंग को पढ़ता है, और `| e` विज़िटर ने जो भेजा है उससे बच जाता है।

## अगले चरण

- [भाग 8: नोट संपादित करें और हटाएं](edit-and-delete.md)
- [अपवाद और त्रुटियाँ](../reference/exceptions.md): प्रत्येक स्थिति का एक क्रिया और एक पृष्ठ उत्तर दे सकता है
