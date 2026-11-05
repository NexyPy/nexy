# ٹیسٹنگ

`nx test` سرور ٹیسٹ کو pytest کے ساتھ چلاتا ہے، اور جب آپ ان سے پوچھتے ہیں تو کلائنٹ vitest کے ساتھ ٹیسٹ کرتا ہے۔

```bash
nx test                       # pytest
nx test -k create_user        # extra arguments go to pytest
nx test --client              # pytest, then vitest
nx test --no-server --client  # vitest only
```

## کیا چلتا ہے

| حصہ | حکم | حالت |
|---|---|---|
| سرور | `pytest` | جب یہ موجود ہو تو `tests/` پر چلتا ہے، بصورت دیگر پروجیکٹ روٹ پر؛ pytest انسٹال نہ ہونے پر انتباہ کے ساتھ چھوڑ دیا گیا۔ |
| کلائنٹ | `npx vitest run` | صرف `--client` کے ساتھ، اور صرف اس وقت جب `vitest.config.ts` موجود ہو یا `vitest` `package.json` میں ظاہر ہو۔ |

کوئی بلٹ ان اینڈ ٹو اینڈ رنر نہیں ہے۔ سرور کو `TestClient` کے ساتھ چلائیں اور براؤزر کے رویے کے لیے خود پلے رائٹ یا سائپرس کو شامل کریں۔

## سرور کی جانچ کریں۔

ٹیسٹ کلائنٹ ASGI ایپ سے ان پروسیس میں بات کرتا ہے: شروع کرنے کے لیے کوئی سرور نہیں، چننے کے لیے کوئی پورٹ نہیں۔

```python filename="tests/test_pages.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_home_renders():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
```

`nexy.app.app` جمع کردہ ایپلیکیشن ہے، جسے پہلی بار پڑھا گیا ہے۔ یہ ورکنگ ڈائرکٹری سے `nexyconfig.py` پڑھتا ہے، لہذا پروجیکٹ روٹ سے pytest چلائیں۔

جب کوئی ٹیسٹ کنفیگریشن یا روٹس تبدیل کرتا ہے تو ماڈیول لیول والے کو دوبارہ استعمال کرنے کے بجائے ایک تازہ ایپلیکیشن بنائیں:

```python
from fastapi.testclient import TestClient
from nexy.modules.routers.app import AppServer


def test_api_hello():
    with TestClient(AppServer().run()) as client:
        response = client.get("/api/hello")
    assert response.json() == {"message": "Hello"}
```

`AppServer().run()` روٹس، مڈل ویئر، سیشنز اور ترجمے کو دوبارہ جوڑتا ہے، لہذا ہر کال پروجیکٹ ڈائرکٹری کی موجودہ حالت سے شروع ہوتی ہے۔

## کیا دعوی کرنا ہے

ایک صفحہ HTML لوٹاتا ہے۔ اسٹیٹس پر زور دیں، پھر وہ مواد جس کی آپ کو پرواہ ہے:

```python
def test_blog_page_renders_slug(client):
    response = client.get("/blog/post-1")
    assert "post-1" in response.text
```

ایک API ہینڈلر JSON واپس کرتا ہے۔ توثیق کی ناکامی ایک `422` ہے، اور گمشدہ راستہ ایک `404` ہے جس کا جواب `notfound.nexy` نے دیا ہے جب وہ فائل موجود ہے:

```python
def test_create_item_validates_body(client):
    assert client.post("/api/items", json={}).status_code == 422
```

کسی عمل کے لیے، فنکشن کو براہ راست جانچیں - یہ ایک عام فنکشن ہے - اور HTTP کے اختتامی نقطہ کو اس صفحہ سے اس کے تیار کردہ راستے کو پڑھ کر جانچیں جو اسے بے نقاب کرتا ہے:

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

JSON کے ساتھ ایک کال نتیجہ کے ساتھ جواب دیتی ہے، اور `422` غلط فیلڈز کے ساتھ۔

> [!NOTE]
> کارروائی کے راستے منصوبے کے لیے مخصوص ہیں اور پیدا کیے گئے ہیں۔ ٹیسٹ میں کبھی ہارڈ کوڈ `/_nx_<hash>` نہ کریں۔

## ایک `.nexy` جزو کی جانچ کریں۔

`nexy.testing.render` ایک جز کو مرتب کرتا ہے، ان اجزاء کے ساتھ جو یہ درآمد کرتا ہے، اور اس کا HTML واپس کرتا ہے۔ پرپس کلیدی الفاظ کے دلائل ہیں اور `children=` سلاٹ کو بھرتے ہیں:

```python filename="tests/test_button.py"
from nexy.testing import render


def test_button_shows_its_label():
    assert "Save" in render("src/components/button.nexy", label="Save")
```

پروجیکٹ روٹ سے pytest چلائیں: مرتب شدہ فائلیں `__nexy__/` پر جاتی ہیں، جیسا کہ `nx dev`۔ ایک جزو جو درخواست کو پڑھتا ہے (`usePathname`, `useSession`) اس کے بجائے `TestClient` کے ساتھ صفحہ کی جانچ کی ضرورت ہے۔

## کلائنٹ کی جانچ کریں۔

`nx test --client` آپ کے اپنے بہترین سیٹ اپ کی توقع رکھتا ہے۔ ایک کم سے کم جزو ٹیسٹ:

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

`vitest` اور ٹیسٹنگ لائبریری پروجیکٹ انحصار ہیں: `nexy new` ٹیسٹ اسٹیک انسٹال نہیں کرتا ہے۔ اپنی ضرورت کے ماحول کے ساتھ `vitest.config.ts` شامل کریں (اجزاء کے لیے jsdom یا happy-dom)۔

## مسلسل انضمام

پروجیکٹ پائپ لائن کے لیے دو کمانڈز کافی ہیں:

```bash
nx build
nx test
```

`nx build` تالیف کی غلطی پر ناکام ہو جاتا ہے۔ `nx test` ناکام ہونے والے دعوے پر ناکام ہو جاتا ہے اور غیر صفر سے نکل جاتا ہے۔ `nx check` mypy اور `tsc` کو رن میں شامل کرتا ہے۔

Nexy پر کام کرنا خود مختلف کمانڈز کا استعمال کرتا ہے: دیکھیں [CONTRIBUTING](https://github.com/NexyPy/nexy/blob/main/CONTRIBUTING.md)۔

## اگلے اقدامات

- [CLI](../reference/cli.md): `nx test` کا ہر جھنڈا
- [API](../routing/fbr/handlers/README.md): آخر نقطہ کیا واپس آتا ہے۔
- [تعینات](../deployment/README.md): CI میں ٹیسٹ کرنے سے پہلے تعمیر کریں۔
