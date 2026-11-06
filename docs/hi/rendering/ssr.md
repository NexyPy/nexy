# एसएसआर (सर्वर रेंडरिंग)

## परिभाषा

SSR डिफ़ॉल्ट है: सर्वर प्रत्येक अनुरोध के लिए पृष्ठ को HTML में प्रस्तुत करता है। कुछ भी इसे सक्षम नहीं करता है, और कोई ध्वज इसे बंद नहीं करता है - एक सर्वर-मोड प्रोजेक्ट हर अनुरोध पर प्रस्तुत होता है जब तक कि कोई पृष्ठ `revalidate` घोषित नहीं करता है।

## यह कैसे काम करता है

<!-- router:fbr,custom -->
| रूट फ़ाइल | HTML क्या उत्पन्न करता है | कब |
|---|---|---|
| `.nexy` | संकलित Python मॉड्यूल, Jinja2 के माध्यम से | हर अनुरोध |
| `.md` | Markdown, फिर निकटतम लेआउट | हर अनुरोध |
| `.mdx`, `.tsx`, `.vue`, `.svelte` | रूपरेखा, नोड में प्रस्तुत की गई | बिल्ड पर जब रूट में कोई लेआउट न हो, अन्यथा ब्राउज़र में |
| `.py` | कुछ नहीं: यह JSON या `Response` लौटाता है | - |

एक Markdown पेज और एक हैंडलर, एक ही प्रोजेक्ट में साथ-साथ:

```md filename="src/routes/changelog.md"
# Changelog

Rendered to HTML on every request, then wrapped in the nearest layout.
```

```python filename="src/routes/api/health.py"
async def GET():
    return {"status": "ok"}
```

घटक मार्ग वह मामला है जिसके लिए दूसरे वाक्य की आवश्यकता होती है। उत्पादन में, एक घटक मार्ग **बिना** एक लेआउट को निर्माण के समय उत्पादित HTML के साथ परोसा जाता है, और घटक इसे हाइड्रेट करता है। किसी लेआउट के साथ, या विकास में, कंटेनर खाली होता है और घटक ब्राउज़र में प्रस्तुत होता है - पृष्ठ तब एक शेल होता है जो स्वयं भर जाता है।

तालिका का घटक मार्ग, बिना किसी लेआउट के, इसलिए उत्पादन बिल्ड से अपना HTML प्रस्तुत करता है:

```tsx filename="src/routes/pricing.tsx"
export default function Pricing() {
  return <h1>Pricing</h1>;
}
```
<!-- /router -->

<!-- router:modular -->
| एक नियंत्रक लौटता है | HTML क्या उत्पन्न करता है | कब |
|---|---|---|
| `useViews("....nexy")` | संकलित Python मॉड्यूल, Jinja2 के माध्यम से | हर अनुरोध |
| एक `dict`, एक सूची, एक मॉडल | कुछ नहीं: FastAPI JSON का उत्तर देता है | - |

एक दृश्य और एक JSON समापन बिंदु, एक ही मॉड्यूल में साथ-साथ:

```nexy filename="src/apps/changelog_view.nexy"
<h1>Changelog</h1>
<p>Rendered to HTML on every request.</p>
```

```python filename="src/apps/site_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/changelog")
class ChangelogController:
    async def get(self):
        return useViews("src/apps/changelog_view.nexy")


@Controller("/api/health")
class HealthController:
    async def get(self):
        return {"status": "ok"}
```
<!-- /router -->

## जीवनचक्र का प्रतिपादन

<!-- router:fbr,custom -->
1. अनुरोध फ़ाइल-आधारित राउटर तक पहुंचता है। पथ का मिलान किया जाता है, और गतिशील खंडों को घटक द्वारा घोषित प्रकारों के अनुसार डाला जाता है।

   ```nexy फ़ाइलनाम='src/routes/orders/[id].nexy'
   ---
   आईडी: प्रोप[int]
   ---
   <h1>आदेश #{{आईडी + 1000 }}</h1>
   ```

   `/orders/42` प्रस्तुत करता है `Order #1042`; `/orders/abc` उत्तर `404`।
2. घटक चलता है. जो नोड पर प्रतीक्षा करता है - एक क्लाइंट दस्तावेज़ - थ्रेड पूल में चलता है, इसलिए यह इवेंट लूप को रोकता नहीं है।
3. शरीर को `text/html` के रूप में प्रवाहित किया जाता है। एक घटक जो टुकड़े उत्पन्न करता है, उन्हें उसी प्रकार प्रवाहित करता है जैसे वह उन्हें बनाता है।
4. ब्राउज़र HTML प्राप्त करता है. द्वीप उनके [निर्देश](islands.md) के अनुसार हाइड्रेट करते हैं।

रेंडरिंग के दौरान उत्पन्न हुई त्रुटि को `errors.nexy` द्वारा एक पृष्ठ में बदल दिया जाता है, जब प्रोजेक्ट में एक त्रुटि होती है: [त्रुटि पृष्ठ](../routing/fbr/errors/README.md) देखें।
<!-- /router -->

<!-- router:modular -->
1. अनुरोध नियंत्रक तक पहुंचता है। इसके पथ पैरामीटर विधि द्वारा घोषित प्रकार के अनुसार डाले जाते हैं, और दृश्य में पास किए जाते हैं:

   ```पायथन फ़ाइल नाम = "src/apps/order_controller.py"
   नेक्सी.डेकोरेटर्स से नियंत्रक आयात करें
   nexy.hooks से उपयोग दृश्य आयात करें


   @नियंत्रक("/आदेश/{id}")
   क्लास ऑर्डरकंट्रोलर:
       async def प्राप्त करें (स्वयं, आईडी: int):
           वापसी उपयोग दृश्य("src/apps/order_view.nexy", context={"id": id})
   ```

   ```nexy फ़ाइलनाम='src/apps/order_view.nexy'
   ---
   आईडी: प्रोप[int]
   ---
   <h1>आदेश #{{आईडी + 1000 }}</h1>
   ```

   `/orders/42/` प्रस्तुत करता है `Order #1042`; `/orders/abc/` उत्तर `404`।
2. दृश्य चलता है, और `useViews` प्रतिक्रिया के रूप में अपना HTML लौटाता है।
3. ब्राउज़र HTML प्राप्त करता है. द्वीप उनके [निर्देश](islands.md) के अनुसार हाइड्रेट करते हैं।

रेंडरिंग के दौरान हुई त्रुटि का उत्तर डिफ़ॉल्ट त्रुटि पृष्ठ से दिया जाता है।
<!-- /router -->

## कब उपयोग करें

- पृष्ठ पाठक के स्वामित्व वाली कोई चीज़ दिखाता है: एक सत्र, एक खाता, एक कार्ट।
- प्रत्येक लोड पर डेटा ताज़ा होना चाहिए।
- जो क्रॉलर JavaScript नहीं चलते, उनके लिए सामग्री HTML में होनी चाहिए।
- पेज को प्रस्तुत करना सस्ता है: एक क्वेरी, एक टेम्पलेट।

पहला मामला, एक पृष्ठ जो सत्र से पाठक का स्वागत करता है। `useSession` `useSession` के सत्र को `nexyconfig.py` में पढ़ता है, जिसके बिना यह विफल हो जाता है:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSession = {"secret_key": "change-me"}
```

<!-- router:fbr,custom -->
```nexy filename="src/routes/account.nexy"
---
from nexy import useSession

user = useSession().get("user", "guest")
---
<h1>Signed in as {{ user }}</h1>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/account_view.nexy"
---
from nexy import useSession

user = useSession().get("user", "guest")
---
<h1>Signed in as {{ user }}</h1>
```
<!-- /router -->

## विन्यास

<!-- router:fbr,custom -->
कोई नहीं. दो रास्ते, और उनके पास एक जैसा अनाज नहीं है:

| एसएसआर को छोड़ने के लिए | ऐसा करो | अनाज |
|---|---|---|
| एक पेज, कैश के साथ | `revalidate = 60` इसके अग्रभाग में → [आईएसआर](isr.md) | पेज |
| संपूर्ण प्रोजेक्ट, क्लाइंट-रूटेड | `useCSR = True` में `nexyconfig.py` → [सीएसआर](csr.md) | प्रोजेक्ट |

`nexyconfig.py` में प्रोजेक्ट-व्यापी स्विच। क्लाइंट मोड को क्लाइंट फ़्रेमवर्क की आवश्यकता होती है:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```
<!-- /router -->

<!-- router:modular -->
कोई नहीं. प्रत्येक अनुरोध पर नियंत्रक द्वारा दिए गए प्रत्येक दृश्य को प्रस्तुत किया जाता है: [ISR](isr.md) और [CSR](csr.md) फ़ाइल-आधारित राउटर के मोड हैं।
<!-- /router -->

## उदाहरण

<!-- router:fbr,custom -->
```nexy filename="src/routes/blog/[slug].nexy"
---
slug: prop[str] = "untitled"
---
<h1>{{ slug }}</h1>
```

`GET /blog/hello` इस टेम्पलेट को एक बार चलाता है, `slug` को `hello` पर सेट करके। दूसरा अनुरोध इसे फिर से चलाता है: दोनों के बीच कुछ भी नहीं रखा जाता है। क्वेरी स्ट्रिंग एक प्रोप नहीं है - इसे [नेविगेशन](../routing/fbr/navigation/hooks.md) में हुक के साथ पढ़ें।
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/blog_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/blog/{slug}")
class PostController:
    async def get(self, slug: str):
        return useViews("src/apps/post_view.nexy", context={"slug": slug})
```

```nexy filename="src/apps/post_view.nexy"
---
slug: prop[str] = "untitled"
---
<h1>{{ slug }}</h1>
```

`GET /blog/hello/` इस दृश्य को एक बार चलाता है, `slug` को `hello` पर सेट करके। दूसरा अनुरोध इसे फिर से चलाता है: दोनों के बीच कुछ भी नहीं रखा जाता है। क्वेरी स्ट्रिंग एक प्रोप नहीं है - इसे `useSearchParams` के साथ पढ़ें।
<!-- /router -->

## सीमाएँ

- **प्रति अनुरोध एक रेंडर।** एक ही सेकंड में दो विज़िटर रेंडर और उसके पीछे के प्रश्नों के लिए भुगतान करते हैं।
- **कोई कैश नहीं।** वार्म करने के लिए कोई साझा प्रतिक्रिया कैश नहीं है: फ़ाइल मार्गों के साथ, [आईएसआर](isr.md) प्रति यूआरएल एक जोड़ता है।
- **स्ट्रीमिंग केवल उस घटक की मदद करती है जो परिणाम देता है।** पृष्ठ के शीर्ष पर एक धीमी क्वेरी अभी भी पहले बाइट में देरी करती है।
- **कोई स्थिर आउटपुट नहीं।** सर्वर मोड में बिल्ड पर कुछ भी फ़्रीज़ नहीं होता है: कोई एसएसजी मोड नहीं है, और कोई निर्यात कमांड नहीं है। [रेंडरिंग](README.md) देखें।
- **`.nexy` टेम्प्लेट में ऑटोएस्केपिंग बंद है**। `| e` के साथ अविश्वसनीय मूल्यों से बचें।

<!-- router:fbr,custom -->
```nexy filename="src/routes/search.nexy"
---
from nexy import useSearchParams

q = useSearchParams().get("q", "")
---
<p>Results for {{ q | e }}</p>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/search_view.nexy"
---
from nexy import useSearchParams

q = useSearchParams().get("q", "")
---
<p>Results for {{ q | e }}</p>
```
<!-- /router -->

## अगले चरण

<!-- router:fbr,custom -->
- [आईएसआर](isr.md): इस पेज को प्रति यूआरएल कैश करें
<!-- /router -->
- [द्वीप](islands.md): एसएसआर रखें और एक विजेट को इंटरैक्टिव बनाएं
<!-- router:fbr,custom -->
- [सीएसआर](csr.md): ब्राउज़र पर हाथ से नेविगेशन
<!-- /router -->
- [प्रदर्शन](../deployment/performance.md)
