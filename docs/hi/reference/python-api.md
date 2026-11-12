# Python एपीआई

प्रत्येक नाम Nexy मॉड्यूल द्वारा आपके Python कोड पर निर्यात करता है। एक परीक्षण इस पृष्ठ को दोनों दिशाओं में कोड के विरुद्ध जांचता है: यहां सूचीबद्ध एक नाम मौजूद होना चाहिए, और कोड निर्यात करने वाला नाम यहां सूचीबद्ध होना चाहिए।

## `nexy`

`.nexy` टेम्प्लेट और अनुरोध हुक के लिए घटक।

| नाम | यह क्या है |
|---|---|
| `Audio`, `Video` | देशी `<audio>` और `<video>` खिलाड़ी, देखें [घटक](../views/nexy/components.md) |
| `Image` | एक `<img>` जो डिफ़ॉल्ट रूप से सुस्ती से लोड होता है |
| `Link` | एक क्लाइंट-साइड `<a>` वैकल्पिक प्रीफ़ेच के साथ |
| `Import` | एक क्लाइंट घटक को `.nexy` पृष्ठ में आयात करें |
| `Template` | Jinja2 और Markdown टेम्पलेट प्रस्तुत करें |
| `Vite` | Vite क्लाइंट टैग की प्रत्येक पृष्ठ को आवश्यकता होती है |
| `Form` | बिना किसी व्यवहार वाला प्लेसहोल्डर: एक [क्रिया](../guides/actions.md) के साथ एक सादे `<form>` का उपयोग करें |
| `usePathname` | वर्तमान अनुरोध का पथ |
| `useSearchParams` | क्वेरी स्ट्रिंग एक निर्देश के रूप में |
| `useParams` | डायनेमिक पथ पैरामीटर को एक निर्देश के रूप में, जैसे क्लाइंट पर `useParams()` |
| `useQuery` | `useParams` का मूल नाम, मौजूदा पृष्ठों के लिए रखा गया है (यह क्वेरी स्ट्रिंग को नहीं पढ़ता है) |
| `useRequest` | वर्तमान अनुरोध, अन्य हुक में क्या शामिल नहीं है |
| `useHeaders` | अनुरोध हेडर को लोअर-केस नामों के साथ एक निर्देश के रूप में |
| `useUrl` | पूरा यूआरएल: `.scheme`, `.hostname`, `.path`, `.query` |
| `useIsActive` | चाहे कोई लिंक नेविगेशन बार के लिए वर्तमान पृष्ठ या उसके माता-पिता में से किसी एक पर इंगित करता हो |
| `useRouter` | `path`, `base_url` और `url_for` वर्तमान अनुरोध के |
| `useSession` | सत्र बंद होने पर सत्र निर्देश खाली हो जाता है |
| `useCookies` | एक निर्देश के रूप में कुकीज़ का अनुरोध करें |
| `useToc` | वर्तमान पृष्ठ की सामग्री तालिका, HTML के रूप में |
| `useViews` | एक हैंडलर से `about.tsx` जैसी दृश्य फ़ाइल प्रस्तुत करें |
| `setMetadata`, `useMetadata` | किसी पृष्ठ के शीर्षक और हेड टैग को नाम दें और उन्हें लेआउट में लिखें |
| `redirect`, `permanentRedirect` | विज़िटर को अन्यत्र भेजें (307, 308) और अनुरोध रोकें |
| `notFound`, `forbidden`, `unauthorized` | कहीं से भी उत्तर 404, 403 या 401 दें |

हुक केवल अनुरोध के अंदर काम करते हैं: [हुक](../routing/fbr/navigation/hooks.md) देखें।

<!-- router:fbr,custom -->
```nexy filename="src/routes/index.nexy"
---
from nexy import useCookies, usePathname, useSearchParams

pathname = usePathname()
page = useSearchParams().get("page", "1")
theme = useCookies().get("theme", "light")
---
<p>{{ pathname }} - page {{ page }} - {{ theme }} theme</p>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/home_view.nexy"
---
from nexy import useCookies, usePathname, useSearchParams

pathname = usePathname()
page = useSearchParams().get("page", "1")
theme = useCookies().get("theme", "light")
---
<p>{{ pathname }} - page {{ page }} - {{ theme }} theme</p>
```
<!-- /router -->

## `nexy.http`

एक हैंडलर की HTTP शब्दावली। FastAPI के बजाय यहां से आयात करें, इसलिए आपके संचालक नेक्सी के अनुबंध पर निर्भर हैं।

| नाम | यह क्या है |
|---|---|
| `Request`, `Response` | आने वाला अनुरोध और बाहर जाने वाला प्रत्युत्तर |
| `HTTPException` | हैंडलर को एक स्थिति और एक `detail` के साथ रोकें |
| `status` | नामित स्थिति कोड, जैसे कि `status.HTTP_404_NOT_FOUND` |
| `Depends` | पहले एक फ़ंक्शन चलाएं और उसका परिणाम पास करें |
| `Header`, `Cookie`, `Query`, `Path`, `Body` | पैरामीटर कहां से आता है |
| `Form`, `File`, `UploadFile` | प्रपत्र फ़ील्ड और अपलोड (`python-multipart` केवल `multipart/form-data` के लिए) |
| `BackgroundTasks` | उत्तर भेजे जाने के बाद चलने वाला कार्य |
| `JSONResponse`, `HTMLResponse`, `PlainTextResponse` | एक निश्चित सामग्री प्रकार के साथ उत्तर |
| `RedirectResponse` | एक HTTP रीडायरेक्ट |
| `redirect`, `permanentRedirect` | किसी पेज, हैंडलर, कंट्रोलर या गार्ड से रीडायरेक्ट (307, 308) बढ़ाएं |
| `notFound`, `forbidden`, `unauthorized` | उन्हीं स्थानों से 404, 403 या 401 उठाएँ |
| `FileResponse`, `StreamingResponse` | किसी फ़ाइल या स्ट्रीम के साथ उत्तर दें |

<!-- router:fbr,custom -->
```python filename="src/routes/api/items/[id].py"
from nexy.http import Depends, Header, HTTPException, status


def api_key(x_api_key: str = Header(...)) -> str:
    if x_api_key != "secret":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad key")
    return x_api_key


async def GET(id: int, key: str = Depends(api_key)):
    return {"id": id}
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/items/items_by_id_api_controller.py"
from nexy.decorators import Controller
from nexy.http import Depends, Header, HTTPException, status


def api_key(x_api_key: str = Header(...)) -> str:
    if x_api_key != "secret":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad key")
    return x_api_key


@Controller("/api/items/{id}")
class ItemsByIdApiController:
    async def get(self, id: int, key: str = Depends(api_key)):
        return {"id": id}
```

नियंत्रक को रूट मॉड्यूल के `controllers` में सूचीबद्ध करें।
<!-- /router -->

## `nexy.decorators`

| नाम | यह क्या है |
|---|---|
| `Action` | किसी फ़ंक्शन को `POST` समापन बिंदु में बदलें, [क्रियाएँ](../guides/actions.md) देखें |
| `revalidate` | ब्राउज़र को बताएं कि किसी कार्रवाई के कारण कौन से पृष्ठ पुराने हो गए हैं |
| `Module`, `Controller` | [मॉड्यूलर राउटर](../routing/modular/README.md) में एक मॉड्यूल और एक नियंत्रक घोषित करें |
| `Injectable`, `Container`, `Scope` | [निर्भरता इंजेक्शन](../routing/modular/dependency-injection.md) और इसका जीवनकाल |
| `UseGuard`, `Middleware` | एक हैंडलर की रक्षा करें या लपेटें, देखें [रक्षक](../routing/modular/guards-and-metadata.md) |
| `UseRoute`, `useRoute`, `RouteMeta` | एक मार्ग का नाम बताएं और उसका वर्णन करें OpenAPI |
| `UseResponse`, `ResponseMeta` | किसी मार्ग के उत्तर का वर्णन करें |
| `HTTP_METHODS` | एक हैंडलर फ़ाइल HTTP विधियों को परिभाषित कर सकती है |
| `ACTIONS_STORE` | टूलींग और परीक्षण के लिए क्रियाओं की रजिस्ट्री |

```python filename="src/actions/posts.py"
from nexy.decorators import Action, revalidate


@Action
async def publish(post_id: int) -> bool:
    revalidate("/blog")
    return True
```

## `nexy.testing`

| नाम | यह क्या है |
|---|---|
| `render` | दिए गए प्रॉप्स के लिए `.nexy` घटक का HTML, बिना सर्वर के, देखें [परीक्षण](../guides/testing.md) |

```python filename="परीक्षण/test_button.py"
from nexy.testing import render


def test_the_button_shows_its_label():
    assert "Save" in render("src/components/button.nexy", label="Save")
```

## आगे कहाँ

- [कॉन्फ़िग](config.md): इन नामों के पीछे `use*` फ़ील्ड
- [अपवाद और त्रुटियाँ](exceptions.md): प्रत्येक विफलता क्या उत्तर देती है
- [दस्तावेज़ीकरण सूचकांक](../README.md): आप जो बना रहे हैं उसके लिए पृष्ठ
