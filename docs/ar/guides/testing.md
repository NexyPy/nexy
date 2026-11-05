# اختبار

`nx test` يُجري اختبارات الخادم باستخدام pytest، ويختبر العميل باستخدام vitest عندما تطلبها.

```bash
nx test                       # pytest
nx test -k create_user        # extra arguments go to pytest
nx test --client              # pytest, then vitest
nx test --no-server --client  # vitest only
```

## ما يدير

| الجزء | الأمر | الشرط |
|---|---|---|
| الخادم | `pytest` | يعمل على `tests/` عندما يكون موجودًا، وإلا على جذر المشروع؛ تم تخطيه مع تحذير عند عدم تثبيت pytest |
| العميل | `npx vitest run` | فقط مع `--client`، وفقط عند وجود `vitest.config.ts` أو ظهور `vitest` في `package.json` |

لا يوجد عداء مدمج من النهاية إلى النهاية. قم بقيادة الخادم باستخدام `TestClient` وأضف Playwright أو Cypress بنفسك لسلوك المتصفح.

## اختبر الخادم

يتحدث عميل الاختبار إلى تطبيق ASGI قيد التشغيل: لا يوجد خادم لبدء التشغيل، ولا يوجد منفذ للاختيار.

```python filename="الاختبارات/test_pages.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_home_renders():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
```

`nexy.app.app` هو التطبيق المجمع، الذي بني عند قراءته لأول مرة. يقرأ `nexyconfig.py` من دليل العمل، لذا قم بتشغيل pytest من جذر المشروع.

عندما يغير الاختبار التكوين أو المسارات، أنشئ تطبيقًا جديدًا بدلاً من إعادة استخدام مستوى الوحدة النمطية:

```python
from fastapi.testclient import TestClient
from nexy.modules.routers.app import AppServer


def test_api_hello():
    with TestClient(AppServer().run()) as client:
        response = client.get("/api/hello")
    assert response.json() == {"message": "Hello"}
```

`AppServer().run()` يعيد تجميع المسارات والبرامج الوسيطة والجلسات والترجمات، بحيث يبدأ كل استدعاء من الحالة الحالية لدليل المشروع.

## ما يجب التأكيد عليه

صفحة ترجع HTML. قم بتأكيد الحالة، ثم المحتوى الذي يهمك:

```python
def test_blog_page_renders_slug(client):
    response = client.get("/blog/post-1")
    assert "post-1" in response.text
```

يقوم معالج API بإرجاع JSON. فشل التحقق من الصحة هو `422`، والمسار المفقود هو `404` تمت الإجابة عليه بواسطة `notfound.nexy` عند وجود هذا الملف:

```python
def test_create_item_validates_body(client):
    assert client.post("/api/items", json={}).status_code == 422
```

بالنسبة لإجراء ما، اختبر الوظيفة مباشرة - فهي وظيفة عادية - واختبر نقطة نهاية HTTP من خلال قراءة المسار الذي تم إنشاؤه من الصفحة التي تعرضها:

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

مكالمة مع JSON تجيب بالنتيجة، و `422` بالحقول غير الصالحة.

> [!ملاحظة]
> مسارات العمل خاصة بالمشروع وتم إنشاؤها. لا تستخدم الكود الثابت أبدًا `/_nx_<hash>` في الاختبار.

## اختبار مكون `.nexy`

`nexy.testing.render` يقوم بتجميع مكون، مع المكونات التي يستوردها، وإرجاع HTML الخاص به. الدعائم هي وسائط الكلمات الرئيسية و `children=` تملأ الفتحة:

```python filename="الاختبارات/test_button.py"
from nexy.testing import render


def test_button_shows_its_label():
    assert "Save" in render("src/components/button.nexy", label="Save")
```

قم بتشغيل pytest من جذر المشروع: تذهب الملفات المترجمة إلى `__nexy__/`، كما هو الحال مع `nx dev`. يحتاج المكون الذي يقرأ الطلب (`usePathname`، `useSession`) إلى اختبار صفحة باستخدام `TestClient` بدلاً من ذلك.

## اختبر العميل

`nx test --client` يتوقع الإعداد الأكثر قوة الخاص بك. اختبار الحد الأدنى من المكونات:

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

`vitest` ومكتبة الاختبار هي تبعيات للمشروع: `nexy new` لا يقوم بتثبيت مكدس اختبار. أضف `vitest.config.ts` مع البيئة التي تحتاجها (jsdom أو Happy-dom للمكونات).

## التكامل المستمر

هناك أمران يكفيان لخط أنابيب المشروع:

```bash
nx build
nx test
```

`nx build` فشل بسبب خطأ في الترجمة؛ `nx test` يفشل في التأكيد الفاشل ويخرج من الصفر. `nx check` يضيف mypy و `tsc` إلى التشغيل.

يستخدم العمل على Nexy نفسه أوامر مختلفة: راجع [المساهمة](../../CONTRIBUTING.md).

## الخطوات التالية

- [CLI](../reference/cli.md): كل علم `nx test`
- [API](../routing/fbr/handlers/README.md): ما ترجعه نقطة النهاية
- [نشر](../deployment/README.md): قم بالإنشاء قبل الاختبار في CI
