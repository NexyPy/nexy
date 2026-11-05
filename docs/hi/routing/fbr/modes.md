# सर्वर मोड और क्लाइंट मोड

एक नेक्सी प्रोजेक्ट या तो **सर्वर-रेंडर्ड** या **क्लाइंट-रूटेड** है, जैसे कि Next.js प्रोजेक्ट या तो सर्वर या क्लाइंट ऐप पर रेंडर किए गए पेज हैं। `useCSR` में `nexyconfig.py` चुनता है।

## सर्वर मोड (`useCSR = False`)

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
```

- पृष्ठ `.nexy`, `.md` या `.mdx` फ़ाइलें `src/routes/` के अंतर्गत हैं।
- मूल `layout.nexy` का स्वामी `<!DOCTYPE html>`, `<html>`, `<head>` और `<body>` है।
- क्लाइंट घटकों (React, Vue, Svelte, Solid या Preact) को **द्वीपों** के रूप में अनुमति दी जाती है: आप `.nexy` पृष्ठ से एक आयात करते हैं और यह ब्राउज़र में हाइड्रेट होता है। देखें [द्वीप](../../rendering/islands.md)।
- क्लाइंट घटक कभी भी रूट नहीं होता है. उन्हें `src/components/` में रखें।
- एक समय में एक ग्राहक ढांचा।

```text
src/
├─ routes/
│  ├─ layout.nexy         document
│  ├─ index.nexy          page
│  └─ api/users.py        API handler
└─ components/Counter.tsx island
```

## क्लाइंट मोड (`useCSR = True`)

```python filename="nexyconfig.py"
class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

- पेज आपके क्लाइंट फ्रेमवर्क की फ़ाइलें हैं: `.tsx` के लिए React, `.vue`, `.svelte`।
- `.md` और `.mdx` फ़ाइलें वैध मार्ग बनी रहती हैं: नेक्सी उन्हें क्लाइंट लेआउट के अंदर सर्वर पर प्रस्तुत करता है, और क्लाइंट राउटर वहां से नेविगेशन लेता है।
- किसी भी फ्रेमवर्क का रूट लेआउट (`layout.tsx`, `layout.vue`, `layout.svelte`) का मालिक है `<!DOCTYPE html>`, `<html>`, `<head>` और `<body>`, जैसे Next.js ऐप राउटर का रूट लेआउट। नेक्सी इसे पहली प्रतिक्रिया के लिए नोड में प्रस्तुत करता है और फ्रेमवर्क पूरे दस्तावेज़ को हाइड्रेट करता है। [layout.tsx](../../views/react/differences.md) देखें।
- `.py` फ़ाइलें एपीआई हैंडलर हैं जो क्लाइंट मार्गों के बगल में FastAPI द्वारा प्रदान की जाती हैं।
- कोई `.nexy` फ़ाइल नहीं है, और कोई `layout.nexy` भी नहीं है।
- पेजों के बीच नेविगेशन ब्राउज़र में होता है।

```text
src/routes/
├─ layout.tsx             document
├─ index.tsx              page
├─ users.tsx              page
└─ api/users.py           API handler
```

## क्या अस्वीकार किया गया है

नेक्सी `nx dev`, `nx start` और `nx build` से पहले प्रोजेक्ट की जांच करता है और फाइलों की सूची के साथ रुकता है:

| मोड | अस्वीकृत | संदेश |
|---|---|---|
| सर्वर | `.tsx`, `.jsx`, `.vue` या `.svelte` `src/routes/` | के अंतर्गत घटकों को `src/components/` पर ले जाएं, या `useCSR = True` | सेट करें
| क्लाइंट | किसी भी `.nexy` फ़ाइल को `src/routes/` | के अंतर्गत फ्रेमवर्क घटकों के रूप में लिखें, या सेट करें `useCSR = False` |
| दोनों | में एक से अधिक फ्रंटएंड फ्रेमवर्क `useFF` | `useFF must configure exactly one frontend framework` |
| क्लाइंट | `useRouter` (मॉड्यूलर राउटर) | `useCSR requires file-based routing` |
| ग्राहक | नहीं `useFF` | `useCSR requires a client framework` |

`_` या `.` से शुरू होने वाली फ़ाइलों और फ़ोल्डरों को इस जाँच द्वारा अनदेखा कर दिया जाता है।

## कौन सा

- **सामग्री, विपणन, दस्तावेज़, एसईओ-प्रथम साइटें**: द्वीपों के साथ सर्वर मोड।
- **समृद्ध क्लाइंट नेविगेशन वाले डैशबोर्ड और ऐप्स**: क्लाइंट मोड।
- **शीर्ष पर एक क्लाइंट ऐप के साथ एक Python एपीआई**: क्लाइंट मोड, पृष्ठों के बगल में `.py` हैंडलर के साथ।

## अगले चरण

- [लेआउट](layouts/README.md)
- [प्रतिपादन](../../rendering/README.md)
- [कॉन्फिग](../../reference/config.md)
