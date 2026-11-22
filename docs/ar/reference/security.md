# الأمن

كيف تحافظ Nexy على حجم سطح الهجوم الخاص بها صغيرًا، والإصدارات التي تتطلبها، وكيفية التحقق من المشروع.

## طوابق الإصدار

يعتمد النكسي على FastAPI، Starlette، Jinja2، Vite و React. الأرضية هي أقل إصدار يسمح به Nexy؛ كل واحد يجيب على استشارة منشورة.

| الحزمة | الكلمة | لماذا |
|---|---|---|
| `starlette` | 1.3.1 | CVE-2026-48710 (BadHost، تم إصلاحه في 1.0.1): يقوم رأس `Host` بتغيير مسار التقارير Starlette إلى البرامج الوسيطة، مما يتجاوز التفويض المكتوب على `request.url.path`؛ مدرجة على أنها مستغلة من قبل CISA. CVE-2026-48817 وCVE-2026-48818 (إرسال الطلب، `StaticFiles` على نظام التشغيل Windows، تم إصلاحه في 1.1.0)، وCVE-2026-54282 (لم يتم التحقق من صحة مسار الطلب، 1.3.0) وCVE-2026-54283 (حدود `request.form()`، 1.3.1). |
| `python-dotenv` | 1.2.2 | يتم تحميل CVE-2026-28684، في قارئ الملف `.env` `nx migrate` |
| `fastapi` | 0.133.0 | الإصدار الأول الذي يقبل ثابت Starlette |
| `jinja2` | 3.1.6 | الهروب من وضع الحماية من خلال مرشح `attr` (CVE-2025-27516) |
| `vite` (المشاريع السقالة) | 6.4.5 | `server.fs.deny` تجاوزات (CVE-2026-53571 على مسارات Windows البديلة؛ GHSA-rq7h-c2jc-7f22، تم إصلاحه في 6.4.4؛ GHSA-8g5g-mxqh-grgj، تجاوز الاستعلام 6.4.4 تم إحضاره نفسه، تم إصلاحه في 6.4.5)، وتم إصلاح النصائح `launch-editor` في 6.4.4 |
| `svelte` (المشاريع السقالية) | 5.55.7 | ستة إرشادات XSS لعرض الخادم من خلال سمات الانتشار وأسماء العلامات الديناميكية و `bind:innerText` |
| `esbuild` (المشاريع السقالية) | 0.28.1 | قراءة الملف التعسفي من خلال خادم التطوير (GHSA-g7r4-m6w7-qqqr) |
| `react`، `react-dom` | 19.2.5 | تتعلق تحذيرات 2026 React بالحزم `react-server-dom-*` التي لا يستخدمها Nexy؛ الأرضية تحافظ على الخط مصححًا |

`python scripts/audit_dependencies.py` يتحقق من كل طابق مقابل OSV بعد القفل، في CI أيضًا: فشل الاستشارة الجديدة في الطابق في التدقيق.

تحقق من الإصدارات التي تم حلها:

```bash
uv pip list | grep -i -E "starlette|fastapi|jinja2"
npm ls vite
```

## القواعد التي يتبعها Nexy

- **لا تثق أبدًا في رأس المضيف للمسارات.** يقرأ Nexy `scope["path"]`، وليس `request.url.path`، في البرامج الوسيطة الخاصة به (البرامج الوسيطة للدليل). افعل نفس الشيء في ملكك.
- **الهروب مما يصل إلى HTML.** الدعائم التي تم تمريرها إلى مكونات العميل، والسمات `Link`، والسمات `Image`، و `Audio` و `Video`، ومثبتات جدول المحتويات وتفاصيل `HTTPException` كلها تم تجاوزها من HTML. لا يمكن الهروب من القالب `.nexy` من تلقاء نفسه: اكتب `{{ value | e }}` لأي قيمة تأتي من الزائر أو قاعدة البيانات، ولا يتم أبدًا `| safe` عند إدخال المستخدم.
- **نقاط نهاية المطور هي للاسترجاع فقط وضيقة.** تقبل نقطة نهاية عرض المطورين (`/__nexy__/render`) فقط الملفات الموجودة ضمن `src/routes/` ذات الامتداد `.tsx` أو `.jsx`، ولا يمكن الوصول إليها إلا من خلال خادم التطوير، الذي يرفض رؤوس `Host` الأجنبية.
- **تفاصيل الخطأ لا تتسرب.** تظهر صفحة الخطأ التي تفشل نفسها فقط رمز الحالة.
- **تحمل إجابات الإنتاج رؤوسًا آمنة.** `X-Content-Type-Options: nosniff` و `Referrer-Policy: strict-origin-when-cross-origin`، ما لم يحدد الكود الخاص بك خاصته. لم يتم إرسال رأس `Server`. أضف `Strict-Transport-Security` و `Content-Security-Policy` في الوكيل أو البرنامج الوسيط: يعتمدان على المجال الخاص بك.
- **يظهر العطل مرجعًا، وليس الخطأ.** راجع [صفحات الخطأ](../routing/fbr/errors/README.md#unhandled-exceptions).
- **لا يوجد `eval` ولا `shell=True` في كود Nexy Python.** تعمل البرامج الخارجية بقائمة الوسائط.

## تشغيل عمليات التدقيق

```bash
python scripts/audit_dependencies.py        # Python dependencies against the lock
npm audit                                    # in a scaffolded project
uv run bandit -r nexy -c .bandit             # static analysis of Nexy itself
```

يقوم مستودع Nexy الخاص بتشغيل الأول والثالث في عمليات التحقق الخاصة به. يتم التعامل مع الاستشارة الجديدة في الطابق العلوي عن طريق رفع الأرضية في `pyproject.toml` أو في السقالة `package.json`، ثم تجديد القفل.

## النشر بأمان

- اضبط `useTrustedHost` على نطاقاتك: فهو يرفض رؤوس `Host` غير المتوقعة قبل أي مسار.
- لا تكشف خادم التطوير Vite: `nx dev` يبقيه في حالة استرجاع خلف أصل Nexy.
- قم بتعيين `useDocs = False` إذا كان مخطط واجهة برمجة التطبيقات (API) لا يجب أن يكون عامًا.

انظر [البرامج الوسيطة والأمان](../guides/middleware-and-security.md).

## المصادر

- [CVE-2026-48710 (BadHost) في Starlette](https://www.penligent.ai/hackinglabs/cve-2026-48710/)
- [Vite الاستشارة GHSA-fx2h-pf6j-xcff](https://github.com/advisories/GHSA-fx2h-pf6j-xcff) و [GHSA-v2wj-q39q-566r](https://github.com/advisories/GHSA-v2wj-q39q-566r)
- [Jinja2 CVE-2025-27516](https://advisories.gitlab.com/pypi/jinja2/CVE-2025-27516/)
- [React حزم الخادم CVE-2026-44907](https://www.wiz.io/vulnerability-database/cve/cve-2026-44907)

## الخطوات التالية

- [الوسيطة والأمن](../guides/middleware-and-security.md)
- [نشر](../deployment/README.md)
- [التكوين](config.md)
