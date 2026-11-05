# التثبيت

## المتطلبات

| المتطلب | لماذا |
|---|---|
| Python 3.12+ | `requires-python` في `pyproject.toml` |
| [uv](https://docs.astral.sh/uv/) | يقوم بإنشاء المشروع وتثبيت حزمه وتشغيل Nexy |
| Node.js 18+ | فقط لإطار عمل العميل (React، Vue، Svelte، Solid، Preact) |

المشروع بدون إطار عمل العميل لا يحتاج إلى Node.js على الإطلاق.

## قم بتثبيت uv أولاً

`uvx` ليست أداة منفصلة: فهي تأتي مع uv، لذا قم بتثبيت uv قبل أي شيء آخر.

```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

راجعه مع `uv --version` و `uvx --version`.

## إنشاء مشروع

```bash
uvx nexy new my-app
```

`uvx` يدير Nexy في بيئة مؤقتة ولا يترك شيئًا خلفه. هذا يكفي **لإنشاء** مشروع (`new`، `init`) ولا شيء أكثر من ذلك: البيئة المؤقتة تحتوي على Nexy ولا تحتوي على حزمة أخرى. `nexy new` ينشئ البيئة الافتراضية الخاصة بالمشروع، `.venv`، ويثبت حزمه هناك.

`nexy new my-app` يطرح أربعة أسئلة: جهاز التوجيه (المعتمد على الملف أو المعياري)، ونوع المشروع (الويب أو واجهة برمجة التطبيقات)، وإطار عمل العميل، وORM. يتم بعد ذلك تشغيل تثبيت Python وتبعيات العقدة بسطر واحد لكل خطوة ومدتها. انظر [CLI](../reference/cli.md).

تخطي المطالبات باستخدام القالب المسجل:

```bash
uvx nexy new my-app --template <name>
```

## العمل داخل البيئة الافتراضية للمشروع

كل أمر آخر (`nexy dev`، `nexy build`، `nexy migrate`...) يجب أن يعمل **داخل البيئة الافتراضية للمشروع**. هذا هو المكان الذي تعيش فيه حزمك الخاصة: ORM الخاص بك، ومكتباتك، وNexy الذي تم إنشاء المشروع به. وخارجها يفشل مشروع يحتاج إلى `sqlmodel` مع `ModuleNotFoundError: No module named 'sqlmodel'`.

قم بتنشيطه مرة واحدة لكل محطة، من مجلد المشروع:

| شل | الأمر |
|---|---|
| بوويرشيل، كمد (ويندوز) | `.venv\Scripts\activate` |
| ماك، لينكس | `source .venv/bin/activate` |

ثم يبدأ الموجه بـ `(.venv)`. من هناك:

```bash
cd my-app
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

فتح <http://localhost:3000>.

لتخطي التنشيط دع uv يفعل ذلك لأمر واحد: `uv run nexy dev`.

> [!NOTE]
> `nexy` و `nx` هما نفس الثنائي. النسخة المثبتة مع `uv tool install nexy` تعيش في بيئتها الخاصة، مثل `uvx`، لذا استخدمها لإنشاء المشاريع وتشغيل كل شيء آخر من بيئة المشروع.

## إضافة Nexy إلى مشروع موجود

قم بتشغيله من البيئة الافتراضية للمشروع، مع وجود Nexy ضمن حزمه (`uv add nexy`):

```bash
nexy init
```

## الخطوات التالية

- [بداية سريعة](quick-start.md)
- [البرنامج التعليمي](tutorial.md)
- [هيكل المشروع](project-structure.md)
- [استكشاف الأخطاء وإصلاحها](../guides/troubleshooting.md)
