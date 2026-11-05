# मॉड्यूलर रूटिंग

मॉड्यूलर रूटिंग `src/routes/` के अंतर्गत फ़ाइलों के बजाय डेकोरेटर वाले वर्गों का उपयोग करती है: नियंत्रक अनुरोधों को संभालते हैं, मॉड्यूल उन्हें समूहित करते हैं, और प्रदाताओं को इंजेक्ट किया जाता है। परिणामी `APIRouter` को `useRouter` के साथ `nexyconfig.py` में माउंट करें।

**शुरू करने से पहले:** एक नेक्सी प्रोजेक्ट और एक कार्यशील पृष्ठ। मॉड्यूलर राउटर फ़ाइल-आधारित राउटर को प्रतिस्थापित करता है, इसलिए यदि आपने अभी तक राउटर नहीं चुना है तो पहले [रूटिंग](../README.md) पढ़ें।

| पृष्ठ | इसमें क्या शामिल है |
|---|---|
| यह पृष्ठ | एक मॉड्यूल माउंट करें, एक नियंत्रक लिखें, समूह नियंत्रक |
| [निर्भरता इंजेक्शन](dependency-injection.md) | `@Injectable`, स्कोप, कंटेनर |
| [गार्ड और मेटाडेटा](guards-and-metadata.md) | `@UseGuard`, `@Middleware`, `@UseRoute`, `@UseResponse` |
| [नेक्सी और NestJS](vs-nestjs.md) | क्या मेल खाता है NestJS और क्या नहीं |

## राउटर सेट करें

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

> [!NOTE]
> फ़ाइल-आधारित रूटिंग कार्य करती रहती है. यदि `src/routes/` मौजूद है, तो इसे `useRouter` सेट होने पर भी स्कैन किया जाता है।

## एक नियंत्रक लिखें

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.core.types import JsonResponse


@Controller()
class AppController:
    async def get(self) -> JsonResponse:
        return {"message": "Welcome to Nexy Modular API"}
```

विधियाँ नाम के अनुसार, केस-असंवेदनशील रूप से मेल खाती हैं: `get`, `post`, `put`, `patch`, `delete`, `options`, `head`, `trace`।

एक नियंत्रक प्रति HTTP विधि एक हैंडलर घोषित करता है; स्टार्टअप पर एक डुप्लिकेट बढ़ता है। `@Controller(prefix="/users")` के साथ एक उपसर्ग जोड़ें - प्रत्येक हैंडलर `prefix/` पर आरूढ़ है। `async def SOCKET(...)` एक नियंत्रक पर उसी पथ पर एक WebSocket पंजीकृत करता है।

## एक मॉड्यूल में समूह नियंत्रक

```python filename="src/apps/app_module.py"
from nexy.decorators import Module
from .app_controller import AppController


@Module()
class AppModule:
    controllers = [AppController]
```

`@Module(prefix="/api")` एक `APIRouter` लौटाता है। `controllers` आवश्यक है; `providers`, `imports` और `exports` वैकल्पिक हैं। आयातित मॉड्यूल को उप-राउटर के रूप में माउंट किया जाता है, और उनके निर्यातित प्रदाताओं को स्टार्टअप पर हल किया जाता है।

## एक नियंत्रक से दृश्य

एक नियंत्रक एक पृष्ठ वापस कर सकता है। `useViews` एक `.nexy` दृश्य प्रस्तुत करता है; इसे एक लेआउट में लपेटने के लिए एक को दूसरे के अंदर घोंसला बनाएं:

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller()
class AppController:
    async def get(self):
        return useViews("src/apps/layout.nexy", context={
            "children": useViews("src/apps/app_view.nexy"),
        })
```

[लेआउट](../fbr/layouts/README.md) देखें।

## उदाहरण

`examples/Modular/api/minimal/` देखें।

## अगले चरण

- [निर्भरता इंजेक्शन](dependency-injection.md): सेवाएँ और दायरे
- [गार्ड और मेटाडेटा](guards-and-metadata.md): मार्गों की सुरक्षा और दस्तावेज़ीकरण
- [रूटिंग](../README.md): फ़ाइल-आधारित राउटर
- [कॉन्फ़िगर](../../reference/config.md): `useRouter` सहित प्रत्येक विकल्प
