# التثبيت

## المتطلبات

| المتطلبات | لماذا |
|---|---|
| بايثون 3.12+ | `requires-python` في `pyproject.toml` |
| [uv](https://docs.astral.sh/uv/) | يقوم بإنشاء المشروع وتثبيت حزمه وتشغيل Nexy |
| Node.js 18+ | فقط لإطار عمل العميل (React، Vue، Svelte، Solid، Preact) |

المشروع الذي لا يحتوي على إطار عمل العميل لا يحتاج إلى Node.js على الإطلاق.

## قم بتثبيت الأشعة فوق البنفسجية أولاً

`uvx` ليست أداة منفصلة: فهي تأتي مع الأشعة فوق البنفسجية، لذا قم بتثبيت الأشعة فوق البنفسجية قبل أي شيء آخر.

```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

وراجعه مع `uv --version` و`uvx --version`.

## إنشاء مشروع

```bash
uvx nexy new my-app
```

`uvx` يدير Nexy في بيئة مؤقتة ولا يترك شيئًا خلفه. وهذا يكفي **لإنشاء** أ
المشروع (`new`، `init`) وليس أكثر: البيئة المؤقتة تحمل Nexy وليس غيرها
package. `nexy new` يقوم بإنشاء البيئة الافتراضية الخاصة بالمشروع، `.venv`، وتثبيت حزمه
هناك.

`nexy new my-app` يطرح أربعة أسئلة: جهاز التوجيه (المعتمد على الملف أو المعياري)، ونوع المشروع (الويب أو واجهة برمجة التطبيقات)،
إطار عمل العميل ORM يتم بعد ذلك تشغيل تثبيت تبعيات Python وNode بسطر واحد لكل
الخطوة ومدتها. انظر [CLI](../reference/cli.md).

تخطي المطالبات باستخدام القالب المسجل:

```bash
uvx nexy new my-app --template <name>
```

## العمل داخل البيئة الافتراضية للمشروع

كل أمر آخر (`nexy dev`، `nexy build`، `nexy migrate`...) يجب أن يعمل ** داخل المشروع
البيئة الافتراضية**. هذا هو المكان الذي تعيش فيه حزمك الخاصة: ORM، ومكتباتك، وNexy
تم بناء المشروع مع. وخارجها يفشل مشروع يحتاج إلى `sqlmodel` مع
`ModuleNotFoundError: No module named 'sqlmodel'`.

قم بتنشيطه مرة واحدة لكل محطة، من مجلد المشروع:

| شل | الأمر |
|---|---|
| PowerShell، cmd (Windows) | `.venv\Scripts\activate` |
| ماك، لينكس | `source .venv/bin/activate` |

ثم يبدأ الموجه بـ `(.venv)`. من هناك:

```bash
cd my-app
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

فتح <http://localhost:3000>.

لتخطي التنشيط، دع uv يفعل ذلك بأمر واحد: `uv run nexy dev`.

> [!ملاحظة]
>  `nexy` و `nx` هما نفس الثنائي. تم تثبيت نسخة باستخدام أداة تثبيت الأشعة فوق البنفسجية
> nexy` lives in its own environment, like `uvx`، لذا استخدمه لإنشاء المشاريع وتشغيل كل شيء
> أخرى من بيئة المشروع.

## إضافة Nexy إلى مشروع موجود

قم بتشغيله من البيئة الافتراضية للمشروع، مع وجود Nexy ضمن حزمه (`uv add nexy`):

```bash
nexy init
```

## الخطوات التالية

- [بداية سريعة](quick-start.md)
- [البرنامج التعليمي](tutorial.md)
- [هيكل المشروع](project-structure.md)
-  [استكشاف الأخطاء وإصلاحها](../guides/troubleshooting.md)