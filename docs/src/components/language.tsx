import { useState, useEffect, useRef, useCallback } from "react";
import { Languages } from "lucide-react";

interface NexyLocales {
    current: string;
    available: string[];
}

declare global {
    interface Window {
        __NEXY_LOCALES?: NexyLocales;
    }
}

function Language() {
    const [open, setOpen] = useState(false);
    const ref = useRef<HTMLDivElement>(null);

    useEffect(() => {
        function handleClick(e: MouseEvent) {
            if (ref.current && !ref.current.contains(e.target as Node)) {
                setOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClick);
        return () => document.removeEventListener("mousedown", handleClick);
    }, []);

    const locales = typeof window !== "undefined" ? window.__NEXY_LOCALES : undefined;
    const current = locales?.current?.toUpperCase() ?? "EN";
    const available = locales?.available ?? [];

    const switchLocale = useCallback((locale: string) => {
        const path = window.location.pathname;
        const segments = path.split("/").filter(Boolean);
        const localeRegex = /^[a-z]{2}(?:-[A-Z]{2})?$/;
        const clean = segments.length > 0 && localeRegex.test(segments[0])
            ? "/" + segments.slice(1).join("/")
            : path;
        window.location.href = "/" + locale + (clean === "/" ? "" : clean);
    }, []);

    if (available.length <= 1) {
        return (
            <div className="flex items-center gap-1 font-mono">
                <Languages size={18} />
                {current}
            </div>
        );
    }

    return (
        <div ref={ref} className="relative flex items-center gap-1 font-mono">
            <button
                onClick={() => setOpen(!open)}
                className="flex items-center gap-1 cursor-pointer"
            >
                <Languages size={18} />
                {current}
            </button>
            {open && (
                <ul className="absolute top-8 right-0 bg-background border border-border rounded-xl shadow-lg py-1 z-50 min-w-32">
                    {available.map((locale) => (
                        <li key={locale}>
                            <button
                                onClick={() => switchLocale(locale)}
                                className="w-full text-left px-4 py-1.5 text-sm hover:bg-muted transition-colors"
                            >
                                {locale.toUpperCase()}
                            </button>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}

export default Language;