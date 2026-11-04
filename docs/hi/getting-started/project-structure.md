# प्रोजेक्ट संरचना

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

- **कुछ ऐसा जिसे ब्राउज़र खोल सकता है** - एक मार्ग: `src/routes/`।
- **कई मार्गों द्वारा उपयोग किया जाने वाला एक टुकड़ा** - एक घटक या एक मॉड्यूल: `src/components/`, `src/`।
- **एक फ़ाइल वैसे ही परोसी जाती है जैसे वह है** - `public/`।
- **मॉड्यूलर राउटर का एक नियंत्रक** - `src/apps/`।
- **उत्पन्न** - `__nexy__/`; इसे कभी संपादित न करें.

> [!चेतावनी]
> `src/routes/` को स्कैन किया जाता है: वहां रखा गया एक सहायक एक मार्ग बन जाता है। एक सहायक रखो जो मार्ग नहीं है
> `src/routes/` के बाहर, या इसका नाम `_` से शुरू करें।

## `src/routes/`

नीचे आरक्षित नामों को छोड़कर, प्रत्येक फ़ाइल एक रूट बन जाती है। फ़ाइल पथ माइनस एक्सटेंशन है
यूआरएल - [रूटिंग](../routing/README.md) देखें।

| फ़ाइल | भूमिका |
|---|---|
| `layout.nexy` | सहोदर और बाल पृष्ठों को लपेटता है |
| `errors.nexy` | निर्देशिका के लिए 500 पृष्ठ |
| `notfound.nexy` | निर्देशिका के लिए 404 पृष्ठ |
| `dependencies.py` | ने निर्देशिका के लिए फास्टएपीआई निर्भरताएं साझा कीं |
| `__init__.py` | पायथन पैकेज मार्कर |
| `loading.nexy` | आरक्षित - मार्गों से बाहर रखा गया है, लेकिन इसका अभी तक कोई रनटाइम प्रभाव नहीं है |

प्रत्येक पृष्ठ का नाम प्रति ढाँचे में भी मौजूद है। `react()` कॉन्फ़िगर के साथ, `layout.jsx` और `layout.tsx`
बिल्कुल `layout.nexy` की तरह आरक्षित हैं। सूचियाँ `nexy/core/config.py` में बनाई गई हैं
(`LAYOUT_FILE_NAMES`, `ERROR_FILE_NAMES`, `NOTFOUND_FILE_NAMES`, `LOADING_FILE_NAMES`)।

> [!नोट]
> `notfound.nexy` और `errors.nexy` केवल तभी स्थापित किए जाते हैं जब एक प्रति मौजूद हो
> मार्ग मूल। उपनिर्देशिका में एक प्रतिलिपि उस उपसर्ग के लिए पृष्ठ को परिष्कृत करती है।

## `src/apps/`

निर्देशिका `nexy new` मॉड्यूलर राउटर के लिए उपयोग करती है: नियंत्रक, मॉड्यूल और प्रदाता रजिस्टर
`nexy.decorators` से डेकोरेटर के माध्यम से उनके मार्ग, फिर समुच्चय `APIRouter` को माउंट किया जाता है
`nexyconfig.py` में `useRouter` के साथ।

एक प्रोजेक्ट में दोनों राउटर हो सकते हैं: `useRouter` मॉड्यूलर राउटर को माउंट करता है, और `src/routes/` स्कैन किया जाता है
जब भी वह निर्देशिका मौजूद हो. [मॉड्यूलर रूटिंग](../routing/modular/README.md) देखें।

## `public/`

यहां फ़ाइलें साइट रूट से दी जाती हैं: `/favicon.ico`, `/robots.txt`, छवियां, फ़ॉन्ट।

## `__nexy__/`

`nx build` द्वारा उत्पन्न (और `nx dev` द्वारा इसके लिए आवश्यक भागों के लिए)। इसमें शामिल है:

- संकलित रूट मॉड्यूल, पायथन पैकेज के रूप में (`__nexy__/src/routes/...`);
- जनरेट किए गए क्लाइंट प्रवेश बिंदु (`main.ts`, `vite.ts`, `*.auto.ts`);
- `client/` वाइट बिल्ड के बाद - संपत्ति, मेनिफेस्ट, पूर्व-रेंडर HTML;
- `build-cache.json`।

संपूर्ण निर्देशिका को डिस्पोजेबल मानें: इसे हटाएं, इसका पुनर्निर्माण करें। इसे हाथ से संपादित करने से परिवर्तन नष्ट हो जाता है
अगले निर्माण पर. इसे `.gitignore` में जोड़ें।

## अगले चरण

- [रूटिंग](../routing/README.md): एक पथ एक यूआरएल कैसे बनता है
- [कॉन्फिग](../reference/config.md): प्रत्येक प्रोजेक्ट विकल्प
- [फ्रंटएंड](../guides/frontend.md): वाइट, स्टाइलिंग और क्लाइंट बिल्ड