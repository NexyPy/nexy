# निर्भरता इंजेक्शन

नेक्सी नियंत्रकों और सेवाओं के लिए कंस्ट्रक्टर निर्भरता का समाधान करता है। एक वर्ग इसके साथ जुड़ता है
`@Injectable()`.

## एक सेवा इंजेक्ट करें

```python filename="src/apps/users/user_service.py"
from nexy.decorators import Injectable


@Injectable()
class UserService:
    def get_all(self) -> list[dict]:
        return [{"id": 1, "name": "Ada"}]
```

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller
from .user_service import UserService


@Controller(prefix="/users")
class UserController:
    def __init__(self, svc: UserService) -> None:
        self.svc = svc

    def get(self) -> list[dict]:
        return self.svc.get_all()
```

नियंत्रक को एक मॉड्यूल में पंजीकृत करें। सेवा को `providers` में सूचीबद्ध करने से अतिरिक्त रूप से इसका समाधान हो जाता है
स्टार्टअप पर उत्सुकता से:

```python filename="src/apps/users/users_module.py"
from nexy.decorators import Module
from .user_controller import UserController
from .user_service import UserService


@Module()
class UsersModule:
    controllers = [UserController]
    providers = [UserService]
```

## रिज़ॉल्यूशन कैसे काम करता है

- प्रत्येक `__init__` पैरामीटर को उसके **प्रकार के एनोटेशन** से हल किया जाता है। एनोटेशन एक होना चाहिए
  `@Injectable()` वर्ग, या पैरामीटर का एक डिफ़ॉल्ट मान होना चाहिए; अन्यथा संकल्प बढ़ता है
  `ValueError`.
- स्टार्टअप पर नियंत्रकों को `Container.resolve()` से त्वरित किया जाता है।
- एक निर्भरता चक्र वर्ग का नामकरण `RecursionError` करता है।
- सेवाएं अन्य सेवाओं को किसी भी गहराई तक शामिल कर सकती हैं।

## क्षेत्र

```python
from nexy.decorators import Injectable, Scope


@Injectable(scope=Scope.REQUEST)
class CurrentUser: ...
```

| दायरा | जीवनकाल |
|---|---|
| `Scope.SINGLETON` (डिफ़ॉल्ट) | पूरी प्रक्रिया के लिए एक उदाहरण |
| `Scope.REQUEST` | प्रति अनुरोध संदर्भ एक उदाहरण |
| `Scope.TRANSIENT` | प्रत्येक रिज़ॉल्यूशन पर एक नया उदाहरण |

## कंटेनर

```python
from nexy.decorators import Container

service = Container.resolve(UserService)
```

`@Injectable()` वर्ग का निर्माण स्वयं करने से `TypeError` बढ़ता है: कंटेनर का अपना जीवनचक्र होता है।
`Container.resolve(...)` का उपयोग करें या किसी अन्य कंस्ट्रक्टर के माध्यम से क्लास प्राप्त करें।

`Container.clear_request_scope()` वर्तमान अनुरोध के उदाहरणों को हटा देता है।

## रूट पैरामीटर

फास्टएपीआई `Depends` कंस्ट्रक्टर इंजेक्शन के बगल में हैंडलर पैरामीटर के लिए सामान्य रूप से काम करता है:

```python
from fastapi import Depends


def get(self, limit: int = Depends(pagination)) -> list[dict]: ...
```

## सीमाएँ

कंटेनर प्रक्रिया-व्यापी है. प्रदाताओं को प्रति मॉड्यूल अलग-अलग नहीं किया जाता है, `exports` केवल यह तय करता है कि कौन सा
प्रदाता एक आयात मॉड्यूल उत्सुकता से हल करता है, और प्रदाता को स्वैप करने के लिए कोई सार्वजनिक एपीआई नहीं है
परीक्षण. पूरी तुलना के लिए [नेक्सी और नेस्टजेएस](vs-nestjs.md) देखें।

## अगले चरण

- [गार्ड और मेटाडेटा](guards-and-metadata.md)
- [परीक्षण](../../guides/testing.md)