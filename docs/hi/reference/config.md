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

| मैदान | डिफ़ॉल्ट | मतलब |
|---|---|---|
| `usePort` | `3000` | `dev` और `start` के लिए पोर्ट |
| `useHost` | `"0.0.0.0"` | बाइंड एड्रेस |
| `useSslKeyfile`, `useSslCertfile` | `None` | सीधे HTTPS परोसें |
| `useDevTools` | `True` | टूलबार `nexy dev` प्रत्येक पृष्ठ पर जुड़ता है (पृष्ठ जानकारी, मार्ग, त्रुटियाँ, कॉन्फ़िगरेशन); `False` इसे हटा देता है। उत्पादन में कभी मौजूद नहीं |
| `useHealth` | `False` | लोड बैलेंसर्स और कुबेरनेट्स जांच के लिए `GET /health/live` और `GET /health/ready` परोसें; देखें [तैनाती](../deployment/README.md#built-in-endpoints) |
| `useMaxBodySize` | `1048576` | एक कार्यकर्ता द्वारा पढ़ा जाने वाला सबसे बड़ा अनुरोध निकाय, बाइट्स में (1 MiB); बड़ा वाला एक `413` है, और `0` सीमा को बंद कर देता है। फ़ाइल अपलोड करने वाले रूट के लिए इसे बढ़ाएं |
| `useSiteUrl` | `None` | साइट का सार्वजनिक मूल, जैसे कि `"https://example.com"`; एक बार सेट हो जाने पर, नेक्सी `/sitemap.xml` और `/robots.txt` परोसता है। [साइटमैप और robots.txt](../guides/sitemap.md) देखें |
| `useWorkers` | `0` | प्रक्रियाएँ `nx start` चलती हैं; `0` लिनक्स और मैकओएस पर प्रति सीपीयू एक है, विंडोज़ पर एक |
| `useCSR` | `False` | क्लाइंट-साइड रूटिंग मोड; `.nexy` मार्ग अक्षम हैं |
| `useBasePath` | `None` | संपूर्ण एप्लिकेशन के लिए सार्वजनिक उपसर्ग, जैसे `"/app"`; इसके बाहर के अनुरोध 404 का उत्तर देते हैं, और उत्पन्न लिंक, क्लाइंट रूट, एक्शन कॉल और संपत्तियां उपसर्ग ले जाती हैं। देखें [तैनाती](../deployment/README.md#serve-under-a-sub-path) |
| `useImageWidths` | `[320, 640, 960, 1280]` | पिक्सेल चौड़ाई `nx build` स्थानीय छवियों के लिए उत्पन्न होती है; रूपांतरण के लिए `Pillow` की आवश्यकता होती है, और इसके बिना छवियां अपना मूल यूआरएल बनाए रखती हैं। देखें [छवि](../routing/fbr/navigation/linking-and-navigating.md#image) |

## डेटाबेस

| मैदान | डिफ़ॉल्ट | मतलब |
|---|---|---|
| `useORM` | `None` | परियोजना का ORM: `"SQLModel"`, `"SQLAlchemy"` या `"Tortoise-ORM"`। `nx new` इसे लिखता है, और `nx migrate` इसमें से Alembic या Aerich चुनता है; इसके बिना, `nx migrate` पहला ORM इंस्टाल करता है। देखें [डेटाबेस](../guides/databases.md#migrations) |

## मार्ग

| मैदान | डिफ़ॉल्ट | मतलब |
|---|---|---|
| `useRouter` | `None` | फ़ाइल-आधारित मार्गों के बगल में स्थापित एक `APIRouter` उदाहरण या वर्ग; `None` का अर्थ केवल फ़ाइल-आधारित है |
| `excludeDirs` | `["templates", "extension", "docs"]` | मार्गों को स्कैन करते समय निर्देशिकाएँ छूट गईं |
| `useAliases` | `None` | उपनाम आयात करें, उदा. `{"@": "src"}` (`@/components/Counter.tsx` का अर्थ है `src/components/Counter.tsx`); `nx new` जिसे आपने चुना है उसे लिखता है, और Vite और `tsconfig.json` उसका अनुसरण करते हैं |

## अग्रभाग

| मैदान | डिफ़ॉल्ट | मतलब |
|---|---|---|
| `useFF` | `None` | क्लाइंट फ्रेमवर्क फ़ैक्टरी: `react()`, `vue()`, `svelte()`, `solid()`, `preact()` |
| `useVite` | `True` | Vite के साथ क्लाइंट बंडल बनाएं और परोसें |
| `useMarkdownExtensions` | `[]` | `.md`/`.mdx` प्रतिपादन के लिए अतिरिक्त एक्सटेंशन |
| `useWatchExtensions` | `None` | डेव सर्वर अतिरिक्त एक्सटेंशन देखता है |
| `useWatchExcludePatterns` | `None` | ग्लोब पैटर्न को डेव सर्वर अनदेखा कर देता है |

> **जानकर अच्छा लगा**: `NexyConfigModel` घोषणा करता है `useVite = False`; रनटाइम `Config` डिफ़ॉल्ट `True` है।

## आरक्षित फ़ाइल नाम

प्रत्येक फ़ील्ड आरक्षित भूमिका में एक्सटेंशन जोड़ता है। `useLayoutExtensions = ["md"]` `layout.md` को बिल्कुल `layout.nexy` की तरह आरक्षित बनाता है।

| मैदान | में एक्सटेंशन जोड़ता है |
|---|---|
| `useLayoutExtensions` | `layout.*` |
| `useNotFoundExtensions` | `notfound.*` |
| `useErrorsExtensions` | `errors.*` |
| `useForbiddenExtensions` | `forbidden.*` |
| `useUnauthorizedExtensions` | `unauthorized.*` |
| `useLoadingExtensions` | `loading.*` |

## एपीआई दस्तावेज़ीकरण

| मैदान | डिफ़ॉल्ट | मतलब |
|---|---|---|
| `useDocs` | `"dev"` | जहां स्केलर संदर्भ पृष्ठ और `/openapi.json` परोसे जाते हैं: `"dev"` केवल `nx dev` पर, `True` उत्पादन में भी (स्कीमा हर मार्ग और सर्वर कार्रवाई को सूचीबद्ध करता है), `False` कहीं नहीं |
| `useDocsUrl` | `"/docs"` | एपीआई संदर्भ पृष्ठ का पथ |
| `useRedocsUrl` | `"/redocs"` | घोषित किया गया है लेकिन कोई रूट तय नहीं किया गया है |
| `useTitle` | `"Nexy App"` | OpenAPI शीर्षक और पृष्ठ शीर्षक (`"Nexy"` में `NexyConfigModel`) |

### परियोजना के एक पृष्ठ के लिए निःशुल्क `/docs`

एपीआई संदर्भ किसी भी मार्ग से पहले `/docs` उत्तर देता है, इसलिए `src/routes/docs.nexy` या `src/routes/docs/[[...slug]].nexy` वहां कभी नहीं परोसा जाता है। `nx dev` और `nx start` स्टार्टअप पर ऐसे पेज को नाम दें। `useDocsUrl` के साथ संदर्भ को स्थानांतरित करें:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useDocsUrl = "/api-reference"
```

या इसे `useDocs = False` से बंद कर दें, जिससे `/openapi.json` की सेवा भी बंद हो जाती है। जब संदर्भ चालू हो, तो प्रोजेक्ट के मार्गों को उस पथ से दूर रखें।

## मिडलवेयर

| मैदान | डिफ़ॉल्ट | मतलब |
|---|---|---|
| `useMiddlewares` | `[]` | एएसजीआई मिडलवेयर क्लासेस |
| `useCORS` | `None` | `CORSMiddleware` के लिए क्वार्ग्स |
| `useGZip` | `None` | `GZipMiddleware` के लिए क्वार्ग्स |
| `useTrustedHost` | `None` | `TrustedHostMiddleware` के लिए क्वार्ग्स |
| `useSession` | `None` | `SessionMiddleware` के लिए क्वार्ग्स |
| `useAuth` | `None` | प्रमाणीकरण मिडलवेयर कॉन्फ़िगरेशन |
| `useHTTPSRedirect` | `False` | HTTP को HTTPS पर रीडायरेक्ट करें |

## Markdown

| मैदान | डिफ़ॉल्ट | मतलब |
|---|---|---|
| `useTocDepth` | `"2-6"` | सामग्री की तालिका में शामिल शीर्षक स्तर |
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
- [परिनियोजन](../deployment/README.md): उत्पादन विकल्प
