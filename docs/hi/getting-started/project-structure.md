# परियोजना संरचना

नेक्सी प्रोजेक्ट की प्रत्येक फ़ाइल में एक कार्य होता है। यह पृष्ठ जो कहता है।

## शीर्ष स्तर

```text
my-app/
├─ src/
│  ├─ routes/            file-based routes (FBR)
│  │  ├─ index.nexy      → /
│  │  ├─ layout.nexy     shared layout, not a route
│  │  └─ api/hello.py    → /api/hello
│  ├─ apps/              modular router, decorators (optional, next to routes/)
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

कोई फ़ोल्डर चुनने के लिए, पूछें कि फ़ाइल क्या है:

- **ब्राउज़र कुछ खोल सकता है** - एक मार्ग: `src/routes/`।
- **कई मार्गों द्वारा उपयोग किया जाने वाला एक टुकड़ा** - एक घटक या एक मॉड्यूल: `src/components/`, `src/`।
- **एक फ़ाइल इस प्रकार प्रस्तुत की गई है** - `public/`।
- **मॉड्यूलर राउटर का एक नियंत्रक** - `src/apps/`।
- **उत्पन्न** - `__nexy__/`; इसे कभी संपादित न करें.

> [!चेतावनी]
> `src/routes/` को स्कैन किया जाता है: वहां रखा गया एक सहायक एक मार्ग बन जाता है। एक सहायक रखें जो `src/routes/` के बाहर का मार्ग नहीं है, या उसका नाम `_` से शुरू करें।

## `src/routes/`

नीचे आरक्षित नामों को छोड़कर, प्रत्येक फ़ाइल एक रूट बन जाती है। फ़ाइल पथ में एक्सटेंशन को छोड़कर URL है - [रूटिंग](../routing/README.md) देखें।

| फ़ाइल | भूमिका |
|---|---|
| `layout.nexy` | सहोदर और बच्चों के पन्ने लपेटता है |
| `errors.nexy` | निर्देशिका के लिए 500 पृष्ठ |
| `notfound.nexy` | निर्देशिका के लिए 404 पृष्ठ |
| `dependencies.py` | निर्देशिका के लिए साझा की गई FastAPI निर्भरताएँ |
| `__init__.py` | Python पैकेज मार्कर |
| `loading.nexy` | आरक्षित - मार्गों से बाहर रखा गया है, लेकिन इसका अभी तक कोई रनटाइम प्रभाव नहीं है |

प्रत्येक पृष्ठ का नाम प्रति ढाँचे में भी मौजूद है। `react()` कॉन्फ़िगर होने पर, `layout.jsx` और `layout.tsx` बिल्कुल `layout.nexy` की तरह आरक्षित हैं। सूचियाँ `nexy/core/config.py` (`LAYOUT_FILE_NAMES`, `ERROR_FILE_NAMES`, `NOTFOUND_FILE_NAMES`, `LOADING_FILE_NAMES`) में बनाई गई हैं।

> [!नोट]
> `notfound.nexy` और `errors.nexy` केवल तभी स्थापित होते हैं जब रूट रूट पर एक प्रति मौजूद होती है। उपनिर्देशिका में एक प्रतिलिपि उस उपसर्ग के लिए पृष्ठ को परिष्कृत करती है।

## `src/apps/`

निर्देशिका `nexy new` मॉड्यूलर राउटर के लिए उपयोग करती है: नियंत्रक, मॉड्यूल और प्रदाता `nexy.decorators` से डेकोरेटर के माध्यम से अपने मार्गों को पंजीकृत करते हैं, फिर कुल `APIRouter` को `nexyconfig.py` में `useRouter` के साथ माउंट किया जाता है।

एक प्रोजेक्ट में दोनों राउटर हो सकते हैं: `useRouter` मॉड्यूलर राउटर को माउंट करता है, और `src/routes/` जब भी वह निर्देशिका मौजूद होती है तो स्कैन किया जाता है। [मॉड्यूलर रूटिंग](../routing/modular/README.md) देखें।

## `public/`

यहां फ़ाइलें साइट रूट से दी जाती हैं: `/favicon.ico`, `/robots.txt`, छवियां, फ़ॉन्ट।

## `__nexy__/`

`nx build` द्वारा उत्पन्न (और `nx dev` द्वारा इसके लिए आवश्यक भागों के लिए)। इसमें शामिल है:

- संकलित रूट मॉड्यूल, एक Python पैकेज (`__nexy__/src/routes/...`) के रूप में;
- उत्पन्न क्लाइंट प्रवेश बिंदु (`main.ts`, `vite.ts`, `*.auto.ts`);
- `client/` एक Vite निर्माण के बाद - संपत्ति, प्रकट, पूर्व-रेंडर HTML;
- `build-cache.json`.

संपूर्ण निर्देशिका को डिस्पोजेबल मानें: इसे हटाएं, इसका पुनर्निर्माण करें। इसे हाथ से संपादित करने से अगले निर्माण में परिवर्तन खो जाता है। इसे `.gitignore` में जोड़ें।

## अगले चरण

- [रूटिंग](../routing/README.md): कैसे एक पथ एक यूआरएल बन जाता है
- [कॉन्फ़िगर](../reference/config.md): प्रत्येक प्रोजेक्ट विकल्प
- [फ्रंटएंड](../guides/frontend.md): Vite, स्टाइलिंग और क्लाइंट बिल्ड
