# मॉड्यूलर रूटिंग

मॉड्यूलर रूटिंग `src/routes/`: नियंत्रकों के अंतर्गत फ़ाइलों के बजाय डेकोरेटर वाली कक्षाओं का उपयोग करती है
अनुरोधों को संभालें, मॉड्यूल उन्हें समूहित करें, और प्रदाताओं को इंजेक्ट किया जाए। परिणामी माउंट करें `APIRouter`
`useRouter` के साथ `nexyconfig.py` में।

**शुरू करने से पहले:** एक नेक्सी प्रोजेक्ट और एक वर्किंग पेज। मॉड्यूलर राउटर इसकी जगह लेता है
फ़ाइल-आधारित, इसलिए यदि आपने अभी तक राउटर नहीं चुना है तो पहले [रूटिंग](../README.md) पढ़ें।

| पेज | इसमें क्या शामिल है |
|---|---|
| यह पृष्ठ | एक मॉड्यूल माउंट करें, एक नियंत्रक लिखें, समूह नियंत्रक |
| [निर्भरता इंजेक्शन](dependency-injection.md) | `@Injectable`, स्कोप, कंटेनर |
| [गार्ड और मेटाडेटा](guards-and-metadata.md) | `@UseGuard`, `@Middleware`, `@UseRoute`, `@UseResponse` |
| [नेक्सी और नेस्टजेएस](vs-nestjs.md) | क्या नेस्टजेएस से मेल खाता है और क्या नहीं |

## राउटर सेट करें

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

> [!नोट]
> फ़ाइल-आधारित रूटिंग काम करती रहती है। यदि `src/routes/` मौजूद है, तो इसे स्कैन भी किया जाता है
> जब `useRouter` सेट हो।

## एक नियंत्रक लिखें

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.core.types import JsonResponse


@Controller()
class AppController:
    async def get(self) -> JsonResponse:
        return {"message": "Welcome to Nexy Modular API"}
```

विधियाँ नाम के अनुसार, केस-असंवेदनशील रूप से मेल खाती हैं: `get`, `post`, `put`, `patch`, `delete`, `options`,
`head`, `trace`।

एक नियंत्रक प्रति HTTP विधि एक हैंडलर घोषित करता है; स्टार्टअप पर एक डुप्लिकेट बढ़ता है। के साथ एक उपसर्ग जोड़ें
`@Controller(prefix="/users")` - प्रत्येक हैंडलर `prefix/` पर लगा हुआ है। `async def SOCKET(...)` ए पर
नियंत्रक उसी पथ पर एक WebSocket पंजीकृत करता है।

## एक मॉड्यूल में समूह नियंत्रक

```python filename="src/apps/app_module.py"
from nexy.decorators import Module
from .app_controller import AppController


@Module()
class AppModule:
    controllers = [AppController]
```

`@Module(prefix="/api")` एक `APIRouter` लौटाता है। `controllers` आवश्यक है; `providers`, `imports`
और `exports` वैकल्पिक हैं। आयातित मॉड्यूल उप-राउटर और उनके निर्यातित प्रदाताओं के रूप में माउंट किए जाते हैं
स्टार्टअप पर हल किया जाता है।

## एक नियंत्रक से दृश्य

एक नियंत्रक एक पृष्ठ वापस कर सकता है। `useViews` एक `.nexy` दृश्य प्रस्तुत करता है; इसे लपेटने के लिए एक को दूसरे के अंदर घोंसला बनाएं
एक लेआउट में:

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