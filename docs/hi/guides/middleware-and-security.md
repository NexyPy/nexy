# मिडलवेयर और सुरक्षा

नेक्सी FastAPI और Starlette पर चलता है, इसलिए उनका मिडलवेयर लागू होता है। आम लोग `nexyconfig.py` में एक पंक्ति हैं।

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {
        "allow_origins": ["https://app.example.com"],
        "allow_methods": ["GET", "POST"],
        "allow_credentials": True,
    }
    useGZip = {"minimum_size": 1000}
    useTrustedHost = {"allowed_hosts": ["example.com", "*.example.com"]}
    useHTTPSRedirect = True
    useSession = {"secret_key": "change-me"}
```

प्रत्येक `use*` शब्दकोश को मिलान करने वाले Starlette मिडलवेयर के लिए कीवर्ड तर्क के रूप में पारित किया जाता है: `CORSMiddleware`, `GZipMiddleware`, `TrustedHostMiddleware`, `SessionMiddleware`।

## आपका अपना मिडलवेयर

```python filename="nexyconfig.py"
from my_app.middleware import RequestIdMiddleware


class NexyConfig(NexyConfigModel):
    useMiddlewares = [RequestIdMiddleware]
```

`useMiddlewares` एएसजीआई मिडलवेयर कक्षाएं लेता है।

## दर सीमित करना

`useRateLimit` उस ग्राहक के पते पर `429 Too Many Requests` उत्तर देता है जो `per` सेकंड की एक विंडो में `requests` से अधिक अनुरोध भेजता है।

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useRateLimit = {"requests": 60, "per": 60, "paths": ["/api/", "/_nx_"]}
```

नेक्सी गारंटी देता है कि सीमा से अधिक के अनुरोध को `Retry-After` हेडर के साथ एक `429` मिलता है, विंडो में बचे सेकंड, और कभी भी आपके मार्गों, कार्यों या मिडलवेयर तक नहीं पहुंचते हैं।

नेक्सी गारंटी देता है कि `useRateLimit` के बिना कोई दर सीमा मिडलवेयर नहीं जोड़ा जाएगा।

नेक्सी गारंटी देता है कि `useHealth` जांच कभी भी सीमित नहीं होती है।

`paths` वैकल्पिक है: इसके बिना हर रास्ता सीमित है। सर्वर क्रियाएँ `/_nx_` के अंतर्गत प्रस्तुत की जाती हैं, ताकि उपसर्ग उन सभी को सीमित कर दे।

विंडो को ठीक कर दिया गया है और सभी ग्राहकों द्वारा साझा किया गया है: `per` सेकंड के प्रत्येक गुणज पर गिनती फिर से शुरू होती है। इसलिए एक ग्राहक एक विंडो के किनारे तक दो बार `requests` भेज सकता है।

गिनती प्रत्येक कार्यकर्ता की स्मृति में रहती है। उपरोक्त `useWorkers` के साथ, एक ग्राहक प्रत्येक कार्यकर्ता को `requests` भेज सकता है, और सर्वर पुनरारंभ होने पर गिनती फिर से शुरू हो जाती है।

ग्राहक का पता वह है जो यूविकॉर्न अनुरोध देता है। उसी मशीन पर रिवर्स प्रॉक्सी के पीछे, यूविकॉर्न इसे `X-Forwarded-For` से पढ़ता है; किसी अन्य मशीन पर प्रॉक्सी के लिए, उसका पता `FORWARDED_ALLOW_IPS` पर्यावरण चर में सूचीबद्ध करें, या प्रत्येक ग्राहक प्रॉक्सी का पता साझा करता है।

आपका एप्लिकेशन कई श्रमिकों या सर्वरों द्वारा साझा की गई सीमा के लिए जिम्मेदार है: एक रिवर्स प्रॉक्सी या रेडिस जैसा स्टोर।

## HTTPS

HTTPS को सीधे `useSslKeyfile` और `useSslCertfile` के साथ परोसें, या रिवर्स प्रॉक्सी पर टीएलएस को समाप्त करें और `useHTTPSRedirect` सेट करें। विकास में Vite डेव सर्वर नेक्सी मूल के पीछे लूपबैक HTTP पर रहता है, इसलिए टीएलएस कभी भी उस तक नहीं पहुंचता है।

## उत्पादन चेकलिस्ट

- `useDocs = False` यदि OpenAPI स्कीमा सार्वजनिक नहीं होनी चाहिए।
- `useTrustedHost` होस्ट-हेडर हमलों को रोकने के लिए, आपके डोमेन पर सेट करें।
- `useCORS` स्पष्ट मूल के साथ, कभी भी `["*"]` प्रमाण-पत्रों के साथ नहीं।
- सत्रों के लिए एक वास्तविक `secret_key`, परिवेश से पढ़ें।
- Props क्लाइंट घटकों को पास किया गया HTML Nexy द्वारा बच गया है। टेम्प्लेट में उपयोगकर्ता इनपुट `| safe` को चिह्नित न करें।

## रक्षक और निर्भरताएँ

प्रति-मार्ग सुरक्षा FastAPI निर्भरता का उपयोग करती है। रूट निर्देशिका में एक `dependencies.py` इसके नीचे की हर चीज़ पर लागू होता है: [निर्भरताएं](../routing/fbr/dependencies/README.md) देखें। मॉड्यूलर राउटर में [`@UseGuard`](../routing/modular/guards-and-metadata.md) का उपयोग करें।

## अगले चरण

- [कॉन्फ़िग](../reference/config.md): प्रत्येक मिडलवेयर फ़ील्ड
- [तैनाती](../deployment/README.md)
- [प्रदर्शन](../deployment/performance.md)
