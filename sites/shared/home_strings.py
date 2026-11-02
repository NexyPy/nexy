"""Translated copy for the documentation home: hero, groups and cards.

The English copy lives in `docs/README.md` and in the cards (from `docs/README.md` menu). The
pages stay in English; only these strings change with the language, plus the site chrome. Keys match
the Getting Started slugs so the cards can be translated without rewriting `home.py`.
"""

from __future__ import annotations

HERO: dict[str, dict[str, str]] = {
    "en": {
        "title": "Nexy Documentation",
        "text": "A Python framework for fullstack web applications: FastAPI and Starlette on the server, Vite on the client, and one origin for both. A route is a file under `src/routes/`.",
    },
    "zh": {
        "title": "Nexy 文档",
        "text": "Nexy 是一个全栈 Python 框架：服务端使用 FastAPI 与 Starlette，客户端使用 Vite，前后端同源。路由即 `src/routes/` 下的文件。",
    },
    "hi": {
        "title": "Nexy दस्तावेज़",
        "text": "Nexy एक पूर्ण स्टैक Python फ्रेमवर्क है: सर्वर पर FastAPI और Starlette, क्लाइंट पर Vite, और दोनों का एक ही मूल। मार्ग `src/routes/` के अंतर्गत एक फ़ाइल है।",
    },
    "es": {
        "title": "Documentación de Nexy",
        "text": "Nexy es un framework Python fullstack: FastAPI y Starlette en el servidor, Vite en el cliente y un único origen para ambos. Una ruta es un archivo en `src/routes/`.",
    },
    "fr": {
        "title": "Documentation Nexy",
        "text": "Nexy est un framework Python fullstack : FastAPI et Starlette côté serveur, Vite côté client, un seul et même origine. Une route est un fichier sous `src/routes/`.",
    },
    "ar": {
        "title": "وثائق Nexy",
        "text": "Nexy إطار عمل Python متكامل: FastAPI وStarlette على الخادم، وVite على العميل، وأصل واحد لكليهما. المسار ملف تحت `src/routes/`.",
    },
    "bn": {
        "title": "Nexy ডকুমেন্টেশন",
        "text": "Nexy একটি ফুলস্ট্যাক Python ফ্রেমওয়ার্ক: সার্ভারে FastAPI ও Starlette, ক্লায়েন্টে Vite, এবং উভয়ের জন্য একটি উত্স। রুট হলো `src/routes/` এর অধীনে একটি ফাইল।",
    },
    "pt": {
        "title": "Documentação do Nexy",
        "text": "Nexy é um framework Python fullstack: FastAPI e Starlette no servidor, Vite no cliente e uma única origem para ambos. Uma rota é um arquivo em `src/routes/`.",
    },
    "ru": {
        "title": "Документация Nexy",
        "text": "Nexy — полнофункциональный фреймворк на Python: FastAPI и Starlette на сервере, Vite на клиенте, общий origin для обоих. Маршрут — файл в `src/routes/`.",
    },
    "ur": {
        "title": "Nexy دستاویزات",
        "text": "Nexy ایک فل سٹیک Python فریم ورک ہے: سرور پر FastAPI اور Starlette، کلائنٹ پر Vite، اور دونوں کے لیے ایک ہی اصل۔ روٹ `src/routes/` میں ایک فائل ہوتی ہے۔",
    },
    "id": {
        "title": "Dokumentasi Nexy",
        "text": "Nexy adalah framework Python fullstack: FastAPI dan Starlette di server, Vite di klien, serta satu origin untuk keduanya. Rute adalah berkas di `src/routes/`.",
    },
    "de": {
        "title": "Nexy-Dokumentation",
        "text": "Nexy ist ein Python-Fullstack-Framework: FastAPI und Starlette auf dem Server, Vite auf dem Client und ein gemeinsamer Ursprung für beide. Eine Route ist eine Datei unter `src/routes/`.",
    },
}

GROUPS: dict[str, dict[str, str]] = {
    "en": {
        "first-steps": "First steps",
        "understand-the-model": "Understand the model",
        "coming-from-elsewhere": "Coming from elsewhere",
    },
    "zh": {
        "first-steps": "第一步",
        "understand-the-model": "理解模型",
        "coming-from-elsewhere": "从别处而来",
    },
    "hi": {
        "first-steps": "पहले कदम",
        "understand-the-model": "मॉडल समझें",
        "coming-from-elsewhere": "कहीं और से आना",
    },
    "es": {
        "first-steps": "Primeros pasos",
        "understand-the-model": "Entiende el modelo",
        "coming-from-elsewhere": "Viniendo de otro sitio",
    },
    "fr": {
        "first-steps": "Premiers pas",
        "understand-the-model": "Comprendre le modèle",
        "coming-from-elsewhere": "Venir d'ailleurs",
    },
    "ar": {
        "first-steps": "الخطوات الأولى",
        "understand-the-model": "افهم النموذج",
        "coming-from-elsewhere": "القادمون من مكان آخر",
    },
    "bn": {
        "first-steps": "প্রথম ধাপ",
        "understand-the-model": "মডেল বুঝুন",
        "coming-from-elsewhere": "অন্য জায়গা থেকে আসা",
    },
    "pt": {
        "first-steps": "Primeiros passos",
        "understand-the-model": "Compreender o modelo",
        "coming-from-elsewhere": "Vindo de outro lugar",
    },
    "ru": {
        "first-steps": "Первые шаги",
        "understand-the-model": "Понять модель",
        "coming-from-elsewhere": "Пришли из другого места",
    },
    "ur": {
        "first-steps": "پہلے قدم",
        "understand-the-model": "ماڈل سمجھیں",
        "coming-from-elsewhere": "کہیں اور سے آنا",
    },
    "id": {
        "first-steps": "Langkah pertama",
        "understand-the-model": "Pahami modelnya",
        "coming-from-elsewhere": "Datang dari tempat lain",
    },
    "de": {
        "first-steps": "Erste Schritte",
        "understand-the-model": "Das Modell verstehen",
        "coming-from-elsewhere": "Von anderswo",
    },
}

CARDS: dict[str, dict[str, dict[str, str]]] = {
    "en": {
        "getting-started/installation": {
            "title": "Installation",
            "text": "Install uv and the Nexy CLI, then create your first project",
        },
        "getting-started/quick-start": {
            "title": "Quick start",
            "text": "Create a project, run it with live reload, and build it for production",
        },
        "getting-started/tutorial": {
            "title": "Tutorial",
            "text": "Build a notes page with an endpoint, shared data and a production build",
        },
        "getting-started/core-concepts": {
            "title": "Core concepts",
            "text": "Get the mental model: route, page, view, component, handler, endpoint",
        },
        "getting-started/how-nexy-works": {
            "title": "How Nexy works",
            "text": "Follow one request from the URL to the file that answers it",
        },
        "architecture": {
            "title": "Architecture",
            "text": "Know which layer does what, and what Nexy leaves to your application",
        },
        "getting-started/project-structure": {
            "title": "Project structure",
            "text": "A tour of a new project and what goes where",
        },
        "routing": {
            "title": "Routing",
            "text": "Choose the router that fits: file-based, modular or custom",
        },
        "views": {
            "title": "Views",
            "text": "Pick how you write pages: .nexy, .md/.mdx or a frontend framework",
        },
        "getting-started/coming-from-other-frameworks": {
            "title": "Coming from other frameworks",
            "text": "A map from Next.js, Remix, Django, FastAPI or Astro to Nexy",
        },
    },
    "zh": {
        "getting-started/installation": {
            "title": "安装",
            "text": "安装 uv 和 Nexy CLI，然后创建你的第一个项目",
        },
        "getting-started/quick-start": {
            "title": "快速开始",
            "text": "创建项目，实时重载运行，并构建用于生产",
        },
        "getting-started/tutorial": {
            "title": "教程",
            "text": "构建带有端点、共享数据和生产构建的笔记页",
        },
        "getting-started/core-concepts": {
            "title": "核心概念",
            "text": "理解路由、页面、视图、组件、处理器、端点等概念",
        },
        "getting-started/how-nexy-works": {
            "title": "Nexy 工作原理",
            "text": "跟随一次请求从 URL 到响应文件的全过程",
        },
        "architecture": {"title": "架构", "text": "了解各层职责以及 Nexy 留给应用的部分"},
        "getting-started/project-structure": {
            "title": "项目结构",
            "text": "新项目导览及各文件作用",
        },
        "routing": {"title": "路由", "text": "选择合适的路由：文件式、模块式或自定义"},
        "views": {"title": "视图", "text": "选择页面编写方式：.nexy、.md/.mdx 或前端框架"},
        "getting-started/coming-from-other-frameworks": {
            "title": "从其他框架迁移",
            "text": "从 Next.js、Remix、Django、FastAPI 或 Astro 到 Nexy 的对照",
        },
    },
    "hi": {
        "getting-started/installation": {
            "title": "स्थापना",
            "text": "uv और Nexy CLI स्थापित करें, फिर अपना पहला प्रोजेक्ट बनाएं",
        },
        "getting-started/quick-start": {
            "title": "त्वरित शुरुआत",
            "text": "प्रोजेक्ट बनाएं, लाइव रीलोड के साथ चलाएं और प्रोडक्शन के लिए बिल्ड करें",
        },
        "getting-started/tutorial": {
            "title": "ट्यूटोरियल",
            "text": "एंडपॉइंट, साझा डेटा और प्रोडक्शन बिल्ड के साथ नोट्स पेज बनाएं",
        },
        "getting-started/core-concepts": {
            "title": "मुख्य अवधारणाएँ",
            "text": "मानसिक मॉडल समझें: रूट, पेज, व्यू, कंपोनेंट, हैंडलर, एंडपॉइंट",
        },
        "getting-started/how-nexy-works": {
            "title": "Nexy कैसे काम करता है",
            "text": "URL से लेकर उत्तर देने वाली फ़ाइल तक एक अनुरोध का अनुसरण करें",
        },
        "architecture": {
            "title": "आर्किटेक्चर",
            "text": "जानें कौन सी परत क्या करती है और Nexy क्या छोड़ता है",
        },
        "getting-started/project-structure": {
            "title": "प्रोजेक्ट संरचना",
            "text": "नए प्रोजेक्ट का दौरा और क्या कहाँ जाता है",
        },
        "routing": {"title": "रूटिंग", "text": "उपयुक्त राउटर चुनें: फ़ाइल-आधारित, मॉड्यूलर या कस्टम"},
        "views": {"title": "व्यू", "text": "पेज लिखने का तरीका चुनें: .nexy, .md/.mdx या फ्रंटएंड फ्रेमवर्क"},
        "getting-started/coming-from-other-frameworks": {
            "title": "अन्य फ्रेमवर्क से आना",
            "text": "Next.js, Remix, Django, FastAPI या Astro से Nexy तक का नक्शा",
        },
    },
    "es": {
        "getting-started/installation": {
            "title": "Instalación",
            "text": "Instala uv y el CLI de Nexy, y crea tu primer proyecto",
        },
        "getting-started/quick-start": {
            "title": "Inicio rápido",
            "text": "Crea un proyecto, ejecútalo con recarga en vivo y compílalo para producción",
        },
        "getting-started/tutorial": {
            "title": "Tutorial",
            "text": "Crea una página de notas con un endpoint, datos compartidos y compilación para producción",
        },
        "getting-started/core-concepts": {
            "title": "Conceptos clave",
            "text": "Entiende el modelo: ruta, página, vista, componente, manejador, endpoint",
        },
        "getting-started/how-nexy-works": {
            "title": "Cómo funciona Nexy",
            "text": "Sigue una petición desde la URL hasta el archivo que la responde",
        },
        "architecture": {
            "title": "Arquitectura",
            "text": "Conoce qué hace cada capa y qué deja Nexy a tu aplicación",
        },
        "getting-started/project-structure": {
            "title": "Estructura del proyecto",
            "text": "Recorrido de un proyecto nuevo y dónde va cada cosa",
        },
        "routing": {
            "title": "Enrutamiento",
            "text": "Elige el enrutador adecuado: basado en archivos, modular o personalizado",
        },
        "views": {
            "title": "Vistas",
            "text": "Elige cómo escribir páginas: .nexy, .md/.mdx o un framework cliente",
        },
        "getting-started/coming-from-other-frameworks": {
            "title": "Desde otros frameworks",
            "text": "Mapa de Next.js, Remix, Django, FastAPI o Astro a Nexy",
        },
    },
    "fr": {
        "getting-started/installation": {
            "title": "Installation",
            "text": "Installez uv et le CLI Nexy, puis créez votre premier projet",
        },
        "getting-started/quick-start": {
            "title": "Démarrage rapide",
            "text": "Créez un projet, lancez-le en rechargement à chaud et construisez-le pour la production",
        },
        "getting-started/tutorial": {
            "title": "Tutoriel",
            "text": "Créez une page de notes avec un point de terminaison, des données partagées et un build de production",
        },
        "getting-started/core-concepts": {
            "title": "Concepts clés",
            "text": "Le modèle mental : route, page, vue, composant, gestionnaire, endpoint",
        },
        "getting-started/how-nexy-works": {
            "title": "Comment fonctionne Nexy",
            "text": "Suivez une requête de l'URL au fichier qui y répond",
        },
        "architecture": {
            "title": "Architecture",
            "text": "Quelles couches font quoi et ce que Nexy laisse à votre application",
        },
        "getting-started/project-structure": {
            "title": "Structure du projet",
            "text": "Visite d'un nouveau projet et répartition des fichiers",
        },
        "routing": {
            "title": "Routage",
            "text": "Choisissez le routeur : basé sur les fichiers, modulaire ou personnalisé",
        },
        "views": {
            "title": "Vues",
            "text": "Choisissez comment écrire des pages : .nexy, .md/.mdx ou un framework frontend",
        },
        "getting-started/coming-from-other-frameworks": {
            "title": "Depuis d'autres frameworks",
            "text": "Passage de Next.js, Remix, Django, FastAPI ou Astro vers Nexy",
        },
    },
    "ar": {
        "getting-started/installation": {
            "title": "التثبيت",
            "text": "ثبّت uv وCLI الخاص بـ Nexy، ثم أنشئ مشروعك الأول",
        },
        "getting-started/quick-start": {
            "title": "بدء سريع",
            "text": "أنشئ مشروعًا، شغّله مع إعادة التحميل الحي، وابنه للإنتاج",
        },
        "getting-started/tutorial": {
            "title": "درس تعليمي",
            "text": "أنشئ صفحة ملاحظات بنقطة نهاية وبيانات مشتركة وبناء للإنتاج",
        },
        "getting-started/core-concepts": {
            "title": "المفاهيم الأساسية",
            "text": "النموذج الذهني: مسار، صفحة، عرض، مكوّن، معالج، نقطة نهاية",
        },
        "getting-started/how-nexy-works": {
            "title": "كيف يعمل Nexy",
            "text": "اتبع طلبًا من URL إلى الملف الذي يجيب عليه",
        },
        "architecture": {"title": "البنية", "text": "ما تفعله كل طبقة وما يتركه Nexy لتطبيقك"},
        "getting-started/project-structure": {
            "title": "هيكل المشروع",
            "text": "جولة في مشروع جديد وأين يذهب كل شيء",
        },
        "routing": {
            "title": "التوجيه",
            "text": "اختر الموجه المناسب: قائم على الملفات، أو وحدات، أو مخصص",
        },
        "views": {
            "title": "العروض",
            "text": "اختر كيفية كتابة الصفحات: .nexy أو .md/.mdx أو إطار عمل عميل",
        },
        "getting-started/coming-from-other-frameworks": {
            "title": "من أطر أخرى",
            "text": "خريطة من Next.js أو Remix أو Django أو FastAPI أو Astro إلى Nexy",
        },
    },
    "bn": {
        "getting-started/installation": {
            "title": "ইনস্টলেশন",
            "text": "uv এবং Nexy CLI ইনস্টল করুন, তারপর প্রথম প্রজেক্ট তৈরি করুন",
        },
        "getting-started/quick-start": {
            "title": "দ্রুত শুরু",
            "text": "প্রজেক্ট তৈরি করুন, লাইভ রিলোডে চালান এবং প্রোডাকশনের জন্য বিল্ড করুন",
        },
        "getting-started/tutorial": {
            "title": "টিউটোরিয়াল",
            "text": "এন্ডপয়েন্ট, শেয়ার করা ডাটা এবং প্রোডাকশন বিল্ডসহ নোট পেজ তৈরি করুন",
        },
        "getting-started/core-concepts": {
            "title": "মূল ধারণা",
            "text": "মেন্টাল মডেল: রুট, পেজ, ভিউ, কম্পোনেন্ট, হ্যান্ডলার, এন্ডপয়েন্ট",
        },
        "getting-started/how-nexy-works": {
            "title": "Nexy কীভাবে কাজ করে",
            "text": "URL থেকে উত্তর দেওয়া ফাইল পর্যন্ত একটি অনুরোধ অনুসরণ করুন",
        },
        "architecture": {
            "title": "আর্কিটেকচার",
            "text": "কোন স্তর কী করে এবং Nexy আপনার অ্যাপকে কী ছেড়ে দেয় জানুন",
        },
        "getting-started/project-structure": {
            "title": "প্রজেক্ট স্ট্রাকচার",
            "text": "নতুন প্রজেক্টের ভ্রমণ এবং কোথায় কী যায়",
        },
        "routing": {"title": "রাউটিং", "text": "উপযুক্ত রাউটার নির্বাচন করুন: ফাইল-ভিত্তিক, মডুলার বা কাস্টম"},
        "views": {"title": "ভিউ", "text": "পেজ লেখার পদ্ধতি বাছুন: .nexy, .md/.mdx বা ক্লায়েন্ট ফ্রেমওয়ার্ক"},
        "getting-started/coming-from-other-frameworks": {
            "title": "অন্যান্য ফ্রেমওয়ার্ক থেকে",
            "text": "Next.js, Remix, Django, FastAPI বা Astro থেকে Nexy পর্যন্ত ম্যাপ",
        },
    },
    "pt": {
        "getting-started/installation": {
            "title": "Instalação",
            "text": "Instale o uv e o CLI do Nexy, depois crie o seu primeiro projeto",
        },
        "getting-started/quick-start": {
            "title": "Início rápido",
            "text": "Crie um projeto, execute-o com recarregamento ao vivo e construa para produção",
        },
        "getting-started/tutorial": {
            "title": "Tutorial",
            "text": "Crie uma página de notas com endpoint, dados partilhados e build para produção",
        },
        "getting-started/core-concepts": {
            "title": "Conceitos fundamentais",
            "text": "Modelo mental: rota, página, vista, componente, handler, endpoint",
        },
        "getting-started/how-nexy-works": {
            "title": "Como funciona o Nexy",
            "text": "Siga um pedido do URL até ao ficheiro que o responde",
        },
        "architecture": {
            "title": "Arquitetura",
            "text": "O que cada camada faz e o que o Nexy deixa à sua aplicação",
        },
        "getting-started/project-structure": {
            "title": "Estrutura do projeto",
            "text": "Percurso de um projeto novo e onde fica cada coisa",
        },
        "routing": {
            "title": "Encaminhamento",
            "text": "Escolha o router: baseado em ficheiros, modular ou personalizado",
        },
        "views": {
            "title": "Vistas",
            "text": "Escolha como escrever páginas: .nexy, .md/.mdx ou framework cliente",
        },
        "getting-started/coming-from-other-frameworks": {
            "title": "De outros frameworks",
            "text": "Mapa de Next.js, Remix, Django, FastAPI ou Astro para Nexy",
        },
    },
    "ru": {
        "getting-started/installation": {
            "title": "Установка",
            "text": "Установите uv и CLI Nexy, затем создайте первый проект",
        },
        "getting-started/quick-start": {
            "title": "Быстрый старт",
            "text": "Создайте проект, запустите с hot reload и соберите для продакшена",
        },
        "getting-started/tutorial": {
            "title": "Учебник",
            "text": "Создайте страницу заметок с эндпоинтом, общими данными и продакшен-сборкой",
        },
        "getting-started/core-concepts": {
            "title": "Основные понятия",
            "text": "Модель: маршрут, страница, представление, компонент, обработчик, эндпоинт",
        },
        "getting-started/how-nexy-works": {
            "title": "Как работает Nexy",
            "text": "Проследите запрос от URL до файла, который на него отвечает",
        },
        "architecture": {
            "title": "Архитектура",
            "text": "Кто за что отвечает и что Nexy оставляет вашему приложению",
        },
        "getting-started/project-structure": {
            "title": "Структура проекта",
            "text": "Обзор нового проекта: где что находится",
        },
        "routing": {
            "title": "Маршрутизация",
            "text": "Выберите роутер: файловый, модульный или кастомный",
        },
        "views": {
            "title": "Представления",
            "text": "Как писать страницы: .nexy, .md/.mdx или клиентский фреймворк",
        },
        "getting-started/coming-from-other-frameworks": {
            "title": "Переход с других фреймворков",
            "text": "Карта перехода с Next.js, Remix, Django, FastAPI или Astro на Nexy",
        },
    },
    "ur": {
        "getting-started/installation": {
            "title": "تنصیب",
            "text": "uv اور Nexy CLI نصب کریں، پھر اپنا پہلا پروجیکٹ بنائیں",
        },
        "getting-started/quick-start": {
            "title": "فوری آغاز",
            "text": "پروجیکٹ بنائیں، لائیو ری لوڈ کے ساتھ چلائیں، اور پروڈکشن کے لیے بنائیں",
        },
        "getting-started/tutorial": {
            "title": "سبق",
            "text": "اینڈ پوائنٹ، مشترکہ ڈیٹا اور پروڈکشن بلڈ کے ساتھ نوٹس کا صفحہ بنائیں",
        },
        "getting-started/core-concepts": {
            "title": "بنیادی تصورات",
            "text": "ذہنی ماڈل: روٹ، صفحہ، ویو، اجزاء، ہینڈلر، اینڈ پوائنٹ",
        },
        "getting-started/how-nexy-works": {
            "title": "Nexy کیسے کام کرتا ہے",
            "text": "URL سے لے کر جواب دینے والی فائل تک ایک درخواست کا پیچھا کریں",
        },
        "architecture": {
            "title": "فن تعمیر",
            "text": "جانیں کون سی تہہ کیا کرتی ہے اور Nexy کیا آپ کی ایپ پر چھوڑتا ہے",
        },
        "getting-started/project-structure": {
            "title": "پروجیکٹ کا ڈھانچہ",
            "text": "نئے پروجیکٹ کا دورہ اور ہر چیز کہاں جاتی ہے",
        },
        "routing": {
            "title": "روٹنگ",
            "text": "مناسب روٹر منتخب کریں: فائل پر مبنی، ماڈیولر یا حسب ضرورت",
        },
        "views": {
            "title": "مناظر",
            "text": "صفحے لکھنے کا طریقہ منتخب کریں: .nexy، .md/.mdx یا کلائنٹ فریم ورک",
        },
        "getting-started/coming-from-other-frameworks": {
            "title": "دیگر فریم ورکس سے",
            "text": "Next.js، Remix، Django، FastAPI یا Astro سے Nexy تک نقشہ",
        },
    },
    "id": {
        "getting-started/installation": {
            "title": "Instalasi",
            "text": "Pasang uv dan CLI Nexy, lalu buat proyek pertama Anda",
        },
        "getting-started/quick-start": {
            "title": "Mulai cepat",
            "text": "Buat proyek, jalankan dengan muat ulang langsung, dan bangun untuk produksi",
        },
        "getting-started/tutorial": {
            "title": "Tutorial",
            "text": "Bangun halaman catatan dengan endpoint, data bersama, dan bangunan produksi",
        },
        "getting-started/core-concepts": {
            "title": "Konsep inti",
            "text": "Pahami model mental: rute, halaman, tampilan, komponen, penangan, endpoint",
        },
        "getting-started/how-nexy-works": {
            "title": "Cara kerja Nexy",
            "text": "Ikuti permintaan dari URL hingga berkas yang menjawabnya",
        },
        "architecture": {
            "title": "Arsitektur",
            "text": "Ketahui peran setiap lapisan dan apa yang Nexy serahkan ke aplikasi Anda",
        },
        "getting-started/project-structure": {
            "title": "Struktur proyek",
            "text": "Tur proyek baru dan letak setiap berkas",
        },
        "routing": {
            "title": "Perutean",
            "text": "Pilih router yang sesuai: berbasis berkas, modular, atau kustom",
        },
        "views": {
            "title": "Tampilan",
            "text": "Pilih cara menulis halaman: .nexy, .md/.mdx, atau framework klien",
        },
        "getting-started/coming-from-other-frameworks": {
            "title": "Dari framework lain",
            "text": "Peta dari Next.js, Remix, Django, FastAPI, atau Astro ke Nexy",
        },
    },
    "de": {
        "getting-started/installation": {
            "title": "Installation",
            "text": "uv und den Nexy-CLI installieren, dann erstes Projekt erstellen",
        },
        "getting-started/quick-start": {
            "title": "Schnellstart",
            "text": "Projekt erstellen, mit Live-Reload laufen lassen und für Produktion bauen",
        },
        "getting-started/tutorial": {
            "title": "Tutorial",
            "text": "Notizenseite mit Endpoint, gemeinsamen Daten und Produktionsbuild erstellen",
        },
        "getting-started/core-concepts": {
            "title": "Kernkonzepte",
            "text": "Das Modell: Route, Seite, View, Komponente, Handler, Endpoint",
        },
        "getting-started/how-nexy-works": {
            "title": "Wie Nexy funktioniert",
            "text": "Einer Anfrage von der URL bis zur antwortenden Datei folgen",
        },
        "architecture": {
            "title": "Architektur",
            "text": "Welche Schicht was tut und was Nexy deiner App überlässt",
        },
        "getting-started/project-structure": {
            "title": "Projektstruktur",
            "text": "Rundgang durch ein neues Projekt und wo alles liegt",
        },
        "routing": {
            "title": "Routing",
            "text": "Router wählen: dateibasiert, modular oder benutzerdefiniert",
        },
        "views": {
            "title": "Views",
            "text": "Wählen, wie Seiten geschrieben werden: .nexy, .md/.mdx oder Frontend-Framework",
        },
        "getting-started/coming-from-other-frameworks": {
            "title": "Von anderen Frameworks",
            "text": "Von Next.js, Remix, Django, FastAPI oder Astro zu Nexy",
        },
    },
}
