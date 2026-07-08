import { useState, useEffect, useRef, useCallback } from "react";
import { Languages, X, ChevronRight, Check } from "lucide-react";

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

function Language() {
    const [open, setOpen] = useState(false);
    const modalRef = useRef<HTMLDivElement>(null);
    const [activeIndex, setActiveIndex] = useState(0);

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
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === "Escape") {
                setOpen(false);
            }
            if (open) {
                if (e.key === "ArrowDown") {
                    e.preventDefault();
                    setActiveIndex((prev) =>
                        prev >= available.length - 1 ? 0 : prev + 1
                    );
                }
                if (e.key === "ArrowUp") {
                    e.preventDefault();
                    setActiveIndex((prev) =>
                        prev <= 0 ? available.length - 1 : prev - 1
                    );
                }
                if (e.key === "Enter" && available[activeIndex]) {
                    e.preventDefault();
                    switchLocale(available[activeIndex].code);
                }
            }
        };
        document.addEventListener("keydown", handleKeyDown);
        return () => document.removeEventListener("keydown", handleKeyDown);
    }, [open, activeIndex]);

    const locales = typeof window !== "undefined" ? window.__NEXY_LOCALES : undefined;
    const currentLocale = locales?.current ?? "en";
    const available = locales?.available ?? [];

    const currentLangInfo = available.find(l => l.code === currentLocale);

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
                <span className="text-lg">{currentLangInfo?.flag ?? "🌍"}</span>
            </button>

            {open && (
                <div className="fixed inset-0 z-[9999] flex items-start justify-center p-4 pt-20 md:pt-32">
                    <div 
                        className="absolute inset-0 bg-black/60 backdrop-blur-sm" 
                        onClick={() => setOpen(false)} 
                    />
                    <div
                        ref={modalRef}
                        className="relative bg-background border border-border rounded-xl shadow-2xl w-full max-w-md overflow-hidden"
                    >
                        <div className="flex items-center justify-between px-4 py-3 border-b border-border">
                            <h3 className="text-lg font-semibold">Choose Language</h3>
                            <button
                                onClick={() => setOpen(false)}
                                className="p-1.5 hover:bg-muted rounded-md transition-colors"
                            >
                                <X size={18} />
                            </button>
                        </div>

                        <div className="max-h-80 overflow-y-auto">
                            <div className="p-2">
                                {available.map((locale, index) => (
                                    <button
                                        key={locale.code}
                                        onClick={() => switchLocale(locale.code)}
                                        onMouseEnter={() => setActiveIndex(index)}
                                        className={`w-full flex items-center justify-between gap-3 px-3 py-2.5 text-left rounded-lg transition-all ${
                                            index === activeIndex 
                                                ? "bg-foreground/5 ring-1 ring-foreground/10" 
                                                : "hover:bg-foreground/5"
                                        }`}
                                    >
                                        <div className="flex items-center gap-3">
                                            <span className="text-2xl">{locale.flag}</span>
                                            <div className="flex flex-col">
                                                <span className="font-medium">{locale.name}</span>
                                                <span className="text-xs text-muted-foreground uppercase">
                                                    {locale.code}
                                                </span>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-1">
                                            {locale.code === currentLocale && (
                                                <Check size={16} className="text-green-500" />
                                            )}
                                            <ChevronRight size={14} className="text-muted-foreground" />
                                        </div>
                                    </button>
                                ))}
                            </div>
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