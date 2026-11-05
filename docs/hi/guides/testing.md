# परीक्षण

`nx test` सर्वर परीक्षण को pytest के साथ चलाता है, और जब आप उनके लिए पूछते हैं तो क्लाइंट विटेस्ट के साथ परीक्षण करता है।

```bash
nx test                       # pytest
nx test -k create_user        # extra arguments go to pytest
nx test --client              # pytest, then vitest
nx test --no-server --client  # vitest only
```

## क्या चलता है

| भाग | कमान | शर्त |
|---|---|---|
| सर्वर | `pytest` | मौजूद होने पर `tests/` पर चलता है, अन्यथा प्रोजेक्ट रूट पर; pytest स्थापित नहीं होने पर चेतावनी के साथ छोड़ दिया गया |
| क्लाइंट | `npx vitest run` | केवल `--client` के साथ, और केवल जब `vitest.config.ts` मौजूद है या `vitest` `package.json` में दिखाई देता है |

इसमें कोई बिल्ट-इन एंड-टू-एंड रनर नहीं है। `TestClient` के साथ सर्वर को चलाएं और ब्राउज़र व्यवहार के लिए प्लेराइट या साइप्रस को स्वयं जोड़ें।

## सर्वर का परीक्षण करें

परीक्षण क्लाइंट प्रक्रिया के दौरान एएसजीआई ऐप से बात करता है: शुरू करने के लिए कोई सर्वर नहीं, चुनने के लिए कोई पोर्ट नहीं।

```python filename="परीक्षण/test_pages.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_home_renders():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
```

`nexy.app.app` असेंबल किया गया एप्लिकेशन है, जिसे पहली बार पढ़ते ही बनाया जाता है। यह कार्यशील निर्देशिका से `nexyconfig.py` पढ़ता है, इसलिए प्रोजेक्ट रूट से pytest चलाएँ।

जब कोई परीक्षण कॉन्फ़िगरेशन या रूट बदलता है, तो मॉड्यूल-स्तर का पुन: उपयोग करने के बजाय एक नया एप्लिकेशन बनाएं:

```python
from fastapi.testclient import TestClient
from nexy.modules.routers.app import AppServer


def test_api_hello():
    with TestClient(AppServer().run()) as client:
        response = client.get("/api/hello")
    assert response.json() == {"message": "Hello"}
```

`AppServer().run()` मार्गों, मिडलवेयर, सत्रों और अनुवादों को फिर से जोड़ता है, इसलिए प्रत्येक कॉल प्रोजेक्ट निर्देशिका की वर्तमान स्थिति से शुरू होती है।

## क्या दावा करें

एक पेज HTML लौटाता है. स्थिति पर जोर दें, फिर वह सामग्री जिसकी आप परवाह करते हैं:

```python
def test_blog_page_renders_slug(client):
    response = client.get("/blog/post-1")
    assert "post-1" in response.text
```

एक एपीआई हैंडलर JSON लौटाता है। एक सत्यापन विफलता एक `422` है, और एक लापता मार्ग एक `404` है जिसका उत्तर `notfound.nexy` द्वारा दिया जाता है जब वह फ़ाइल मौजूद होती है:

```python
def test_create_item_validates_body(client):
    assert client.post("/api/items", json={}).status_code == 422
```

किसी कार्रवाई के लिए, फ़ंक्शन का सीधे परीक्षण करें - यह एक सामान्य फ़ंक्शन है - और इसे प्रदर्शित करने वाले पृष्ठ से इसके जेनरेट किए गए पथ को पढ़कर HTTP समापन बिंदु का परीक्षण करें:

```python
from src.actions.user import create_user


async def test_create_user_returns_name():
    assert await create_user("Ada") == {"name": "Ada"}
```

```python
def test_form_posts_to_action(client):
    html = client.get("/").text
    action = html.split('action="')[1].split('"')[0]
    response = client.post(action, data={"name": "Ada"}, follow_redirects=False)
    assert response.status_code == 303
```

JSON वाली कॉल परिणाम के साथ उत्तर देती है, और `422` अमान्य फ़ील्ड के साथ।

> [!NOTE]
> क्रिया पथ परियोजना के लिए विशिष्ट होते हैं और उत्पन्न होते हैं। परीक्षण में कभी भी हार्डकोड `/_nx_<hash>` न करें।

## `.nexy` घटक का परीक्षण करें

`nexy.testing.render` एक घटक को आयातित घटकों के साथ संकलित करता है, और उसका HTML लौटाता है। प्रॉप्स कीवर्ड तर्क हैं और `children=` स्लॉट भरता है:

```python filename="परीक्षण/test_button.py"
from nexy.testing import render


def test_button_shows_its_label():
    assert "Save" in render("src/components/button.nexy", label="Save")
```

प्रोजेक्ट रूट से pytest चलाएँ: संकलित फ़ाइलें `__nexy__/` पर जाती हैं, जैसा कि `nx dev` में होता है। एक घटक जो अनुरोध को पढ़ता है (`usePathname`, `useSession`) को इसके बजाय `TestClient` के साथ एक पृष्ठ परीक्षण की आवश्यकता होती है।

## ग्राहक का परीक्षण करें

`nx test --client` आपके स्वयं के विटेस्ट सेटअप की अपेक्षा करता है। एक न्यूनतम घटक परीक्षण:

```tsx filename="src/components/counter.test.tsx"
import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import Counter from "./counter";

describe("Counter", () => {
  it("starts at zero", () => {
    const { getByText } = render(<Counter start={0} />);
    expect(getByText("0")).toBeTruthy();
  });
});
```

`vitest` और परीक्षण लाइब्रेरी परियोजना निर्भरताएं हैं: `nexy new` परीक्षण स्टैक स्थापित नहीं करता है। `vitest.config.ts` को उस वातावरण के साथ जोड़ें जिसकी आपको आवश्यकता है (घटकों के लिए jsdom या हैप्पी-डोम)।

## सतत एकीकरण

किसी प्रोजेक्ट पाइपलाइन के लिए दो कमांड पर्याप्त हैं:

```bash
nx build
nx test
```

`nx build` संकलन त्रुटि पर विफल रहता है; `nx test` एक असफल दावे पर विफल रहता है और गैर-शून्य से बाहर निकल जाता है। `nx check` रन में mypy और `tsc` जोड़ता है।

नेक्सी पर काम करने के लिए अलग-अलग कमांड का उपयोग किया जाता है: [योगदान](https://github.com/NexyPy/nexy/blob/main/CONTRIBUTING.md) देखें।

## अगले चरण

- [सीएलआई](../reference/cli.md): `nx test` का हर झंडा
- [एपीआई](../routing/fbr/handlers/README.md): समापन बिंदु क्या लौटाता है
- [तैनाती](../deployment/README.md): सीआई में परीक्षण करने से पहले निर्माण करें
