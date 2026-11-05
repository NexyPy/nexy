# दृश्य

फ़ाइल प्रारूप चुनने से पहले, यह अंतर करना महत्वपूर्ण है कि नेक्सी संसाधनों को कैसे संभालती है और उन्हें कैसे प्रस्तुत करती है।

| शब्द | परिभाषा |
|---|---|
| **पेज** | एप्लिकेशन का एक यूआरएल-एड्रेसेबल संसाधन। इसे `src/routes/` के अंतर्गत एक फ़ाइल द्वारा परिभाषित किया गया है। |
| **देखें** | एक पृष्ठ के लिए प्रतिक्रिया निकाय तैयार करने की प्रक्रिया। एक दृश्य तर्क और डेटा को HTML या JSON में बदल देता है। |
| **घटक** | एक पुन: प्रयोज्य यूआई बिल्डिंग ब्लॉक जिसका उपयोग दृश्य बनाने के लिए किया जाता है। घटक मूल नेक्सी सहायक या फ्रेमवर्क-विशिष्ट (React, Vue, आदि) हो सकते हैं। |
| **रूट हैंडलर** | एक Python फ़ंक्शन जो एक विशिष्ट विधि के लिए HTTP अनुरोध को संभालता है (उदाहरण के लिए, `GET`, `POST`)। |
| **समापन बिंदु** | एक यूआरएल और एक HTTP विधि का अनूठा संयोजन जो एक रूट हैंडलर उत्तर देता है। |

**निश्चित नहीं? एक `.nexy` फ़ाइल लिखें।** इसके लिए किसी क्लाइंट फ्रेमवर्क की आवश्यकता नहीं है, और आप बाद में एक द्वीप के रूप में इसके अंदर एक React, Vue, Svelte, Solid या Preact घटक जोड़ सकते हैं।

```diagram filename=""
server logic + HTML          →  .nexy      (Python frontmatter + Jinja2)
prose that changes rarely    →  .md        (GitHub-flavoured Markdown)
prose + components           →  .mdx       (React or Preact)
app-like page, client router →  .tsx .vue .svelte (framework files)
API handler                  →  .py        (GET, POST, …)
```

## प्रारूप

| प्रारूप | फ़ाइल | सर्वर रेंडर | क्लाइंट फ्रेमवर्क | नोट्स |
|---|---|---|---|---|
| `.nexy` | [.नेक्सी फ़ाइलें](nexy/README.md) | Jinja2 + Python तर्क, स्ट्रीम किया गया | वैकल्पिक | नेटिव नेक्सी पेज प्रारूप |
| `.md` | [Markdown और MDX](nexy/markdown.md) | अनुरोध समय पर सीएमआरकेजीएफएम | लेआउट के माध्यम से वैकल्पिक | शुद्ध Markdown, जीएफएम, लेआउट-लिपटे |
| `.mdx` | [Markdown और MDX](nexy/markdown.md) | फ्रेमवर्क एसएसआर | React या Preact | Markdown घटकों के साथ |
| `.tsx` | [React](react/differences.md), [Solid](solid/differences.md) या [Preact](preact/differences.md) | क्लाइंट मोड: फ्रेमवर्क, नोड में प्रस्तुत किया गया | React, Solid या Preact | घटक मार्ग |
| `.vue` | [Vue](vue/differences.md) | क्लाइंट मोड: फ्रेमवर्क, नोड में प्रस्तुत किया गया | Vue | एसएफसी मार्ग |
| `.svelte` | [Svelte](svelte/differences.md) | क्लाइंट मोड: फ्रेमवर्क, नोड में प्रस्तुत किया गया | Svelte | एसएफसी मार्ग |

अंतर्निहित `Image`, `Link`, `Audio`, `Video` और `Import` सहायक: [घटक ](nexy/components.md)।

## मिश्रण प्रारूप

आप एक ही प्रोजेक्ट में विभिन्न तकनीकों को मिला सकते हैं:
- **द्वीप**: आप `.nexy` पृष्ठ के अंदर एक React या Vue घटक आयात कर सकते हैं। सर्वर शेल को प्रस्तुत करता है, और फ्रेमवर्क क्लाइंट पर घटक को हाइड्रेट करता है।
- **साझा तर्क**: `.py` फ़ाइलों में रूट हैंडलर साझा एप्लिकेशन स्थिति या एपीआई कॉल के माध्यम से किसी भी प्रारूप में पृष्ठों को डेटा प्रदान कर सकते हैं।

## एक रूपरेखा सक्षम करें

`useFF` को `nexyconfig.py` में सेट करें और निर्भरताएँ जोड़ने के लिए `nexy new` चलाएँ:

```python filename=""
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
```

एक फ्रेमवर्क सक्षम होने पर, Vite अपने क्लाइंट बंडलों को संभालता है। क्लाइंट मोड में इसके एक्सटेंशन रूट बन जाते हैं; सर्वर मोड में वही फ़ाइलें घटक हैं जिन्हें आप द्वीपों के रूप में आयात करते हैं - `src/routes/` के तहत एक फ्रेमवर्क फ़ाइल को वहां अस्वीकार कर दिया जाता है। [सर्वर मोड और क्लाइंट मोड](../routing/fbr/modes.md) देखें।

> [!NOTE]
> in [CSR](../rendering/csr.md) mode, only framework route files are navigable client-side.

## लेआउट

एक निर्देशिका में एक `layout.*` इसके नीचे पृष्ठों को लपेटता है। [लेआउट](../routing/fbr/layouts/README.md) देखें।

## अगले चरण

- [.nexy फ़ाइलें](nexy/README.md): Python + Jinja2 + प्रॉप्स
- [Markdown और MDX](nexy/markdown.md): सामग्री पृष्ठ
- [घटक](nexy/components.md): अंतर्निहित HTML सहायक
