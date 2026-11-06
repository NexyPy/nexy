# विरासत

`src/routes/` में कई फ़ाइलें उनकी निर्देशिका के नीचे मौजूद सभी चीज़ों पर लागू होती हैं। वे सभी एक ही तरह से हल करते हैं: नेक्सी मार्ग की निर्देशिका से शुरू होती है और `src/routes/` तक चलती है।

```text
src/routes/
├─ layout.nexy               1. outermost
├─ dependencies.py           1. runs first
├─ middleware.py             1. wraps first
├─ notfound.nexy             fallback for every URL
├─ (shop)/                   a group is a directory: it takes part, it is not in the URL
│  ├─ layout.nexy            2.
│  ├─ dependencies.py        2.
│  └─ cart/
│     ├─ layout.nexy         3. innermost
│     ├─ dependencies.py     3. runs last
│     └─ index.nexy          the page
```

| फ़ाइल | नियम |
|---|---|
| `layout.nexy`, `layout.tsx`, `layout.vue`, `layout.svelte` | जड़ से पृष्ठ तक प्रत्येक लेआउट इसे लपेटता है, **सबसे पहले सबसे बाहरी** |
| `middleware.py` | रूट से रूट तक प्रत्येक फ़ाइल अनुरोध को लपेटती है, **सबसे पहले**, निर्भरता से पहले |
| `dependencies.py` | रूट से रूट तक प्रत्येक फ़ाइल चलती है, **पहले सबसे बाहरी**, फिर हैंडलर के अपने गार्ड |
| `notfound.nexy`, `errors.nexy` | **निकटतम** स्थिति कोड के अनुसार, कोई जीतता है |

उपरोक्त पृष्ठ के लिए, लेआउट `root layout > (shop) layout > cart layout > page` के रूप में चलते हैं, और निर्भरताएँ `root > (shop) > cart > handler guards` के रूप में चलती हैं।

## सबसे पहले सबसे बाहरी क्यों

एक बाहरी लेआउट फ्रेम खींचता है और एक बाहरी निर्भरता यह तय करती है कि कौन अंदर आ सकता है। उन्हें पहले रखने का मतलब है कि आंतरिक लोग उन पर भरोसा कर सकते हैं: एक निर्देशिका जिसे प्रमाणीकरण की आवश्यकता होती है वह उपयोगकर्ता को पढ़ने वाले हैंडलर से पहले चलती है।

`(shop)` पेड़ की निर्भरता कार्ट कुकी की जांच करती है, इसलिए इसके नीचे की कार्ट निर्भरता दोबारा जांच किए बिना कार्ट को पढ़ सकती है:

```python filename="src/routes/(दुकान)/निर्भरता.py"
from nexy.http import HTTPException, Request


def require_cart(request: Request) -> None:
    if "cart" not in request.cookies:
        raise HTTPException(status_code=400, detail="No cart")


dependencies = [require_cart]
```

## लेआउट

फ़ोल्डर परिवार स्टैक की सभी लेआउट फ़ाइलें: [लेआउट](layouts/README.md) देखें। विभिन्न परिवार मिश्रण नहीं करते हैं: एक `layout.vue` कभी भी `.tsx` पेज को लपेटता नहीं है, और एक प्रोजेक्ट में या तो `layout.nexy` या क्लाइंट लेआउट होते हैं, कभी भी दोनों ([मोड](modes.md)) नहीं होते हैं।

पेड़ का सबसे भीतरी लेआउट केवल अपना स्वयं का फ्रेम जोड़ता है: इसके चारों ओर का रूट लेआउट अभी भी दस्तावेज़ खींचता है।

```nexy filename="src/routes/(दुकान)/cart/layout.nexy"
---
children: prop[NexyElement]
---
<section class="cart">
  <h2>Your cart</h2>
  {{ children | safe }}
</section>
```

## मिडलवेयर फ़ाइलें

[मिडिलवेयर फ़ाइलें](middleware/README.md) देखें: वे निर्भरता से पहले चलती हैं और रूट तक पहुंचे बिना उत्तर दे सकती हैं।

एक जड़ `middleware.py` पेड़ के हर मार्ग को लपेटती है, गाड़ी में शामिल हैं:

```python filename="src/routes/middleware.py"
import time

from nexy.http import Request


async def middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["x-time-ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"
    return response
```

## निर्भरताएँ

`@UseGuard` और `@Middleware` सहित हैंडलर फ़ाइल में ऑर्डर के लिए [निर्भरताएं](dependencies/README.md) देखें।

## त्रुटि पृष्ठ

`notfound.nexy` और `errors.nexy` रूट रूट पर एक बार स्थापित होते हैं; उपनिर्देशिका में एक प्रतिलिपि उस उपसर्ग के लिए पृष्ठ को परिष्कृत करती है। [त्रुटि पृष्ठ](errors/README.md) देखें।

`cart/` में एक प्रति `/cart` के अंतर्गत 404 का उत्तर देती है, और मूल बाकी को रखता है:

```nexy filename="src/routes/(दुकान)/cart/notfound.nexy"
<h1>This product is gone</h1>
<p><a href="/cart">Back to your cart</a></p>
```

## अगले चरण

- [लेआउट](layouts/README.md)
- [निर्भरताएँ](dependencies/README.md)
- [त्रुटि पृष्ठ](errors/README.md)
