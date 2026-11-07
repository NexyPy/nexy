# परियोजना संरचना

नेक्सी प्रोजेक्ट में प्रत्येक फ़ाइल का एक काम होता है, और वह कहाँ जाती है यह राउटर पर निर्भर करता है: `src/routes/` फ़ाइल-आधारित रूटिंग के लिए, `src/apps/` मॉड्यूलर राउटर के लिए।

## शीर्ष स्तर

<!-- router:fbr -->
```text
my-app/
├─ src/
│  ├─ routes/            every file is a route
│  │  ├─ index.nexy      → /
│  │  ├─ layout.nexy     shared layout, not a route
│  │  └─ api/hello.py    → /api/hello
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

कोई फ़ोल्डर चुनने के लिए, पूछें कि फ़ाइल क्या है:

- **ब्राउज़र कुछ खोल सकता है** - एक मार्ग: `src/routes/`।
- **कई मार्गों द्वारा उपयोग किया जाने वाला एक टुकड़ा** - एक घटक या एक मॉड्यूल: `src/components/`, `src/`।
- **एक फ़ाइल इस प्रकार प्रस्तुत की गई है** - `public/`।
- **उत्पन्न** - `__nexy__/`; इसे कभी संपादित न करें.

> [!WARNING]
> `src/routes/` को स्कैन किया जाता है: वहां रखा गया एक सहायक एक मार्ग बन जाता है। एक सहायक रखें जो `src/routes/` के बाहर का मार्ग नहीं है, या उसका नाम `_` से शुरू करें।
<!-- /router -->

<!-- router:modular -->
```text
my-app/
├─ src/
│  ├─ apps/              controllers, modules and their views
│  │  ├─ app_module.py   the root module, given to useRouter
│  │  ├─ app_controller.py
│  │  ├─ app_view.nexy   a view a controller returns
│  │  ├─ layout.nexy     the frame the controllers pass their view to
│  │  └─ users/          one folder per feature: controller, module, service, model
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration: useRouter = AppModule
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

कोई फ़ोल्डर चुनने के लिए, पूछें कि फ़ाइल क्या है:

- **एक यूआरएल** - `src/apps/` में एक नियंत्रक की एक विधि, जो उसके मॉड्यूल द्वारा पंजीकृत है।
- **एक पृष्ठ** - इसके नियंत्रक के बगल में एक `.nexy` दृश्य, `useViews` के साथ लौटा।
- **कई दृष्टिकोणों द्वारा उपयोग किया गया एक टुकड़ा** - `src/components/`।
- **एक फ़ाइल इस प्रकार प्रस्तुत की गई है** - `public/`।
- **उत्पन्न** - `__nexy__/`; इसे कभी संपादित न करें.
<!-- /router -->

<!-- router:custom -->
```text
my-app/
├─ src/
│  ├─ legacy/            the FastAPI router you include
│  │  └─ api.py          router = APIRouter(prefix="/api")
│  ├─ routes/            pages and route files, served next to it
│  │  └─ index.nexy      → /
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration: useRouter = router
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

कोई फ़ोल्डर चुनने के लिए, पूछें कि फ़ाइल क्या है:

- **शामिल ऐप का एक रूट** - जहां यह पहले से ही है, यहां `src/legacy/`।
- **एक नया पृष्ठ या मार्ग** - `src/routes/`, शामिल राउटर के बगल में।
- **एक फ़ाइल इस प्रकार प्रस्तुत की गई है** - `public/`।
- **उत्पन्न** - `__nexy__/`; इसे कभी संपादित न करें.
<!-- /router -->

<!-- router:fbr,custom -->
## `src/routes/`

नीचे आरक्षित नामों को छोड़कर, प्रत्येक फ़ाइल एक रूट बन जाती है। फ़ाइल पथ में एक्सटेंशन को छोड़कर URL है - [फ़ाइल-आधारित रूटिंग](../routing/fbr/README.md) देखें।

| फ़ाइल | भूमिका |
|---|---|
| `layout.nexy` | सिबलिंग और चाइल्ड पेजों को लपेटता है |
| `errors.nexy` | निर्देशिका के लिए 500 पृष्ठ |
| `notfound.nexy` | निर्देशिका के लिए 404 पेज |
| `dependencies.py` | निर्देशिका के लिए साझा की गई FastAPI निर्भरताएँ |
| `__init__.py` | Python पैकेज मार्कर |
| `loading.nexy` | आरक्षित - मार्गों से बाहर रखा गया है, लेकिन इसका अभी तक कोई रनटाइम प्रभाव नहीं है |

प्रत्येक पृष्ठ का नाम प्रति ढाँचे में भी मौजूद है। `react()` कॉन्फ़िगर होने पर, `layout.jsx` और `layout.tsx` बिल्कुल `layout.nexy` की तरह आरक्षित हैं। सूचियाँ `nexy/core/config.py` (`LAYOUT_FILE_NAMES`, `ERROR_FILE_NAMES`, `NOTFOUND_FILE_NAMES`, `LOADING_FILE_NAMES`) में बनाई गई हैं।

> [!NOTE]
> `notfound.nexy` और `errors.nexy` केवल तभी स्थापित होते हैं जब रूट रूट पर एक प्रति मौजूद होती है। उपनिर्देशिका में एक प्रतिलिपि उस उपसर्ग के लिए पृष्ठ को परिष्कृत करती है।
<!-- /router -->

<!-- router:modular -->
## `src/apps/`

एक नियंत्रक यूआरएल का उत्तर देता है, एक मॉड्यूल नियंत्रकों और प्रदाताओं को समूहित करता है, और रूट मॉड्यूल को `nexyconfig.py` में `useRouter` के साथ माउंट किया जाता है:

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews

LAYOUT = "src/apps/layout.nexy"


@Controller()
class AppController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/app_view.nexy")})
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .app_controller import AppController


@Module()
class AppModule:
    controllers = [AppController]
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
    useAliases = {"@": "src"}  # the views import @/components/...
```

`src/apps/` में कोई भी फ़ाइल अपने नाम से रूट नहीं है: केवल मॉड्यूल सूचीबद्ध नियंत्रक ही उत्तर देते हैं। [मॉड्यूलर रूटिंग](../routing/modular/README.md) देखें।
<!-- /router -->

## `public/`

यहां फ़ाइलें साइट रूट से दी जाती हैं: `/favicon.ico`, `/robots.txt`, छवियां, फ़ॉन्ट।

## `__nexy__/`

`nx build` द्वारा उत्पन्न (और `nx dev` द्वारा इसके लिए आवश्यक भागों के लिए)। इसमें शामिल है:

- संकलित `.nexy` फ़ाइलें, एक Python पैकेज के रूप में (`__nexy__/src/...`);
- उत्पन्न क्लाइंट प्रवेश बिंदु (`main.ts`, `vite.ts`, `*.auto.ts`);
- `client/` एक Vite निर्माण के बाद - संपत्ति, प्रकट, पूर्व-रेंडर HTML;
- `build-cache.json`.

संपूर्ण निर्देशिका को डिस्पोजेबल मानें: इसे हटाएं, इसका पुनर्निर्माण करें। इसे हाथ से संपादित करने से अगले निर्माण में परिवर्तन खो जाता है। इसे `.gitignore` में जोड़ें।

## अगले चरण

<!-- router:fbr -->
- [फ़ाइल-आधारित रूटिंग](../routing/fbr/README.md): कैसे एक पथ एक यूआरएल बन जाता है
<!-- /router -->
<!-- router:modular -->
- [मॉड्यूलर रूटिंग](../routing/modular/README.md): नियंत्रक, मॉड्यूल और प्रदाता
<!-- /router -->
<!-- router:custom -->
- [कस्टम रूटिंग](../routing/custom/README.md): एक मौजूदा FastAPI राउटर शामिल करें
<!-- /router -->
- [कॉन्फ़िग](../reference/config.md): प्रत्येक प्रोजेक्ट विकल्प
- [फ्रंटएंड](../guides/frontend.md): Vite, स्टाइलिंग और क्लाइंट बिल्ड
