import { useState, useEffect, useRef, useCallback } from "react";
import { Languages, X, SearchIcon, Check } from "lucide-react";

interface LocaleInfo {
    code: string;
    name: string;
    flag: string;
}

interface NexyLocales {
    current: string;
    available: LocaleInfo[];
}

declare global {
    interface Window {
        __NEXY_LOCALES?: NexyLocales;
    }
}

const LOCALE_FLAG_MAP: Record<string, string> = {
    fr: "fr", en: "gb", es: "es", pt: "pt", de: "de",
    ru: "ru", zh: "cn", ja: "jp", ko: "kr", ar: "sa", hi: "in",
};

const LOCALE_NAMES: Record<string, string> = {
    fr: "Français", en: "English", es: "Español", pt: "Português", de: "Deutsch",
    ru: "Русский", zh: "中文", ja: "日本語", ko: "한국어", ar: "العربية", hi: "हिन्दी",
};

function Language() {
    const [open, setOpen] = useState(false);
    const modalRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);
    const [search, setSearch] = useState("");
    const [activeIndex, setActiveIndex] = useState(0);

    const locales = typeof window !== "undefined" ? window.__NEXY_LOCALES : undefined;
    const currentLocale = locales?.current ?? "en";
    const raw = locales?.available ?? [];
    const available = raw.map((l: any) =>
        typeof l === "string"
            ? { code: l, name: LOCALE_NAMES[l] ?? l, flag: "" }
            : { code: l.code ?? "", name: l.name ?? LOCALE_NAMES[l.code] ?? l.code, flag: l.flag ?? "" }
    );

    const filtered = available.filter((l) =>
        (l.name ?? '').toLowerCase().includes(search.toLowerCase()) ||
        (l.code ?? '').toLowerCase().includes(search.toLowerCase())
    );

    const currentLangInfo = available.find(l => l?.code === currentLocale);

    useEffect(() => {
        function handleClick(e: MouseEvent) {
            if (modalRef.current && !modalRef.current.contains(e.target as Node)) {
                setOpen(false);
            }
        }
        if (open) {
            document.addEventListener("mousedown", handleClick);
            document.body.style.overflow = "hidden";
        }
        return () => {
            document.removeEventListener("mousedown", handleClick);
            document.body.style.overflow = "";
        };
    }, [open]);

    useEffect(() => {
        if (open) {
            setTimeout(() => inputRef.current?.focus(), 50);
            setSearch("");
            setActiveIndex(0);
        }
    }, [open]);

    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === "Escape") {
                setOpen(false);
            }
            if (open) {
                if (e.key === "ArrowDown") {
                    e.preventDefault();
                    setActiveIndex((prev) =>
                        prev >= filtered.length - 1 ? 0 : prev + 1
                    );
                }
                if (e.key === "ArrowUp") {
                    e.preventDefault();
                    setActiveIndex((prev) =>
                        prev <= 0 ? filtered.length - 1 : prev - 1
                    );
                }
                if (e.key === "Enter" && filtered[activeIndex]) {
                    e.preventDefault();
                    switchLocale(filtered[activeIndex].code);
                }
            }
        };
        document.addEventListener("keydown", handleKeyDown);
        return () => document.removeEventListener("keydown", handleKeyDown);
    }, [open, activeIndex, filtered]);

    const switchLocale = useCallback((localeCode: string) => {
        const path = window.location.pathname;
        const segments = path.split("/").filter(Boolean);
        const localeRegex = /^[a-z]{2}(?:-[A-Z]{2})?$/;
        const clean = segments.length > 0 && localeRegex.test(segments[0])
            ? "/" + segments.slice(1).join("/")
            : path;
        setOpen(false);
        window.location.href = "/" + localeCode + (clean === "/" ? "" : clean);
    }, []);

    if (available.length <= 1) {
        return (
            <div className="flex items-center gap-1 font-mono">
                <Languages size={18} />
                {currentLangInfo?.flag ?? ""}
                {currentLocale.toUpperCase()}
            </div>
        );
    }

    return (
        <>
            <button
                onClick={() => setOpen(true)}
                className="flex items-center gap-2 cursor-pointer"
            >
                <Languages size={18} />
                <img
                    src={`https://flagcdn.com/24x18/${LOCALE_FLAG_MAP[currentLocale] || currentLocale}.png`}
                    alt={currentLocale}
                    className="w-6 h-4"
                />
            </button>

            {open && (
                <div className="fixed inset-0 z-[9999] flex items-start justify-center p-4 pt-20 md:pt-32">
                    <div 
                        className="absolute inset-0 bg-black/60 backdrop-blur-sm" 
                        onClick={() => setOpen(false)} 
                    />
                    <div
                        ref={modalRef}
                        className="relative bg-background border border-border rounded-xl shadow-2xl w-full max-w-2xl overflow-hidden"
                    >
                        <div className="flex items-center gap-3 px-4 py-3 border-b border-border">
                            <SearchIcon size={18} className="text-muted-foreground" />
                            <input
                                ref={inputRef}
                                type="text"
                                placeholder="Search language..."
                                value={search}
                                onChange={(e) => {
                                    setSearch(e.target.value);
                                    setActiveIndex(0);
                                }}
                                className="flex-1 bg-transparent outline-none text-foreground placeholder:text-muted-foreground text-base"
                            />
                            <button
                                onClick={() => setOpen(false)}
                                className="p-1.5 hover:bg-muted rounded-md text-muted-foreground transition-colors"
                            >
                                <X size={18} />
                            </button>
                        </div>

                        <div className="max-h-80 overflow-y-auto p-4">
                            {filtered.length === 0 ? (
                                <div className="p-8 text-center text-muted-foreground">
                                    No languages found
                                </div>
                            ) : (
                                <div className="p-2">
                                    {filtered.map((locale, index) => (
                                        <button
                                            key={locale.code ?? index}
                                            onClick={() => switchLocale(locale.code)}
                                            onMouseEnter={() => setActiveIndex(index)}
                                            className={`w-full flex items-center justify-between gap-3 px-3 py-2.5 text-left rounded-lg transition-all ${
                                                index === activeIndex 
                                                    ? "bg-foreground/5 ring-1 ring-foreground/10" 
                                                    : "hover:bg-foreground/5"
                                            }`}
                                        >
                                            <div className="flex items-center gap-3">
                                                <img
                                                    src={`https://flagcdn.com/32x24/${LOCALE_FLAG_MAP[locale.code] || locale.code}.png`}
                                                    alt={locale.name}
                                                    className="w-8 h-6"
                                                />
                                                <span className="font-medium">{locale.name}</span>
                                            </div>
                                            {locale.code === currentLocale ? (
                                                <div className="flex items-center gap-1.5 text-green-500">
                                                    <Check size={16} />
                                                    <span className="text-xs font-medium">Current</span>
                                                </div>
                                            ) : (
                                                <span className="text-xs text-muted-foreground uppercase">{locale.code}</span>
                                            )}
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>
                        
                        <div className="border-t border-border px-4 py-2 flex items-center justify-between text-xs text-muted-foreground">
                            <div className="flex items-center gap-1">
                                <span>Navigate with</span>
                                <kbd className="bg-muted border border-border rounded px-1.5 py-0.5">↑</kbd>
                                <kbd className="bg-muted border border-border rounded px-1.5 py-0.5">↓</kbd>
                            </div>
                            <div className="flex items-center gap-1">
                                <span>Select with</span>
                                <kbd className="bg-muted border border-border rounded px-1.5 py-0.5">Enter</kbd>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}

export default Language;