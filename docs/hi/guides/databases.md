# डेटाबेस

`nx new` SQLModel, SQLAlchemy या टोर्टोइज़-ओआरएम के साथ एक मॉडल परत तैयार कर सकता है। नेक्सी ओआरएम को लपेटता नहीं है: आप इसे सीधे हैंडलर और पेज से उपयोग करते हैं।

## मचान क्या जोड़ता है

| फ़ाइल | प्रयोजन |
|---|---|
| `src/configs/db.py` | इंजन (SQLModel, SQLAlchemy) या `TORTOISE_ORM` सेटिंग्स |
| `src/models/` | मॉडल कक्षाएं |
| `src/services/` | फ़ंक्शन जो मॉडलों से पूछताछ करते हैं |
| `.env` | `DATABASE_URL`, जब आप `nx new` के दौरान डेटाबेस यूआरएल देते हैं तो लिखा जाता है |

कनेक्शन स्ट्रिंग `DATABASE_URL` पर्यावरण चर से आती है। जब यह अनसेट होता है, तो मचान वाला इंजन वापस स्थानीय SQLite फ़ाइल, `dev.db` पर आ जाता है।

## किसी पृष्ठ में किसी सेवा का उपयोग करें

<!-- router:fbr,custom -->
```nexy filename="src/routes/users/index.nexy"
---
from src.services.user_service import UserService
users = UserService.get_all()
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

## एपीआई हैंडलर में एक सेवा का उपयोग करें

```python filename="src/routes/api/users.py"
from src.services.user_service import UserService


async def GET():
    return UserService.get_all()
```
<!-- /router -->

<!-- router:modular -->
एक नियंत्रक सेवा को कॉल करता है, और पंक्तियों को उसके दृश्य में भेजता है या उन्हें JSON के रूप में लौटाता है:

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews

from src.services.user_service import UserService


@Controller("/users")
class UserController:
    async def get(self):
        users = UserService.get_all()
        return useViews("src/apps/users/user_view.nexy", context={"users": users})


@Controller("/api/users")
class UserApiController:
    async def get(self):
        return UserService.get_all()
```

```nexy filename="src/apps/users/user_view.nexy"
---
users: prop[list] = []
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```
<!-- /router -->

## कछुआ-ओआरएम एसिंक्स है

एक पेज सर्वर के इवेंट लूप में चलता है और उस पर प्रतीक्षा नहीं कर सकता है, इसलिए `asyncio.run(...)` "रनिंग इवेंट लूप से कॉल नहीं किया जा सकता" के साथ वहां विफल हो जाता है। मचान `src/configs/db.py` देता है Tortoise एक धागे में अपना स्वयं का एक लूप, और दो सहायक जो इसे एक कोरआउटिन भेजते हैं:

| आप कहां हैं | बुलाओ | करता है |
|---|---|---|
| सिंक कोड, जैसे कोई पेज | `run(UserService.get_all())` | इसे चलाता है और परिणाम लौटाता है |
| एसिंक कोड, जैसे हैंडलर या कंट्रोलर | `await arun(UserService.get_all())` | वही, सर्वर को ब्लॉक किए बिना |

<!-- router:fbr,custom -->
```nexy filename="src/routes/users/index.nexy"
---
from src.configs.db import run
from src.services.user_service import UserService
users = run(UserService.get_all())
---
```
<!-- /router -->

<!-- router:modular -->
एक नियंत्रक एसिंक है: यह `arun` के माध्यम से सेवा की प्रतीक्षा करता है, और दृश्य केवल पंक्तियाँ दिखाता है:

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews

from src.configs.db import arun
from src.services.user_service import UserService


@Controller("/users")
class UserController:
    async def get(self):
        users = await arun(UserService.get_all())
        return useViews("src/apps/users/user_view.nexy", context={"users": users})
```
<!-- /router -->

Tortoise उनमें से किसी एक को पहली बार कॉल करने पर जुड़ जाता है। मॉडल को `async def` (`await UserModel.all()` एक सेवा के अंदर) से कॉल करें, मॉड्यूल स्तर पर नहीं: कोरआउटिन के बाहर एक कॉल Tortoise कनेक्ट होने से पहले चलती है।

`TORTOISE_ORM` (`src/configs/db.py` की `models` प्रविष्टि) में मॉडल रखने वाले प्रत्येक मॉड्यूल की सूची बनाएं। मचान उपयोगकर्ता मॉडल को सूचीबद्ध करता है और `aerich.models`; मॉड्यूल में एक मॉडल जो सूचीबद्ध नहीं है वह नहीं मिला है।

## पलायन

`nx migrate` आपके ORM के लिए टूल चुनता है: Alembic के लिए SQLModel और SQLAlchemy, Aerich के लिए Tortoise-ORM।

| आदेश | करता है |
|---|---|
| `nx migrate --init` | प्रोजेक्ट के लिए माइग्रेशन टूल प्रारंभ करें |
| `nx migrate -m "add users"` | अपने मॉडल परिवर्तनों से माइग्रेशन बनाएं |
| `nx migrate --upgrade` | लंबित माइग्रेशन लागू करें |

Aerich के साथ, पहला `nx migrate` चलता है `aerich init-db`, जो पहला माइग्रेशन और तालिकाएँ एक साथ बनाता है; अगले वाले `aerich migrate --name "..."` चलते हैं, और `--upgrade` `aerich upgrade` चलते हैं।

`nx migrate` एक स्पष्ट संदेश के साथ रुकता है जब `DATABASE_URL` गायब होता है या डेटाबेस तक नहीं पहुंचा जा सकता (Alembic केवल: Aerich अपनी त्रुटियों की रिपोर्ट करता है)।

### पहला प्रवास आपके लिए बना है

जब आप एक ORM चुनते हैं और एक डेटाबेस URL देते हैं, तो `nx new` माइग्रेशन टूल सेट करता है, पहला माइग्रेशन बनाता है और उसे लागू करता है, इसलिए उपयोगकर्ता पृष्ठ पहले `nexy dev` पर उत्तर देता है। माइग्रेशन टूल (`alembic` या `aerich`) ORM के साथ प्रोजेक्ट में स्थापित है।

यदि डेटाबेस उत्तर नहीं देता है (एक PostgreSQL सर्वर जो नहीं चल रहा है, एक लापता ड्राइवर), `nx new` कहता है क्यों, माइग्रेशन को छोड़ देता है और तैयार होने पर चलाने के लिए दो कमांड सूचीबद्ध करता है:

```bash
nexy migrate -m "create tables"
nexy migrate --upgrade
```

जब तक तालिकाएँ मौजूद नहीं होतीं, डेटाबेस को पढ़ने वाला पृष्ठ "ऐसी कोई तालिका नहीं" के साथ विफल हो जाता है।

### एक मॉडल जोड़ें

Alembic डेटाबेस की तुलना उन मॉडलों से करता है जो `alembic/env.py` आयात करते हैं। किसी नए मॉड्यूल में एक मॉडल तब तक नहीं देखा जाता जब तक कि उस मॉड्यूल को उपयोगकर्ता मॉडल के बगल में आयात नहीं किया जाता है:

```python filename="एलेम्बिक/env.py"
import src.models.user_model  # noqa: F401
import src.models.post_model  # noqa: F401
```

टोर्टोइज़-ओआरएम के लिए, मॉड्यूल को इसके बजाय `TORTOISE_ORM` में सूचीबद्ध करें (ऊपर देखें)।

## अगले चरण

- [परीक्षण](testing.md): एक अस्थायी डेटाबेस के विरुद्ध हैंडलर का परीक्षण करें
- [कॉन्फ़िग](../reference/config.md)
- [परिनियोजन](../deployment/README.md): उत्पादन में `DATABASE_URL` सेट करें
