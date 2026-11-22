# كيف أقوم بتصحيح رمز الخادم في Nexy؟

قم بتصحيح كود الخادم `nx dev` باستخدام `breakpoint()` في الوحدة الطرفية، أو باستخدام VS Code و `debugpy`: يقوم خادم التطوير بتشغيل Python في عمليته الخاصة، لذلك يتوقف مصحح الأخطاء المرتبط به في صفحاتك ومعالجات API والإجراءات.

## كيف يقوم `nx dev` بتشغيل التعليمات البرمجية الخاصة بك

`nx dev` يبدأ اليوفيكورن في عمليته الخاصة، دون وجود عامل منفصل. عندما يتغير ملف Python أو صفحة `.nexy`، فإنه ينسى وحدات مشروعك ويستوردها مرة أخرى في نفس العملية. لذلك يظل مصحح الأخطاء المرتبط بـ `nx dev` مرفقًا عبر عملية إعادة التحميل، وتحتفظ نقطة التوقف المعينة في ملف بمكانها في الكود الجديد.

يتم تجميع ملف `.nexy` إلى وحدة Python ضمن `__nexy__/`، في نفس المسار، وهو ما يتم تشغيله:

<!-- router:fbr,custom -->
| أنت تكتب | يدير نيكي |
|---|---|
| `src/routes/about.nexy` | `__nexy__/src/routes/about.py`، الدالة `About()` |
| `src/components/Button.nexy` | `__nexy__/src/components/Button.py` |
| `src/routes/api/users.py` | الملف نفسه |
<!-- /router -->

<!-- router:modular -->
| أنت تكتب | يدير نيكي |
|---|---|
| `src/apps/users/user_view.nexy` | `__nexy__/src/apps/users/user_view.py` |
| `src/components/Button.nexy` | `__nexy__/src/components/Button.py` |
| `src/apps/users/user_controller.py` | الملف نفسه |
<!-- /router -->

تصبح المادة الأمامية للملف `.nexy` (Python بين السطرين `---`) نصًا لوظيفة تلك الوحدة. `__nexy__/` يُكتب مرة أخرى عند كل تغيير: لا تُعدله أبدًا.

## توقف في المحطة مع `breakpoint()`

ضع `breakpoint()` حيث تريد التوقف، في ملف `.py` أو في مقدمة ملف `.nexy`:

<!-- router:fbr,custom -->
```nexy filename="src/routes/about.nexy"
---
from nexy import useSearchParams

page = useSearchParams().get("page", "1")
breakpoint()
---
<p>Page {{ page }}</p>
```

افتح الصفحة. ينتظر الطلب وتعرض محطة `nx dev` pdb، في الوحدة النمطية المترجمة:

```text
> /path/to/app/__nexy__/src/routes/about.py(21)About()
-> breakpoint()
(Pdb)
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller


@Controller("/users")
class UserController:
    async def get(self):
        page = "1"
        breakpoint()
        return {"page": page}
```

فتح `/users`. ينتظر الطلب وتعرض محطة `nx dev` pdb على هذا الخط. في الجزء الأمامي من طريقة العرض، يعرض pdb الوحدة المترجمة ضمن `__nexy__/src/apps/`.
<!-- /router -->

اكتب `p page` لطباعة القيمة، `n` للسطر التالي، `c` للسماح بمواصلة الطلب. قم بإزالة السطر عند الانتهاء: يتوقف الطلب التالي عند هذا الحد مرة أخرى.

## تصحيح الأخطاء باستخدام رمز VS

تثبيت `debugpy` في بيئة المشروع:

```bash
uv add --dev debugpy
```

ثم قم بإضافة تكوين الإطلاق. `nexy.modules.cli` هي الوحدة خلف الأمر `nx`، لذا فهي تعمل بنفس الطريقة على Linux وmacOS وWindows:

```json filename=".vscode/launch.json"
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "nx dev",
      "type": "debugpy",
      "request": "launch",
      "module": "nexy.modules.cli",
      "args": ["dev"],
      "console": "integratedTerminal"
    }
  ]
}
```

اضغط على F5. قم بتعيين نقاط التوقف في ملفات `.py` الخاصة بك، وفي الوحدة النمطية المترجمة ضمن `__nexy__/` لملف `.nexy`: لا يمكن أن يتوقف VS Code في ملف `.nexy`، لأنه ليس Python حتى يتم تجميعه. تتبع أرقام الأسطر الخاصة بالوحدة المترجمة المادة الأمامية، لذلك قد تتحرك نقطة التوقف هناك بعد تحرير الصفحة؛ `breakpoint()` في المقدمة لا.

## نعلق من محطة أخرى

لبدء خادم التطوير بنفسك وإرفاق مصحح الأخطاء لاحقًا:

```bash
python -m debugpy --listen 127.0.0.1:5678 --wait-for-client -m nexy.modules.cli dev
```

`--wait-for-client` يحفظ البداية حتى يتم إرفاق مصحح الأخطاء؛ اتركه ليبدأ على الفور. في VS Code، قم بإرفاق تكوين `"request": "attach"` و `"connect": { "host": "127.0.0.1", "port": 5678 }`.

قد يحذر debugpy من أنه "يتم استخدام الوحدات النمطية المجمدة". ابدأ Python بـ `-Xfrozen_modules=off` (`python -Xfrozen_modules=off -m debugpy ...`) في حالة فقدان نقطة توقف في المكتبة القياسية؛ لا تتأثر نقاط التوقف في التعليمات البرمجية الخاصة بك.

## الخطوات التالية

- [استكشاف الأخطاء وإصلاحها](troubleshooting.md): أول المشاكل التي يتعرض لها الناس
- [الاختبار ](testing.md): قم بإعادة إنتاج الخطأ في الاختبار بمجرد العثور عليه
- [ملفات .nexy](../views/nexy/README.md): المادة الأمامية، props والقوالب
