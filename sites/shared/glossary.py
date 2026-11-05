"""The words of the docs a service leaves in English when they stand alone in a link.

Inside a sentence, `[views](…)` or `[Testing](…)` reaches the service as a lone word between
brackets, and the service sends it back untouched. Asked alone, it answers the wrong sense:
`hooks` becomes the hooks of a coat rack, `islands` the islands of a sea. This glossary gives the
word a reader of the docs expects, in every language of the site.

A term is written in lower case; `term` gives it the capital of the English word it replaces.
"""

from __future__ import annotations

# The order of the words of every term: the languages of the site, English aside.
ORDER = ("zh", "hi", "es", "fr", "ar", "bn", "pt", "ru", "ur", "id", "de")

TERMS: dict[str, tuple[str, ...]] = {
    "config": (
        "配置", "कॉन्फ़िग", "configuración", "configuration", "الإعداد", "কনফিগ",
        "configuração", "конфигурация", "کنفیگ", "konfigurasi", "Konfiguration",
    ),
    "frontend": (
        "前端", "फ्रंटएंड", "frontend", "frontend", "الواجهة الأمامية", "ফ্রন্টএন্ড",
        "frontend", "фронтенд", "فرنٹ اینڈ", "frontend", "Frontend",
    ),
    "views": (
        "视图", "व्यू", "vistas", "vues", "العروض", "ভিউ", "visualizações", "представления",
        "ویوز", "tampilan", "Ansichten",
    ),
    "layouts": (
        "布局", "लेआउट", "diseños", "mises en page", "التخطيطات", "লেআউট", "layouts", "макеты",
        "لے آؤٹس", "tata letak", "Layouts",
    ),
    ".nexy files": (
        ".nexy 文件", ".nexy फ़ाइलें", "archivos .nexy", "fichiers .nexy", "ملفات .nexy",
        ".nexy ফাইল", "arquivos .nexy", "файлы .nexy", ".nexy فائلیں", "berkas .nexy",
        ".nexy-Dateien",
    ),
    "modes": (
        "模式", "मोड", "modos", "modes", "الأوضاع", "মোড", "modos", "режимы", "موڈز", "mode",
        "Modi",
    ),
    "mode": (
        "模式", "मोड", "modo", "mode", "الوضع", "মোড", "modo", "режим", "موڈ", "mode", "Modus",
    ),
    "routing": (
        "路由", "रूटिंग", "enrutamiento", "routage", "التوجيه", "রাউটিং", "roteamento",
        "маршрутизация", "روٹنگ", "perutean", "Routing",
    ),
    "deploy": (
        "部署", "डिप्लॉय", "despliegue", "déploiement", "النشر", "ডিপ্লয়", "implantação",
        "развёртывание", "ڈپلائے", "penerapan", "Deployment",
    ),
    "rendering": (
        "渲染", "रेंडरिंग", "renderizado", "rendu", "العرض", "রেন্ডারিং", "renderização",
        "рендеринг", "رینڈرنگ", "perenderan", "Rendering",
    ),
    "actions": (
        "操作", "एक्शन", "acciones", "actions", "الإجراءات", "অ্যাকশন", "ações", "действия",
        "ایکشنز", "aksi", "Aktionen",
    ),
    "action": (
        "操作", "एक्शन", "acción", "action", "إجراء", "অ্যাকশন", "ação", "действие", "ایکشن",
        "aksi", "Aktion",
    ),
    "testing": (
        "测试", "टेस्टिंग", "pruebas", "tests", "الاختبار", "টেস্টিং", "testes", "тестирование",
        "ٹیسٹنگ", "pengujian", "Testen",
    ),
    "tutorial": (
        "教程", "ट्यूटोरियल", "tutorial", "tutoriel", "الدرس التعليمي", "টিউটোরিয়াল",
        "tutorial", "руководство", "ٹیوٹوریل", "tutorial", "Tutorial",
    ),
    "modular": (
        "模块化", "मॉड्यूलर", "modular", "modulaire", "المعياري", "মডিউলার", "modular",
        "модульный", "ماڈیولر", "modular", "modular",
    ),
    "hooks": (
        "钩子", "हुक", "hooks", "hooks", "الخطافات", "হুক", "hooks", "хуки", "ہکس", "hook",
        "Hooks",
    ),
    "guards": (
        "守卫", "गार्ड", "guardas", "gardes", "الحراس", "গার্ড", "guardas", "гарды", "گارڈز",
        "guard", "Guards",
    ),
    "handlers": (
        "处理函数", "हैंडलर", "manejadores", "gestionnaires", "المعالجات", "হ্যান্ডলার",
        "manipuladores", "обработчики", "ہینڈلرز", "handler", "Handler",
    ),
    "route handlers": (
        "路由处理函数", "रूट हैंडलर", "manejadores de rutas", "gestionnaires de routes",
        "معالجات المسارات", "রুট হ্যান্ডলার", "manipuladores de rota", "обработчики маршрутов",
        "روٹ ہینڈلرز", "handler rute", "Route-Handler",
    ),
    "websocket handlers": (
        "WebSocket 处理函数", "WebSocket हैंडलर", "manejadores de WebSocket",
        "gestionnaires WebSocket", "معالجات WebSocket", "WebSocket হ্যান্ডলার",
        "manipuladores de WebSocket", "обработчики WebSocket", "WebSocket ہینڈلرز",
        "handler WebSocket", "WebSocket-Handler",
    ),
    "islands": (
        "岛屿", "आइलैंड", "islas", "îlots", "الجزر", "আইল্যান্ড", "ilhas", "острова",
        "آئی لینڈز", "pulau", "Inseln",
    ),
    "island": (
        "岛屿", "आइलैंड", "isla", "îlot", "جزيرة", "আইল্যান্ড", "ilha", "остров", "آئی لینڈ",
        "pulau", "Insel",
    ),
    "pages": (
        "页面", "पृष्ठ", "páginas", "pages", "الصفحات", "পাতা", "páginas", "страницы", "صفحات",
        "halaman", "Seiten",
    ),
    "linking": (
        "链接", "लिंकिंग", "enlaces", "liens", "الروابط", "লিংকিং", "links", "ссылки", "لنکنگ",
        "tautan", "Verlinkung",
    ),
    "components": (
        "组件", "कंपोनेंट", "componentes", "composants", "المكونات", "কম্পোনেন্ট",
        "componentes", "компоненты", "کمپوننٹس", "komponen", "Komponenten",
    ),
    "changelog": (
        "更新日志", "बदलाव सूची", "registro de cambios", "journal des modifications",
        "سجل التغييرات", "পরিবর্তন তালিকা", "registro de alterações", "журнал изменений",
        "تبدیلیوں کا ریکارڈ", "catatan perubahan", "Änderungsprotokoll",
    ),
    "navigation": (
        "导航", "नेविगेशन", "navegación", "navigation", "التنقل", "নেভিগেশন", "navegação",
        "навигация", "نیویگیشن", "navigasi", "Navigation",
    ),
    "installation": (
        "安装", "इंस्टॉलेशन", "instalación", "installation", "التثبيت", "ইনস্টলেশন",
        "instalação", "установка", "انسٹالیشن", "instalasi", "Installation",
    ),
    "architecture": (
        "架构", "आर्किटेक्चर", "arquitectura", "architecture", "البنية", "আর্কিটেকচার",
        "arquitetura", "архитектура", "آرکیٹیکچر", "arsitektur", "Architektur",
    ),
    "issue": (
        "问题", "इश्यू", "incidencia", "ticket", "بلاغ", "ইস্যু", "issue", "обращение", "ایشو",
        "issue", "Issue",
    ),
    "middleware and security": (
        "中间件与安全", "मिडलवेयर और सुरक्षा", "middleware y seguridad",
        "middleware et sécurité", "البرمجيات الوسيطة والأمان", "মিডলওয়্যার ও নিরাপত্তা",
        "middleware e segurança", "промежуточное ПО и безопасность", "مڈل ویئر اور سیکیورٹی",
        "middleware dan keamanan", "Middleware und Sicherheit",
    ),
    "middleware files": (
        "中间件文件", "मिडलवेयर फ़ाइलें", "archivos de middleware", "fichiers middleware",
        "ملفات البرمجيات الوسيطة", "মিডলওয়্যার ফাইল", "arquivos de middleware",
        "файлы промежуточного ПО", "مڈل ویئر فائلیں", "berkas middleware", "Middleware-Dateien",
    ),
    "dev toolbar": (
        "开发工具栏", "डेव टूलबार", "barra de desarrollo", "barre de développement",
        "شريط أدوات التطوير", "ডেভ টুলবার", "barra de desenvolvimento", "панель разработчика",
        "ڈیو ٹول بار", "toolbar pengembangan", "Entwickler-Toolbar",
    ),
    "performance": (
        "性能", "परफ़ॉर्मेंस", "rendimiento", "performances", "الأداء", "পারফরম্যান্স",
        "desempenho", "производительность", "کارکردگی", "performa", "Performance",
    ),
    "dependencies": (
        "依赖", "डिपेंडेंसी", "dependencias", "dépendances", "التبعيات", "ডিপেনডেন্সি",
        "dependências", "зависимости", "ڈیپنڈنسیز", "dependensi", "Abhängigkeiten",
    ),
    "file conventions": (
        "文件约定", "फ़ाइल नियम", "convenciones de archivos", "conventions de fichiers",
        "اصطلاحات الملفات", "ফাইলের নিয়ম", "convenções de arquivos", "соглашения о файлах",
        "فائل کے اصول", "konvensi berkas", "Dateikonventionen",
    ),
    "error pages": (
        "错误页面", "त्रुटि पृष्ठ", "páginas de error", "pages d'erreur", "صفحات الأخطاء",
        "ত্রুটি পাতা", "páginas de erro", "страницы ошибок", "خرابی کے صفحات", "halaman galat",
        "Fehlerseiten",
    ),
    "directive": (
        "指令", "डायरेक्टिव", "directiva", "directive", "التعليمة", "ডিরেক্টিভ", "diretiva",
        "директива", "ڈائریکٹیو", "direktif", "Direktive",
    ),
    "exceptions": (
        "异常", "एक्सेप्शन", "excepciones", "exceptions", "الاستثناءات", "এক্সেপশন", "exceções",
        "исключения", "ایکسیپشنز", "eksepsi", "Ausnahmen",
    ),
    "a database": (
        "数据库", "डेटाबेस", "una base de datos", "une base de données", "قاعدة بيانات",
        "একটি ডেটাবেস", "um banco de dados", "базу данных", "ڈیٹا بیس", "basis data",
        "eine Datenbank",
    ),
    "inheritance": (
        "继承", "इनहेरिटेंस", "herencia", "héritage", "الوراثة", "ইনহেরিটেন্স", "herança",
        "наследование", "وراثت", "pewarisan", "Vererbung",
    ),
    "python api": (
        "Python API", "Python API", "API de Python", "API Python", "واجهة Python البرمجية",
        "Python API", "API Python", "Python API", "Python API", "API Python", "Python-API",
    ),
}  # fmt: skip


def term(english: str, lang: str) -> str | None:
    """The word of the glossary for an English link text, or None when it has none."""
    words = TERMS.get(english.lower())
    if words is None or lang not in ORDER:
        return None
    word = words[ORDER.index(lang)]
    return word[:1].upper() + word[1:] if english[:1].isupper() else word
