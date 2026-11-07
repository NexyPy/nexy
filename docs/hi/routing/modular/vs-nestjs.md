# नेक्सी और NestJS

मॉड्यूलर राउटर NestJS से प्रेरित है: नियंत्रक, मॉड्यूल और कंस्ट्रक्टर इंजेक्शन। यह FastAPI के ऊपर एक पतली परत है, इसलिए यह सभी NestJS को पुन: उत्पन्न करने का प्रयास नहीं करता है। यह पृष्ठ दोनों पक्षों को सूचीबद्ध करता है।

## क्या मेल खाता है

| NestJS | नेक्सी |
|---|---|
| `@Controller('users')` | `@Controller("/users")` |
| `@Module({ controllers, providers, imports, exports })` | `@Module()` समान चार वर्ग विशेषताओं के साथ |
| `@Injectable()` | `@Injectable()` |
| कंस्ट्रक्टर इंजेक्शन | `__init__` टाइप एनोटेशन से पैरामीटर हल किए गए |
| सिंगलटन, अनुरोध और क्षणिक दायरे | `Scope.SINGLETON`, `Scope.REQUEST`, `Scope.TRANSIENT` |
| `@UseGuards(AuthGuard)` | `@UseGuard(guard)` (एक FastAPI निर्भरता) |
| `@ApiOperation`, `@ApiResponse` (स्वैगर) | `@UseRoute`, `@UseResponse` (OpenAPI, `/docs` में सेवा दी गई) |
| WebSocket प्रवेशद्वार | `async def SOCKET(...)` एक नियंत्रक पर |
| डीटीओ सत्यापन (`class-validator`) | Pydantic मॉडल, FastAPI के मूल निवासी |
| परिपत्र निर्भरता का पता लगाना | `RecursionError` वर्ग का नामकरण |

वही नियंत्रक और उसकी इंजेक्टेड सेवा, NestJS पहले:

```ts filename="उपयोगकर्ता.नियंत्रक.ts"
@Injectable()
export class UsersService {
  findAll() {
    return [{ id: 1, name: "Ada" }];
  }
}

@Controller("users")
export class UsersController {
  constructor(private readonly users: UsersService) {}

  @Get()
  findAll() {
    return this.users.findAll();
  }
}
```

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller, Injectable


@Injectable()
class UserService:
    def find_all(self) -> list[dict]:
        return [{"id": 1, "name": "Ada"}]


@Controller("/users")
class UserController:
    def __init__(self, users: UserService) -> None:
        self.users = users

    async def get(self) -> list[dict]:
        return self.users.find_all()
```

## क्या अलग है

- हैंडलर HTTP क्रिया (`get`, `post`...), प्रति नियंत्रक एक के नाम पर नामित विधियां हैं।
- गार्ड और मिडलवेयर डेकोरेटर FastAPI `Depends` हैं, न कि `canActivate` वाले वर्ग।
- पैरामीटर (`@Body`, `@Param`, `@Query`) FastAPI पैरामीटर हैं: प्रकार एनोटेशन, `Query`, `Path`, `Body`।
- पाइप्स Pydantic सत्यापन और FastAPI निर्भरताएँ हैं।

`@Query()`, एक डीटीओ और एक गार्ड वर्ग एक एनोटेशन, एक Pydantic मॉडल और एक फ़ंक्शन बन जाते हैं:

```python filename="src/apps/posts/post_controller.py"
from fastapi import Header, HTTPException, Query
from pydantic import BaseModel
from nexy.decorators import Controller, UseGuard


class NewPost(BaseModel):
    title: str


def require_token(x_token: str = Header(...)) -> None:
    if x_token != "secret":
        raise HTTPException(status_code=403, detail="Forbidden")


@Controller("/posts")
@UseGuard(require_token)
class PostController:
    async def get(self, limit: int = Query(10)) -> list[dict]:
        return []

    async def post(self, body: NewPost) -> dict:
        return {"title": body.title}
```

## क्या कमी है

| NestJS सुविधा | नेक्सी में स्थिति |
|---|---|
| कस्टम प्रदाता (`useValue`, `useFactory`, `useClass`, स्ट्रिंग टोकन) | उपलब्ध नहीं: केवल `@Injectable()` कक्षाएं |
| इंटरफ़ेस या अमूर्त वर्ग द्वारा इंजेक्ट करना | उपलब्ध नहीं है |
| मॉड्यूल एनकैप्सुलेशन | लागू नहीं किया गया: कंटेनर प्रक्रिया-व्यापी है, `exports` केवल उत्सुक रिज़ॉल्यूशन को नियंत्रित करता है |
| गतिशील और वैश्विक मॉड्यूल (`forRoot`, `@Global`) | उपलब्ध नहीं है |
| जीवनचक्र हुक (`onModuleInit`, `onApplicationShutdown`) | उपलब्ध नहीं है |
| इंटरसेप्टर | एएसजीआई मिडलवेयर (`useMiddlewares`) या निर्भरता का उपयोग करें |
| अपवाद फ़िल्टर | FastAPI अपवाद हैंडलर का उपयोग करें |
| प्रदाता के साथ परीक्षण मॉड्यूल ओवरराइड करता है | कोई सार्वजनिक एपीआई नहीं; FastAPI `dependency_overrides` और `TestClient` का उपयोग करें |
| कॉन्फिग मॉड्यूल, शेड्यूलिंग, क्यू, सीक्यूआरएस, माइक्रोसर्विसेज, कैशिंग | नेक्सी का हिस्सा नहीं; Python पारिस्थितिकी तंत्र का उपयोग करें |

`useFactory` प्रदाता के स्थान पर, `Depends` के पीछे एक सादा फ़ंक्शन, जिसे एक परीक्षण `dependency_overrides` के साथ ओवरराइड करता है:

```python filename="src/apps/reports/report_controller.py"
from fastapi import Depends
from nexy.decorators import Controller


def get_settings() -> dict:
    return {"currency": "EUR"}


@Controller("/reports")
class ReportController:
    async def get(self, settings: dict = Depends(get_settings)) -> dict:
        return {"currency": settings["currency"]}
```

## इसे कब चुनना है

जब आप बड़े एपीआई के लिए इंजेक्शन के साथ क्लास-आधारित संरचना चाहते हैं तो मॉड्यूलर राउटर चुनें। जब यूआरएल संरचना आयोजन सिद्धांत हो तो फ़ाइल-आधारित राउटर चुनें। दोनों `nx new` द्वारा बनाए गए हैं, एक ही FastAPI एप्लिकेशन पर चलते हैं, और एक साथ रह सकते हैं।

> [!NOTE]
> उपरोक्त लुप्त वस्तुएँ ईमानदार अंतर हैं। यदि आपको आज परीक्षणों में `useFactory` प्रदाताओं या अतिरंजित प्रदाताओं की आवश्यकता है, तो तर्क को सादे कार्यों और FastAPI `Depends` में रखें, जो स्वाभाविक रूप से लिखते और ओवरराइड करते हैं।

## अगले चरण

- [निर्भरता इंजेक्शन](dependency-injection.md)
- [गार्ड और मेटाडेटा](guards-and-metadata.md)
- [परीक्षण](../../guides/testing.md)
