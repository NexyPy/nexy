# सर्वर मोड और क्लाइंट मोड

नेक्सी प्रोजेक्ट या तो **सर्वर-रेंडर्ड** या **क्लाइंट-रूटेड** है, जैसे नेक्स्ट.जेएस प्रोजेक्ट या तो है
सर्वर या क्लाइंट ऐप पर रेंडर किए गए पेज। `useCSR` में `nexyconfig.py` चुनता है।

## सर्वर मोड (`useCSR = False`)

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
```

- पेज `.nexy`, `.md` या `src/routes/` के अंतर्गत `.mdx` फ़ाइलें हैं।
- मूल `layout.nexy` का स्वामी `<!DOCTYPE html>`, `<html>`, `<head>` और `<body>` है।
- क्लाइंट घटकों (रिएक्ट, व्यू, स्वेल्ट, सॉलिड या प्रीएक्ट) को **द्वीपों** के रूप में अनुमति है: आप एक आयात करते हैं
  `.nexy` पृष्ठ से और यह ब्राउज़र में हाइड्रेट होता है। [द्वीप](../../rendering/islands.md) देखें।
- क्लाइंट घटक कभी भी रूट नहीं होता है। उन्हें `src/components/` में रखें।
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

- पेज आपके क्लाइंट फ्रेमवर्क की फ़ाइलें हैं: `.tsx` रिएक्ट के लिए, `.vue`, `.svelte`।
- `.md` और `.mdx` फ़ाइलें वैध मार्ग बनी रहती हैं: नेक्सी उन्हें क्लाइंट के अंदर सर्वर पर प्रस्तुत करता है
  लेआउट, और क्लाइंट राउटर वहां से नेविगेशन का कार्यभार संभाल लेता है।
- किसी भी ढांचे का रूट लेआउट (`layout.tsx`, `layout.vue`, `layout.svelte`) का मालिक है `<!DOCTYPE html>`, `<html>`, `<head>` और `<body>`, जैसे
  Next.js ऐप राउटर का रूट लेआउट। नेक्सी इसे पहली प्रतिक्रिया के लिए नोड में प्रस्तुत करता है और
  फ्रेमवर्क पूरे दस्तावेज़ को हाइड्रेट करता है। [layout.tsx](../../views/react/differences.md) देखें।
- `.py` फ़ाइलें एपीआई हैंडलर हैं जो क्लाइंट रूट के बगल में फास्टएपीआई द्वारा प्रदान की जाती हैं।
- कोई `.nexy` फ़ाइल नहीं है, और कोई `layout.nexy` भी नहीं है।
- पृष्ठों के बीच नेविगेशन ब्राउज़र में होता है।

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
| सर्वर | `.tsx`, `.jsx`, `.vue` या `.svelte` `src/routes/` के अंतर्गत | घटकों को `src/components/` में ले जाएं, या `useCSR = True` | सेट करें
| क्लाइंट | किसी भी `.nexy` फ़ाइल को `src/routes/` | के अंतर्गत फ्रेमवर्क घटकों के रूप में लिखें, या सेट करें `useCSR = False` |
| दोनों | में एक से अधिक फ्रंटएंड फ्रेमवर्क `useFF` | `useFF must configure exactly one frontend framework` |
| क्लाइंट | `useRouter` (मॉड्यूलर राउटर) | `useCSR requires file-based routing` |
| ग्राहक | नहीं `useFF` | `useCSR requires a client framework` |

`_` या `.` से शुरू होने वाली फ़ाइलों और फ़ोल्डरों को इस जाँच द्वारा अनदेखा कर दिया जाता है।

## कौन सा

- **सामग्री, मार्केटिंग, दस्तावेज़, एसईओ-प्रथम साइटें**: द्वीपों के साथ सर्वर मोड।
- **रिच क्लाइंट नेविगेशन वाले डैशबोर्ड और ऐप्स**: क्लाइंट मोड।
- **शीर्ष पर क्लाइंट ऐप के साथ एक पायथन एपीआई**: क्लाइंट मोड, पेजों के बगल में `.py` हैंडलर के साथ।

## अगले चरण

- [लेआउट](layouts/README.md)
- [प्रतिपादन](../../rendering/README.md)
- [कॉन्फिग](../../reference/config.md)