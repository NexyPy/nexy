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

## HTTPS

HTTPS को सीधे `useSslKeyfile` और `useSslCertfile` के साथ परोसें, या रिवर्स प्रॉक्सी पर टीएलएस को समाप्त करें और `useHTTPSRedirect` सेट करें। विकास में Vite डेव सर्वर नेक्सी मूल के पीछे लूपबैक HTTP पर रहता है, इसलिए टीएलएस कभी भी उस तक नहीं पहुंचता है।

## उत्पादन चेकलिस्ट

- `useDocs = False` यदि OpenAPI स्कीमा सार्वजनिक नहीं होनी चाहिए।
- `useTrustedHost` होस्ट-हेडर हमलों को रोकने के लिए, आपके डोमेन पर सेट करें।
- `useCORS` स्पष्ट मूल के साथ, कभी भी `["*"]` प्रमाण-पत्रों के साथ नहीं।
- सत्रों के लिए एक वास्तविक `secret_key`, परिवेश से पढ़ें।
- क्लाइंट घटकों को दिए गए प्रॉप्स Nexy द्वारा HTML-एस्केप किए गए हैं। टेम्प्लेट में उपयोगकर्ता इनपुट `| safe` को चिह्नित न करें।

## रक्षक और निर्भरताएँ

प्रति-मार्ग सुरक्षा FastAPI निर्भरता का उपयोग करती है। रूट निर्देशिका में एक `dependencies.py` इसके नीचे की हर चीज़ पर लागू होता है: [निर्भरताएं](../routing/fbr/dependencies/README.md) देखें। मॉड्यूलर राउटर में [`@UseGuard`](../routing/modular/guards-and-metadata.md) का उपयोग करें।

## अगले चरण

- [कॉन्फ़िगर](../reference/config.md): प्रत्येक मिडलवेयर फ़ील्ड
- [तैनाती](../deployment/README.md)
- [प्रदर्शन](../deployment/performance.md)
