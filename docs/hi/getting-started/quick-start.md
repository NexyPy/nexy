# त्वरित शुरुआत

आप एक नेक्सी प्रोजेक्ट बनाएंगे, उसे चलाएंगे, और उसे संपादित करते समय एक पृष्ठ परिवर्तन देखेंगे। इसमें तीन मिनट लगते हैं. [ट्यूटोरियल](tutorial.md) फिर एक समापन बिंदु और एक उत्पादन निर्माण जोड़ता है।

## शुरू करने से पहले

| आपको चाहिए | क्यों |
|---|---|
| Python 3.12+ | `requires-python` में `pyproject.toml` |
| [uv](https://docs.astral.sh/uv/) | `uvx` प्रदान करता है, प्रोजेक्ट बनाता है और उसके पैकेज स्थापित करता है |
| Node.js 18+ | केवल यदि आप क्लाइंट फ्रेमवर्क का उपयोग करते हैं (React, Vue, Svelte, Solid, Preact) |

नहीं uv अभी तक? [स्थापना](installation.md) देखें।

## 1. प्रोजेक्ट बनाएं

```bash
uvx nexy new my-app
```

`uvx` uv के साथ आता है, इसलिए पहले uv इंस्टॉल करें। यह नेक्सी को एक अस्थायी वातावरण में चलाता है, जो **परियोजना बनाने** के लिए पर्याप्त है। `nexy new` फिर प्रोजेक्ट का अपना `.venv` बनाता है और वहां अपने पैकेज स्थापित करता है। चार संकेत वायरिंग तय करते हैं:

| शीघ्र | प्रभाव |
|---|---|
| फ़ाइल-आधारित राउटर? | `Yes` स्कैन `src/routes/`; `No` मॉड्यूलर राउटर को `src/apps/` में तैयार करता है |
| प्रोजेक्ट का प्रकार | `Web` एक लेआउट और क्लाइंट संपत्ति जोड़ता है, `API` बिना व्यू के शुरू होता है |
| ग्राहक घटक? | एक रूपरेखा और उसका Vite सेटअप जोड़ता है |
| ओआरएम/डेटाबेस | एक मॉडल परत जोड़ता है, या कुछ भी नहीं |

निश्चित नहीं? उत्तर `Yes`, `Web`, और कोई क्लाइंट घटक नहीं। आप प्रत्येक को बाद में जोड़ सकते हैं.

## 2. इसे चलाएँ

```bash
cd my-app
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

<http://localhost:3000> खोलें। आपको आरंभिक पृष्ठ देखना चाहिए. पोर्ट `usePort` (डिफ़ॉल्ट `3000`) से आता है; `--port` और `--host` इसे प्रति रन ओवरराइड करते हैं।

> [!NOTE]
> प्रोजेक्ट के वर्चुअल वातावरण के अंदर `new` और `init` को छोड़कर प्रत्येक कमांड चलाएँ, या इसे `uv run` के साथ उपसर्ग करें, जैसा कि `uv run nexy dev` में है। इसके बाहर, जिस प्रोजेक्ट को `sqlmodel` की आवश्यकता होती है वह `No module named 'sqlmodel'` के साथ विफल हो जाता है।

## 3. एक पेज बदलें

<!-- router:fbr,custom -->
`src/routes/` के अंतर्गत एक फ़ाइल एक रूट है। `src/routes/hello.nexy` बनाएं:

```nexy filename="src/routes/hello.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```
<!-- /router -->

<!-- router:modular -->
एक नियंत्रक एक दृश्य लौटाता है। `src/apps/hello_view.nexy` बनाएं:

```nexy filename="src/apps/hello_view.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```

फिर पृष्ठ को `src/apps/app_controller.py` में घोषित करें और इसे मॉड्यूल में जोड़ें:

```python filename="src/apps/app_controller.py"
@Controller("/hello")
class HelloController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/hello_view.nexy")})
```

```python filename="src/apps/app_module.py"
from .app_controller import AboutController, AppController, HelloController

controllers = [AppController, AboutController, HelloController]
```
<!-- /router -->

<http://localhost:3000/hello> खोलें। `"Hello"` को `"Bonjour"` में बदलें और सहेजें: पृष्ठ मैन्युअल पुनः लोड किए बिना अपडेट हो जाता है। यदि कोड गलत है, तो ब्राउज़र रिक्त पृष्ठ के बजाय त्रुटि दिखाता है।

`prop[str]` एक टाइप की गई संपत्ति घोषित करता है। फ्रंटमैटर के अंतर्गत मार्कअप Jinja2 है - [.nexy फ़ाइलें](../views/nexy/README.md) देखें।

## आगे कहाँ

| आप चाहते हैं | पढ़ें |
|---|---|
| एक Python एंडपॉइंट जोड़ें और एक बिल्ड शिप करें | [ट्यूटोरियल](tutorial.md) |
| जानें कि प्रत्येक फ़ाइल कहां है | [परियोजना संरचना](project-structure.md) |
| समझें कि कौन क्या बनाता है | [नेक्सी कैसे काम करती है](how-nexy-works.md) |
| React, Vue, Svelte, Solid या Preact का उपयोग करें | [दृश्य](../views/README.md) |
