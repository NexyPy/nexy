# हुक

हुक्स वर्तमान HTTP अनुरोध को `.nexy` पेज, एपीआई हैंडलर या मॉड्यूलर नियंत्रक के अंदर से पढ़ते हैं। उनके नाम क्लाइंट राउटर (`@nexy/client`) के हुक से मेल खाते हैं जहां वे वही काम करते हैं।

> [!NOTE]
> हुक केवल तभी काम करते हैं जब अनुरोध संभाला जा रहा हो। किसी को कहीं और बुलाने से `RuntimeError` बढ़ जाता है।

## हुक

| हुक | रिटर्न |
|---|---|
| `usePathname()` | अनुरोध पथ, उदा. `"/blog/post-1"` |
| `useSearchParams()` | `dict[str, str]` के रूप में क्वेरी स्ट्रिंग, प्रति कुंजी पहला मान |
| `useParams()` | गतिशील पथ पैरामीटर, उदा. `{"slug": "post-1"}` |
| `useQuery()` | `useParams()` का मूल नाम, मौजूदा पृष्ठों के लिए रखा गया है |
| `useRequest()` | Starlette अनुरोध, अन्य हुक में क्या शामिल नहीं है |
| `useHeaders()` | अनुरोध शीर्षलेख `dict[str, str]`, छोटे अक्षरों में नाम |
| `useUrl()` | पूरा यूआरएल: `.scheme`, `.hostname`, `.port`, `.path`, `.query` |
| `useIsActive(href, exact=False)` | क्या `href` वर्तमान पृष्ठ है या उसके माता-पिता में से एक है |
| `useRouter()` | `{"path", "base_url", "url_for"}` |
| `useCookies()` | सभी कुकीज़ `dict[str, str]` के रूप में |
| `useSession()` | सत्र निर्देश, `{}` जब सत्र सक्षम नहीं होते हैं |
| `useToc(depth_range="2-6")` | वर्तमान पृष्ठ के लिए सामग्री तालिका HTML, `""` जब कोई नहीं |
| `useViews(path, context=None)` | एक और दृश्य प्रस्तुत करता है और एक `HTMLResponse` लौटाता है |

## अनुरोध पढ़ें

```nexy filename="src/routes/index.nexy"
---
from nexy import useCookies, usePathname, useSearchParams

pathname = usePathname()
page = useSearchParams().get("page", "1")
theme = useCookies().get("theme", "light")
---
<p>{{ pathname }} - page {{ page }} - {{ theme }} theme</p>
```

## नेविगेशन बार में एक सक्रिय लिंक

`useIsActive` क्लाइंट के समान नियम का पालन करता है: क्वेरी स्ट्रिंग, खंड और एक अनुगामी स्लैश को नजरअंदाज कर दिया जाता है, माता-पिता का लिंक उसके बच्चों पर तब तक सक्रिय रहता है जब तक कि `exact` सेट नहीं किया जाता है, और `/` केवल `/` पर सक्रिय होता है।

```nexy filename="src/components/NavLink.nexy"
---
from nexy import useIsActive

href: prop[str]
label: prop[str]
---
<a href="{{ href }}"{% if useIsActive(href) %} aria-current="page"{% endif %}>{{ label }}</a>
```

## टिप्पणियाँ

- `useQuery()` **पथ** पैरामीटर लौटाता है, क्वेरी स्ट्रिंग नहीं, यही कारण है कि `useParams()` मौजूद है। क्वेरी स्ट्रिंग `useSearchParams()` है।
- `useRouter()` यहां अनुरोध हुक है। यह `useRouter` कॉन्फ़िगरेशन फ़ील्ड नहीं है जो `APIRouter` को माउंट करता है।
- `useSession()` को `nexyconfig.py` में `useSession = {...}` की आवश्यकता है; इसके बिना तानाशाही खाली है.
- `useViews("about.tsx", {"title": "About"})` HTML लौटाता है: एक `.nexy` दृश्य इसके संकलित मॉड्यूल द्वारा प्रस्तुत किया जाता है, एक `.tsx`/`.jsx`/`.vue`/`.svelte`/`.mdx` दृश्य क्लाइंट माउंट कंटेनर बन जाता है।

## अगले चरण

- [पेज](../pages/README.md): गतिशील खंड और लेआउट
- [रेसिपी](../../../guides/recipes.md): `useSession()` पर निर्मित एक परीक्षणित साइन-इन प्रवाह
- [कॉन्फ़िगर](../../../reference/config.md): सत्र और स्थान सक्षम करें
- [.nexy फ़ाइलें](../../../views/nexy/README.md): जहां आमतौर पर हुक कहा जाता है
