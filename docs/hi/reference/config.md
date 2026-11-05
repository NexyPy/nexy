# कॉन्फिग

कॉन्फ़िगरेशन प्रोजेक्ट रूट पर `nexyconfig.py` में एक वर्ग है। नेक्सी इसे उस निर्देशिका से लोड करता है जिसमें यह चलता है; फ़ाइल के बिना एक प्रोजेक्ट डिफ़ॉल्ट का उपयोग करता है।

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    usePort = 3000
    useTitle = "My App"
    useAliases = {"@": "src"}
```

## सर्वर

| फ़ील्ड | डिफ़ॉल्ट | अर्थ |
|---|---|---|
| `usePort` | `3000` | पोर्ट `dev` और `start` | के लिए
| `useHost` | `"0.0.0.0"` | बाइंड पता |
| `useSslKeyfile`, `useSslCertfile` | `None` | सीधे HTTPS परोसें |
| `useDevTools` | `True` | टूलबार `nexy dev` प्रत्येक पृष्ठ पर जुड़ता है (पृष्ठ जानकारी, मार्ग, त्रुटियां, कॉन्फ़िगरेशन); `False` इसे हटा देता है। उत्पादन में कभी मौजूद नहीं |
| `useWorkers` | `0` | प्रक्रियाएं `nx start` चलती हैं; `0` लिनक्स और मैकओएस पर प्रति सीपीयू एक है, विंडोज़ पर एक है |
| `useCSR` | `False` | क्लाइंट-साइड रूटिंग मोड; `.nexy` मार्ग अक्षम हैं |

## मार्ग

| फ़ील्ड | डिफ़ॉल्ट | अर्थ |
|---|---|---|
| `useRouter` | `None` | एक `APIRouter` उदाहरण या वर्ग फ़ाइल-आधारित मार्गों के बगल में स्थापित; `None` का अर्थ केवल फ़ाइल-आधारित है |
| `excludeDirs` | `["templates", "extension", "docs"]` | मार्गों को स्कैन करते समय निर्देशिकाएं छूट गईं |
| `useAliases` | `None` | उपनाम आयात करें, उदा. `{"@": "src"}` (`@/components/Counter.tsx` का अर्थ है `src/components/Counter.tsx`); `nx new` जिसे आपने चुना है उसे लिखता है, और Vite और `tsconfig.json` उसका अनुसरण करते हैं |

## अग्रभाग

| फ़ील्ड | डिफ़ॉल्ट | अर्थ |
|---|---|---|
| `useFF` | `None` | क्लाइंट फ्रेमवर्क फैक्ट्री: `react()`, `vue()`, `svelte()`, `solid()`, `preact()` |
| `useVite` | `True` | Vite | के साथ क्लाइंट बंडल बनाएं और परोसें
| `useMarkdownExtensions` | `[]` | `.md`/`.mdx` प्रतिपादन के लिए अतिरिक्त एक्सटेंशन |
| `useWatchExtensions` | `None` | डेव सर्वर अतिरिक्त एक्सटेंशन देखता है |
| `useWatchExcludePatterns` | `None` | ग्लोब पैटर्न को डेव सर्वर नजरअंदाज कर देता है |

> **जानकर अच्छा लगा**: `NexyConfigModel` घोषणा करता है `useVite = False`; रनटाइम `Config` डिफ़ॉल्ट `True` है।

## आरक्षित फ़ाइल नाम

प्रत्येक फ़ील्ड आरक्षित भूमिका में एक्सटेंशन जोड़ता है। `useLayoutExtensions = ["md"]` `layout.md` को बिल्कुल `layout.nexy` की तरह आरक्षित बनाता है।

| फ़ील्ड | | में एक्सटेंशन जोड़ता है
|---|---|
| `useLayoutExtensions` | `layout.*` |
| `useNotFoundExtensions` | `notfound.*` |
| `useErrorsExtensions` | `errors.*` |
| `useForbiddenExtensions` | `forbidden.*` |
| `useUnauthorizedExtensions` | `unauthorized.*` |
| `useLoadingExtensions` | `loading.*` |

## एपीआई दस्तावेज़ीकरण

| फ़ील्ड | डिफ़ॉल्ट | अर्थ |
|---|---|---|
| `useDocs` | `True` | OpenAPI स्कीमा और उसके स्केलर संदर्भ पृष्ठ की सेवा करें |
| `useDocsUrl` | `"/docs"` | एपीआई संदर्भ पृष्ठ का पथ |
| `useRedocsUrl` | `"/redocs"` | घोषित किया गया है लेकिन कोई मार्ग तय नहीं किया गया है |
| `useTitle` | `"Nexy App"` | OpenAPI शीर्षक और पृष्ठ शीर्षक (`"Nexy"` में `NexyConfigModel`) |

## मिडलवेयर

| फ़ील्ड | डिफ़ॉल्ट | अर्थ |
|---|---|---|
| `useMiddlewares` | `[]` | एएसजीआई मिडलवेयर क्लासेस |
| `useCORS` | `None` | क्वार्ग्स के लिए `CORSMiddleware` |
| `useGZip` | `None` | क्वार्ग्स के लिए `GZipMiddleware` |
| `useTrustedHost` | `None` | क्वार्ग्स के लिए `TrustedHostMiddleware` |
| `useSession` | `None` | क्वार्ग्स के लिए `SessionMiddleware` |
| `useAuth` | `None` | प्रमाणीकरण मिडलवेयर कॉन्फ़िगरेशन |
| `useHTTPSRedirect` | `False` | HTTP को HTTPS पर रीडायरेक्ट करें |

## Markdown

| फ़ील्ड | डिफ़ॉल्ट | अर्थ |
|---|---|---|
| `useTocDepth` | `"2-6"` | विषय-सूची में शामिल शीर्षक स्तर |
| `useTocTitle` | `"Table of Contents"` | टीओसी शीर्षक |
| `useTocAuto` | `True` | Markdown पृष्ठों के लिए सामग्री तालिका तैयार करें |

## फ़ाइल ट्री के बाहर के रूट

एक FastAPI `APIRouter` बनाएं और इसे `useRouter` के साथ माउंट करें। इसे फ़ाइल-आधारित मार्गों के बगल में परोसा जाता है:

```python filename="nexyconfig.py"
from fastapi import APIRouter
from nexy.core.models import NexyConfigModel

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


class NexyConfig(NexyConfigModel):
    useRouter = router
```

उपरोक्त डिफ़ॉल्ट `nexy/core/config.py` से पढ़े गए हैं।

## घोषित, अभी पढ़ा नहीं

ये फ़ील्ड `NexyConfigModel` में मौजूद हैं लेकिन कोई भी कोड उनका उपभोग नहीं करता है। उन्हें सेट करने से कोई प्रभाव नहीं पड़ता:

`useViteDevUrl`, `useRTL`।

## अगले चरण

- [i18n](../guides/i18n.md): अंतर्राष्ट्रीयकरण
- [फ्रंटएंड](../guides/frontend.md): `useFF` और क्लाइंट बिल्ड
- [तैनाती](../deployment/README.md): उत्पादन विकल्प
