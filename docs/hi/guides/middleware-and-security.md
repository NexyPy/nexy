# मिडिलवेयर और सुरक्षा

नेक्सी फास्टएपीआई और स्टारलेट पर चलती है, इसलिए उनका मिडलवेयर लागू होता है। आम लोग एक पंक्ति में हैं
`nexyconfig.py`.

```python filename=""
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

प्रत्येक `use*` शब्दकोष को मेल खाने वाले स्टारलेट मिडलवेयर में कीवर्ड तर्क के रूप में पारित किया जाता है:
`CORSMiddleware`, `GZipMiddleware`, `TrustedHostMiddleware`, `SessionMiddleware`।

## आपका अपना मिडलवेयर

```python filename=""
from my_app.middleware import RequestIdMiddleware


class NexyConfig(NexyConfigModel):
    useMiddlewares = [RequestIdMiddleware]
```

`useMiddlewares` एएसजीआई मिडलवेयर कक्षाएं लेता है।

## एचटीटीपीएस

`useSslKeyfile` और `useSslCertfile` के साथ सीधे HTTPS परोसें, या रिवर्स प्रॉक्सी पर TLS समाप्त करें
और सेट करें `useHTTPSRedirect`। विकास में वाइट देव सर्वर लूपबैक HTTP के पीछे रहता है
नेक्सी मूल, इसलिए टीएलएस उस तक कभी नहीं पहुंचता।

## उत्पादन चेकलिस्ट

- `useDocs = False` यदि ओपनएपीआई स्कीमा सार्वजनिक नहीं होनी चाहिए।
- `useTrustedHost` होस्ट-हेडर हमलों को रोकने के लिए, आपके डोमेन पर सेट करें।
- `useCORS` स्पष्ट मूल के साथ, कभी भी `["*"]` प्रमाण-पत्रों के साथ नहीं।
- सत्रों के लिए एक वास्तविक `secret_key`, परिवेश से पढ़ें।
- क्लाइंट घटकों को दिए गए प्रॉप्स HTML-नेक्सी द्वारा छोड़े गए हैं। उपयोगकर्ता इनपुट को `| safe` में चिह्नित न करें
  टेम्पलेट्स.

## रक्षक और निर्भरताएँ

प्रति-मार्ग सुरक्षा फास्टएपीआई निर्भरता का उपयोग करती है। मार्ग निर्देशिका में एक `dependencies.py` लागू होता है
इसके नीचे सब कुछ: देखें [निर्भरताएं](../routing/fbr/dependencies/README.md)। मॉड्यूलर राउटर में उपयोग करें
[`@UseGuard`](../routing/modular/guards-and-metadata.md)।

## अगले चरण

- [कॉन्फिग](../reference/config.md): प्रत्येक मिडलवेयर फ़ील्ड
- [तैनाती](../deployment/README.md)
- [प्रदर्शन](../deployment/performance.md)