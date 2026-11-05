"""The languages the documentation sites speak, and the words of the site in each.

The pages of `docs/` are written in English, and `scripts/translate_docs.py` writes each language
under `docs/<code>/`. A site publishes every language at `/docs/<code>/`: the pages and the menu
come from that tree, the words of the site around them (buttons, labels, search) from `UI` below,
written into the page on the server by `localize`. A page with no translation yet is served in
English under the language, with one line saying so. The languages are the twelve most spoken
ones; adding one is a block below, then a run of the script.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from html import escape
from pathlib import Path, PurePosixPath

from sites.shared.icons import ICONS


@dataclass(frozen=True)
class Language:
    """One language of the selector: its code, its own name, its English name and its direction."""

    code: str
    native: str
    english: str
    direction: str = "ltr"


LANGUAGES = (
    Language("en", "English", "English"),
    Language("zh", "简体中文", "Chinese"),
    Language("hi", "हिन्दी", "Hindi"),
    Language("es", "Español", "Spanish"),
    Language("fr", "Français", "French"),
    Language("ar", "العربية", "Arabic", "rtl"),
    Language("bn", "বাংলা", "Bengali"),
    Language("pt", "Português", "Portuguese"),
    Language("ru", "Русский", "Russian"),
    Language("ur", "اردو", "Urdu", "rtl"),
    Language("id", "Bahasa Indonesia", "Indonesian"),
    Language("de", "Deutsch", "German"),
)

DEFAULT = "en"
CODES = frozenset(language.code for language in LANGUAGES)


def is_english(relative: str) -> bool:
    """Whether a path under docs/ is an English page, not a copy in a language tree."""
    return not CODES.intersection(PurePosixPath(relative).parts)


def english_pages(docs: Path) -> list[str]:
    """The pages of `docs/` written in English, relative to it: a language tree holds copies."""
    found: list[str] = []
    for path in docs.rglob("*.md"):
        relative = path.relative_to(docs).as_posix()
        if is_english(relative):
            found.append(relative)
    return sorted(found)


def find(code: str) -> Language:
    """The language of a code, or English when the code is unknown."""
    return next((language for language in LANGUAGES if language.code == code), LANGUAGES[0])


def preferred(accept_language: str) -> str:
    """The first language of an Accept-Language header the site speaks, else English.

    The header lists them in the order the reader set: `fr-CA,fr;q=0.9,en;q=0.8` reads French.
    """
    for item in accept_language.split(","):
        code = item.split(";", 1)[0].strip()[:2].lower()
        if code in CODES:
            return code
    return DEFAULT


# The letters of the right-to-left scripts the site speaks: Arabic and Urdu.
_RTL_LETTER = re.compile("[\u0590-\u08ff\ufb1d-\ufdff\ufe70-\ufeff]")


def isolate(text: str, code: str) -> str:
    """The `dir` a short label needs on a page that reads right to left.

    A label with no right-to-left letter (`src/routes/`) reads left to right, or its slashes move
    to the other end; any other label follows the page.
    """
    if find(code).direction != "rtl" or _RTL_LETTER.search(text):
        return ""
    return ' dir="ltr"'


def is_known(code: str) -> bool:
    return any(language.code == code for language in LANGUAGES)


# The words of the site itself: one block per language, the same keys everywhere. The pages and the
# menu come from docs/<code>/; these are the buttons, labels and messages around them.
UI: dict[str, dict[str, str]] = {
    "en": {
        "skip": "Skip to content",
        "search": "Search",
        "search_aria": "Search the docs",
        "open_menu": "Open the menu",
        "collapse_menu": "Collapse the menu",
        "theme": "Switch between light and dark",
        "language": "Language",
        "on_this_page": "On this page",
        "back_to_top": "Back to top",
        "previous": "Previous",
        "next": "Next",
        "copy_page": "Copy page as Markdown",
        "edit_github": "Edit on GitHub",
        "copy": "Copy",
        "copied": "Copied",
        "no_match": "No page matches.",
        "type_to_search": "Type to search.",
        "enter_hint": "Enter opens the result, Esc closes.",
        "continue_prefix": "Continue: ",
        "all_docs": "All documentation",
        "source_github": "Source on GitHub",
        "llms": "llms.txt for agents",
        "docs": "Docs",
        "fallback_note": (
            "This page is still in English. The menu and the home page follow your language."
        ),
    },
    "zh": {
        "skip": "跳到正文",
        "search": "搜索",
        "search_aria": "搜索文档",
        "open_menu": "打开菜单",
        "collapse_menu": "收起菜单",
        "theme": "在浅色与深色之间切换",
        "language": "语言",
        "on_this_page": "本页内容",
        "back_to_top": "回到顶部",
        "previous": "上一页",
        "next": "下一页",
        "copy_page": "以 Markdown 复制本页",
        "edit_github": "在 GitHub 上编辑",
        "copy": "复制",
        "copied": "已复制",
        "no_match": "没有匹配的页面。",
        "type_to_search": "输入以搜索。",
        "enter_hint": "Enter 打开结果，Esc 关闭。",
        "continue_prefix": "继续：",
        "all_docs": "全部文档",
        "source_github": "在 GitHub 查看源码",
        "llms": "面向智能体的 llms.txt",
        "docs": "文档",
        "fallback_note": "本页仍为英文。菜单和首页已使用你选择的语言。",
    },
    "hi": {
        "skip": "सामग्री पर जाएँ",
        "search": "खोजें",
        "search_aria": "दस्तावेज़ खोजें",
        "open_menu": "मेन्यू खोलें",
        "collapse_menu": "मेन्यू समेटें",
        "theme": "हल्के और गहरे रंग के बीच बदलें",
        "language": "भाषा",
        "on_this_page": "इस पृष्ठ पर",
        "back_to_top": "ऊपर जाएँ",
        "previous": "पिछला",
        "next": "अगला",
        "copy_page": "पृष्ठ को Markdown के रूप में कॉपी करें",
        "edit_github": "GitHub पर संपादित करें",
        "copy": "कॉपी",
        "copied": "कॉपी हो गया",
        "no_match": "कोई पृष्ठ नहीं मिला।",
        "type_to_search": "खोजने के लिए लिखें।",
        "enter_hint": "Enter परिणाम खोलता है, Esc बंद करता है।",
        "continue_prefix": "जारी रखें: ",
        "all_docs": "सारा दस्तावेज़",
        "source_github": "GitHub पर स्रोत",
        "llms": "एजेंटों के लिए llms.txt",
        "docs": "दस्तावेज़",
        "fallback_note": "यह पृष्ठ अभी अंग्रेज़ी में है। मेन्यू और मुखपृष्ठ आपकी भाषा में हैं।",
    },
    "es": {
        "skip": "Saltar al contenido",
        "search": "Buscar",
        "search_aria": "Buscar en la documentación",
        "open_menu": "Abrir el menú",
        "collapse_menu": "Plegar el menú",
        "theme": "Cambiar entre claro y oscuro",
        "language": "Idioma",
        "on_this_page": "En esta página",
        "back_to_top": "Volver arriba",
        "previous": "Anterior",
        "next": "Siguiente",
        "copy_page": "Copiar la página como Markdown",
        "edit_github": "Editar en GitHub",
        "copy": "Copiar",
        "copied": "Copiado",
        "no_match": "Ninguna página coincide.",
        "type_to_search": "Escribe para buscar.",
        "enter_hint": "Enter abre el resultado, Esc lo cierra.",
        "continue_prefix": "Continuar: ",
        "all_docs": "Toda la documentación",
        "source_github": "Código en GitHub",
        "llms": "llms.txt para agentes",
        "docs": "Docs",
        "fallback_note": (
            "Esta página sigue en inglés. El menú y la página de inicio usan tu idioma."
        ),
    },
    "fr": {
        "skip": "Aller au contenu",
        "search": "Rechercher",
        "search_aria": "Rechercher dans la documentation",
        "open_menu": "Ouvrir le menu",
        "collapse_menu": "Replier le menu",
        "theme": "Passer du clair au sombre",
        "language": "Langue",
        "on_this_page": "Sur cette page",
        "back_to_top": "Retour en haut",
        "previous": "Précédent",
        "next": "Suivant",
        "copy_page": "Copier la page en Markdown",
        "edit_github": "Modifier sur GitHub",
        "copy": "Copier",
        "copied": "Copié",
        "no_match": "Aucune page ne correspond.",
        "type_to_search": "Tapez pour rechercher.",
        "enter_hint": "Entrée ouvre le résultat, Échap ferme.",
        "continue_prefix": "Continuer : ",
        "all_docs": "Toute la documentation",
        "source_github": "Source sur GitHub",
        "llms": "llms.txt pour les agents",
        "docs": "Docs",
        "fallback_note": (
            "Cette page est encore en anglais. Le menu et l'accueil suivent votre langue."
        ),
    },
    "ar": {
        "skip": "تخطَّ إلى المحتوى",
        "search": "بحث",
        "search_aria": "ابحث في الوثائق",
        "open_menu": "افتح القائمة",
        "collapse_menu": "اطوِ القائمة",
        "theme": "التبديل بين الفاتح والداكن",
        "language": "اللغة",
        "on_this_page": "في هذه الصفحة",
        "back_to_top": "إلى الأعلى",
        "previous": "السابق",
        "next": "التالي",
        "copy_page": "انسخ الصفحة بصيغة Markdown",
        "edit_github": "حرِّر على GitHub",
        "copy": "نسخ",
        "copied": "تم النسخ",
        "no_match": "لا توجد صفحة مطابقة.",
        "type_to_search": "اكتب للبحث.",
        "enter_hint": "Enter يفتح النتيجة، وEsc يغلق.",
        "continue_prefix": "متابعة: ",
        "all_docs": "كل الوثائق",
        "source_github": "المصدر على GitHub",
        "llms": "ملف llms.txt للوكلاء",
        "docs": "الوثائق",
        "fallback_note": "هذه الصفحة ما زالت بالإنجليزية. القائمة والصفحة الرئيسية تتبع لغتك.",
    },
    "bn": {
        "skip": "বিষয়বস্তুতে যান",
        "search": "খুঁজুন",
        "search_aria": "ডকুমেন্টেশন খুঁজুন",
        "open_menu": "মেনু খুলুন",
        "collapse_menu": "মেনু গুটিয়ে নিন",
        "theme": "হালকা ও গাঢ়ের মধ্যে বদলান",
        "language": "ভাষা",
        "on_this_page": "এই পাতায়",
        "back_to_top": "উপরে ফিরুন",
        "previous": "আগের",
        "next": "পরের",
        "copy_page": "পাতাটি Markdown হিসেবে কপি করুন",
        "edit_github": "GitHub-এ সম্পাদনা করুন",
        "copy": "কপি",
        "copied": "কপি হয়েছে",
        "no_match": "কোনো পাতা মেলেনি।",
        "type_to_search": "খুঁজতে লিখুন।",
        "enter_hint": "Enter ফলাফল খোলে, Esc বন্ধ করে।",
        "continue_prefix": "চালিয়ে যান: ",
        "all_docs": "সব ডকুমেন্টেশন",
        "source_github": "GitHub-এ সোর্স",
        "llms": "এজেন্টদের জন্য llms.txt",
        "docs": "ডকুমেন্টেশন",
        "fallback_note": "এই পাতাটি এখনো ইংরেজিতে। মেনু ও হোমপেজ আপনার ভাষায়।",
    },
    "pt": {
        "skip": "Ir para o conteúdo",
        "search": "Pesquisar",
        "search_aria": "Pesquisar na documentação",
        "open_menu": "Abrir o menu",
        "collapse_menu": "Recolher o menu",
        "theme": "Alternar entre claro e escuro",
        "language": "Idioma",
        "on_this_page": "Nesta página",
        "back_to_top": "Voltar ao topo",
        "previous": "Anterior",
        "next": "Seguinte",
        "copy_page": "Copiar a página como Markdown",
        "edit_github": "Editar no GitHub",
        "copy": "Copiar",
        "copied": "Copiado",
        "no_match": "Nenhuma página corresponde.",
        "type_to_search": "Escreva para pesquisar.",
        "enter_hint": "Enter abre o resultado, Esc fecha.",
        "continue_prefix": "Continuar: ",
        "all_docs": "Toda a documentação",
        "source_github": "Código no GitHub",
        "llms": "llms.txt para agentes",
        "docs": "Docs",
        "fallback_note": "Esta página ainda está em inglês. O menu e a página inicial usam o seu idioma.",
    },
    "ru": {
        "skip": "Перейти к содержимому",
        "search": "Поиск",
        "search_aria": "Поиск по документации",
        "open_menu": "Открыть меню",
        "collapse_menu": "Свернуть меню",
        "theme": "Переключить светлую и тёмную тему",
        "language": "Язык",
        "on_this_page": "На этой странице",
        "back_to_top": "Наверх",
        "previous": "Назад",
        "next": "Вперёд",
        "copy_page": "Скопировать страницу как Markdown",
        "edit_github": "Изменить на GitHub",
        "copy": "Копировать",
        "copied": "Скопировано",
        "no_match": "Подходящих страниц нет.",
        "type_to_search": "Введите запрос.",
        "enter_hint": "Enter открывает результат, Esc закрывает.",
        "continue_prefix": "Продолжить: ",
        "all_docs": "Вся документация",
        "source_github": "Исходный код на GitHub",
        "llms": "llms.txt для агентов",
        "docs": "Документация",
        "fallback_note": "Эта страница пока на английском. Меню и главная следуют вашему языку.",
    },
    "ur": {
        "skip": "مواد پر جائیں",
        "search": "تلاش",
        "search_aria": "دستاویزات میں تلاش کریں",
        "open_menu": "مینو کھولیں",
        "collapse_menu": "مینو سمیٹیں",
        "theme": "روشن اور گہرے کے درمیان بدلیں",
        "language": "زبان",
        "on_this_page": "اس صفحے پر",
        "back_to_top": "اوپر جائیں",
        "previous": "پچھلا",
        "next": "اگلا",
        "copy_page": "صفحہ Markdown کے طور پر کاپی کریں",
        "edit_github": "GitHub پر ترمیم کریں",
        "copy": "کاپی",
        "copied": "کاپی ہو گیا",
        "no_match": "کوئی صفحہ نہیں ملا۔",
        "type_to_search": "تلاش کے لیے لکھیں۔",
        "enter_hint": "Enter نتیجہ کھولتا ہے، Esc بند کرتا ہے۔",
        "continue_prefix": "جاری رکھیں: ",
        "all_docs": "تمام دستاویزات",
        "source_github": "GitHub پر سورس",
        "llms": "ایجنٹوں کے لیے llms.txt",
        "docs": "دستاویزات",
        "fallback_note": "یہ صفحہ ابھی انگریزی میں ہے۔ مینو اور ہوم صفحہ آپ کی زبان میں ہیں۔",
    },
    "id": {
        "skip": "Lompat ke isi",
        "search": "Cari",
        "search_aria": "Cari di dokumentasi",
        "open_menu": "Buka menu",
        "collapse_menu": "Lipat menu",
        "theme": "Beralih antara terang dan gelap",
        "language": "Bahasa",
        "on_this_page": "Di halaman ini",
        "back_to_top": "Kembali ke atas",
        "previous": "Sebelumnya",
        "next": "Berikutnya",
        "copy_page": "Salin halaman sebagai Markdown",
        "edit_github": "Sunting di GitHub",
        "copy": "Salin",
        "copied": "Tersalin",
        "no_match": "Tidak ada halaman yang cocok.",
        "type_to_search": "Ketik untuk mencari.",
        "enter_hint": "Enter membuka hasil, Esc menutup.",
        "continue_prefix": "Lanjutkan: ",
        "all_docs": "Semua dokumentasi",
        "source_github": "Sumber di GitHub",
        "llms": "llms.txt untuk agen",
        "docs": "Dokumentasi",
        "fallback_note": "Halaman ini masih dalam bahasa Inggris. Menu dan beranda mengikuti bahasa Anda.",
    },
    "de": {
        "skip": "Zum Inhalt springen",
        "search": "Suchen",
        "search_aria": "Die Dokumentation durchsuchen",
        "open_menu": "Menü öffnen",
        "collapse_menu": "Menü einklappen",
        "theme": "Zwischen hell und dunkel wechseln",
        "language": "Sprache",
        "on_this_page": "Auf dieser Seite",
        "back_to_top": "Nach oben",
        "previous": "Zurück",
        "next": "Weiter",
        "copy_page": "Seite als Markdown kopieren",
        "edit_github": "Auf GitHub bearbeiten",
        "copy": "Kopieren",
        "copied": "Kopiert",
        "no_match": "Keine Seite passt.",
        "type_to_search": "Tippen zum Suchen.",
        "enter_hint": "Enter öffnet das Ergebnis, Esc schließt.",
        "continue_prefix": "Weiter: ",
        "all_docs": "Gesamte Dokumentation",
        "source_github": "Quelltext auf GitHub",
        "llms": "llms.txt für Agenten",
        "docs": "Doku",
        "fallback_note": (
            "Diese Seite ist noch auf Englisch. Menü und Startseite folgen deiner Sprache."
        ),
    },
}


def text(code: str, key: str) -> str:
    """One word of the site in a language, or in English when the language lacks it."""
    return UI.get(code, UI[DEFAULT]).get(key) or UI[DEFAULT][key]


def select_html(current: str = DEFAULT, href: Callable[[str], str] | None = None) -> str:
    """The compact language picker of the top bar: a globe, the code, then every language.

    `href` gives the address of the same page in a language, so a choice is a plain link.
    """
    language = find(current)
    where = href or (lambda _code: "#")
    items = "".join(
        f'<li><a href="{escape(where(one.code))}" data-lang="{one.code}" lang="{one.code}"'
        f' hreflang="{one.code}"'
        f"{' aria-current="true"' if one.code == language.code else ''}>"
        f"<span>{escape(one.native)}</span><small>{escape(one.english)}</small></a></li>"
        for one in LANGUAGES
    )
    return (
        '<details class="lang-select" data-lang-select aria-label="Language" '
        'data-i18n-aria="language">'
        f"<summary>{ICONS['icon_globe']}<span data-lang-code>{language.code.upper()}</span></summary>"
        f"<ul>{items}</ul></details>"
    )


# A word of the site in a page: its text, its label or its placeholder names the key it shows.
_TEXT = re.compile(r'(<[^>]*\bdata-i18n="(\w+)"[^>]*>)([^<]*)(<)')
_ATTRIBUTE = re.compile(r'<[^>]*\bdata-i18n-(aria|placeholder)="(\w+)"[^>]*>')
_NAMES = {"aria": "aria-label", "placeholder": "placeholder"}


def _words(found: re.Match[str], code: str) -> str:
    """One element whose text now says the word in the language; an unknown key stays as it is."""
    if found[2] not in UI[DEFAULT]:
        return found[0]
    return f"{found[1]}{escape(text(code, found[2]), quote=False)}{found[4]}"


def _attribute(found: re.Match[str], code: str) -> str:
    """One tag whose label or placeholder now says the word in the language."""
    if found[2] not in UI[DEFAULT]:
        return found[0]
    name = _NAMES[found[1]]
    value = escape(text(code, found[2]), quote=True)
    return re.sub(rf'\b{name}="[^"]*"', f'{name}="{value}"', found[0], count=1)


def localize(html: str, code: str) -> str:
    """The page with every word of the site in the language: no script needed to read it."""
    if code == DEFAULT:
        return html
    html = _TEXT.sub(lambda found: _words(found, code), html)
    return _ATTRIBUTE.sub(lambda found: _attribute(found, code), html)


def payload() -> dict[str, object]:
    """The words the script writes itself (copy chips, search messages), as JSON-ready data."""
    return {
        "languages": [
            {
                "code": language.code,
                "native": language.native,
                "english": language.english,
                "direction": language.direction,
            }
            for language in LANGUAGES
        ],
        "ui": UI,
    }
