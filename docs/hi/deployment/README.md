# तैनाती

दो आदेश: `nx build` कलाकृतियों का उत्पादन करता है, `nx start` उनकी सेवा करता है।

**शुरू करने से पहले:** एक प्रोजेक्ट जो स्थानीय रूप से `nx build` के साथ बनता है, और - क्लाइंट पेजों के लिए - फ्रंटएंड टूलचेन जिसे `nx new` स्थापित किया गया है।

```bash
nx build
nx start --host 0.0.0.0 --port 8000
```

रनटाइम के लिए केवल Python की आवश्यकता होती है। Uvicorn संकलित ऐप और स्थैतिक संपत्तियों की सेवा करता है; कोई नोड प्रक्रिया और कोई Vite प्रक्रिया शामिल नहीं है।

## बिल्ड क्या उत्पन्न करता है

`__nexy__/` में संकलित रूट मॉड्यूल, `__nexy__/client/` के तहत क्लाइंट बंडल और फ्रेमवर्क रूट के लिए पूर्व-रेंडर HTML शामिल है। प्रोजेक्ट को कॉपी करें - स्रोत प्लस `__nexy__/` - या छवि के अंदर बनाएं।

## Docker

निर्माण चरण के लिए नोड (Vite के लिए) और Python (संकलक के लिए) की आवश्यकता होती है। रनटाइम चरण को केवल Python की आवश्यकता है।

```dockerfile filename="Dockerfile"
FROM node:22-bookworm-slim AS build
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY . .
RUN uv sync --frozen && uv run nx build

FROM python:3.13-slim
WORKDIR /app
COPY --from=build /app /app
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000
CMD ["nx", "start", "--host", "0.0.0.0", "--port", "8000"]
```

`uv` एक प्रबंधित Python लाता है जब आधार छवि में कोई नहीं होता है, यही कारण है कि निर्माण चरण एक नोड छवि से शुरू हो सकता है।

## एक रिवर्स प्रॉक्सी के पीछे

लोकलहोस्ट पर `nx start` चलाएँ और Nginx, Caddy या प्लेटफ़ॉर्म प्रॉक्सी को टीएलएस समाप्त करने दें:

```bash
nx start --host 127.0.0.1 --port 8000
```

सुनिश्चित करें कि यदि आप `SOCKET` हैंडलर का उपयोग करते हैं तो प्रॉक्सी फॉरवर्ड WebSocket अपग्रेड हो जाता है, और यह मूल होस्ट को फॉरवर्ड करता है - FastAPI इससे पूर्ण यूआरएल बनाता है।

### उपपथ के अंतर्गत सेवा करें

`useBasePath` सेट करें जब एप्लिकेशन को डोमेन रूट के बजाय उपसर्ग के तहत प्रकाशित किया जाता है:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useBasePath = "/app"
```

प्रत्येक सार्वजनिक उत्तर तब `/app` के अंतर्गत रहता है: पेज, क्लाइंट नेविगेशन, संपत्ति, सर्वर क्रियाएं, एपीआई दस्तावेज़, साइटमैप और स्वास्थ्य जांच। `/` के लिए एक अनुरोध 404 उत्तर देता है। नेक्सी `app/`, `/app/` और `/app` को एक ही सेटिंग के रूप में स्वीकार करता है और इसे `/app` पर सामान्यीकृत करता है।

रूट फ़ाइलें रूट-सापेक्ष पथ रखती हैं। `/app/about` पर परोसा गया पृष्ठ अभी भी `src/routes/about.tsx` या `about.nexy` है, और आंतरिक पथ `/about` बने हुए हैं। नेक्सी केवल ब्राउज़र पर लिखे गए यूआरएल में उपसर्ग जोड़ता है।

उपसर्ग को अपरिवर्तित अग्रेषित करने के लिए प्रॉक्सी को कॉन्फ़िगर करें, उदाहरण के लिए `/app/...` से `http://127.0.0.1:8000/app/...`। WebSocket उन्नयन के लिए समान उपसर्ग की आवश्यकता होती है। अनुरोध आने के बाद नेक्सी इसे हटा देता है, इसलिए किसी पुनर्लेखन नियम की आवश्यकता नहीं है।

## स्वास्थ्य जांच

<!-- router:fbr,custom -->
एक हैंडलर फ़ाइल जोड़ें, `src/routes/api/health.py`, और जांच करें `/api/health` - एक पृष्ठ के बजाय जो धीरे-धीरे प्रस्तुत हो सकता है:

```python filename="src/routes/api/health.py"
async def GET():
    return {"status": "ok"}
```
<!-- /router -->

<!-- router:modular -->
एक नियंत्रक जोड़ें, और जांच करें `/health/` - एक दृश्य के बजाय जो धीरे-धीरे प्रस्तुत हो सकता है:

```python filename="src/apps/health_controller.py"
from nexy.decorators import Controller


@Controller("/health")
class HealthController:
    async def get(self):
        return {"status": "ok"}
```

इसे रूट मॉड्यूल के `controllers` में सूचीबद्ध करें।
<!-- /router -->

### अंतर्निहित समापनबिंदु

एक लोड बैलेंसर या कुबेरनेट्स दो प्रश्न पूछता है: क्या प्रक्रिया सक्रिय है, और क्या इसे ट्रैफ़िक प्राप्त हो सकता है? सेट `useHealth` और नेक्सी दोनों का उत्तर देती है, बिना किसी हैंडलर फ़ाइल और बिना किसी नियंत्रक के:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useHealth = True
```

| समापन बिंदु | उत्तर 200 | उत्तर 503 |
|---|---|---|
| `GET /health/live` | जबकि प्रक्रिया उत्तर देती है | कभी नहीं |
| `GET /health/ready` | एक बार आवेदन शुरू हो गया है | जब यह शुरू होता है, और एक बार सर्वर इसे रुकने के लिए कहता है |

नेक्सी गारंटी देता है कि `/health/ready` सर्वर के स्टार्टअप और शटडाउन का पालन करता है।

नेक्सी गारंटी देता है कि दोनों एंडपॉइंट एक्सेस लॉग से बाहर और OpenAPI स्कीमा से बाहर रहेंगे।

नेक्सी गारंटी देता है कि दोनों समापन बिंदु `useTrustedHost` और `useHTTPSRedirect` से पहले उत्तर देते हैं, इसलिए पॉड के पते पर HTTP पर भेजी गई जांच को अस्वीकार नहीं किया जाता है।

परंपरा के अनुसार आप अपने स्वयं के मार्गों को `/health/live` और `/health/ready` से दूर रखते हैं जबकि `useHealth` चालू है: नेक्सी के अंतिम बिंदु पहले उत्तर देते हैं। `useHealth` डिफ़ॉल्ट रूप से `False` है, इसलिए एक प्रोजेक्ट जो इसे सेट नहीं करता है वह दोनों पथ रखता है।

आपका एप्लिकेशन यह जाँचने के लिए ज़िम्मेदार है कि यह किस पर निर्भर करता है: `/health/ready` सर्वर के जीवनचक्र की रिपोर्ट करता है, डेटाबेस की स्थिति की नहीं।

कुबेरनेट्स `Deployment` की जांच को उन पर इंगित करें:

```yaml filename="k8s/तैनाती.yaml"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: app
  template:
    metadata:
      labels:
        app: app
    spec:
      containers:
        - name: app
          image: registry.example.com/app:1.0
          ports:
            - containerPort: 8000
          livenessProbe:
            httpGet:
              path: /health/live
              port: 8000
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 8000
            periodSeconds: 5
```

## स्थैतिक होस्टिंग

प्रत्येक पृष्ठ HTML है, लेकिन नेक्सी रूटिंग और एपीआई हैंडलर के लिए एक सर्वर मानता है।

> [!NOTE]
> कोई `--static` बिल्ड मोड नहीं है। `nx build` आउटपुट से आपकी पाइपलाइन में एक विशुद्ध रूप से स्थिर निर्यात उत्पन्न किया जाना है।

## चेकलिस्ट

- [ ] `nx build` सीआई में, उन मार्गों के लिए कोई चेतावनी नहीं है जिन्हें आप सर्वर पर प्रस्तुत करना चाहते हैं
- [ ] `nx start` कोड 1 के साथ बाहर निकलता है, और कुछ भी शुरू नहीं करता है, जब कोई रूट फ़ाइल लोड नहीं हो पाती है
- [ ] `NEXY_ACTION_SECRET` सेट, या `__nexy__/action.key` बिल्ड के साथ रखा गया
- [ ] `useDocs` को `"dev"` पर छोड़ दिया गया है, इसलिए उत्पादन न तो `/docs` और न ही `/openapi.json` पर काम करता है।
- [ ] `useTrustedHost` और `useHTTPSRedirect` सार्वजनिक तैनाती के लिए निर्धारित हैं
- [ ] `useHealth = True` जब कोई लोड बैलेंसर या कुबेरनेट्स ऐप की जांच करता है
- [ ] `__nexy__/` प्रतिबद्ध नहीं

## अगले चरण

- [कॉन्फ़िगरेशन](../reference/config.md): HTTPS, विश्वसनीय होस्ट, सत्र
- [फ्रंटएंड](../guides/frontend.md): Vite क्या बनाता है
- [परीक्षण](../guides/testing.md): सीआई में चलाने के लिए आदेश
