import { SearchIcon, X, ChevronRight } from "lucide-react";
import { useState, useEffect, useRef, useCallback } from "react";

interface SearchDoc {
    id: number;
    title: string;
    content: string;
    href: string;
    lang: string;
}

interface NexyLocales {
    current: string;
    available: { code: string; name: string; flag: string }[];
}

declare global {
    interface Window {
        __NEXY_LOCALES?: NexyLocales;
    }
}

let index: SearchDoc[] | null = null;
let indexLoading = false;
const loadQueue: (() => void)[] = [];

function ensureIndex(): Promise<SearchDoc[]> {
    if (index) return Promise.resolve(index);
    if (indexLoading) {
        return new Promise((resolve) => loadQueue.push(() => resolve(index!)));
    }
    indexLoading = true;
    return fetch("/public/search_index.json")
        .then((r) => r.json())
        .then((docs: SearchDoc[]) => {
            index = docs;
            indexLoading = false;
            loadQueue.splice(0).forEach((fn) => fn());
            return docs;
        })
        .catch((err) => {
            console.error("Search index load failed:", err);
            indexLoading = false;
            return [];
        });
}

function scoreItem(query: string, doc: SearchDoc): number {
    const q = query.toLowerCase();
    const title = doc.title.toLowerCase();
    const content = doc.content.toLowerCase();

    let score = 0;

    if (title === q) score += 100;
    else if (title.startsWith(q)) score += 80;
    else if (title.includes(q)) score += 60;

    const titleWords = q.split(/\s+/).filter(Boolean);
    const titleMatches = titleWords.filter((w) => title.includes(w)).length;
    score += (titleMatches / Math.max(titleWords.length, 1)) * 40;

    if (content.startsWith(q)) score += 30;
    else if (content.includes(q)) score += 20;

    const contentMatches = titleWords.filter((w) => content.includes(w)).length;
    score += (contentMatches / Math.max(titleWords.length, 1)) * 10;

    return score;
}

function searchDocs(query: string, locale: string): SearchDoc[] {
    if (!query.trim() || !index) return [];

    const localeDocs = index.filter((d) => d.lang === locale);

    const scored = localeDocs
        .map((doc) => ({ doc, score: scoreItem(query, doc) }))
        .filter((s) => s.score > 0)
        .sort((a, b) => b.score - a.score);

    return scored.map((s) => s.doc).slice(0, 50);
}

function Search() {
    const [open, setOpen] = useState(false);
    const [search, setSearch] = useState("");
    const [results, setResults] = useState<SearchDoc[]>([]);
    const [loading, setLoading] = useState(false);
    const [ready, setReady] = useState(0);
    const [activeIndex, setActiveIndex] = useState(0);
    const inputRef = useRef<HTMLInputElement>(null);
    const currentLocale =
        typeof window !== "undefined"
            ? window.__NEXY_LOCALES?.current ?? "en"
            : "en";

    useEffect(() => {
        if (!open) return;
        setLoading(true);
        ensureIndex().then(() => {
            setLoading(false);
            setReady((n) => n + 1);
        });
    }, [open]);

    useEffect(() => {
        if (!search.trim()) {
            setResults([]);
            return;
        }
        setResults(searchDocs(search, currentLocale));
        setActiveIndex(0);
    }, [search, currentLocale, ready]);

    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
                e.preventDefault();
                setOpen(!open);
                setActiveIndex(0);
            }
            if (e.key === "Escape") {
                setOpen(false);
            }
            if (open) {
                if (e.key === "ArrowDown") {
                    e.preventDefault();
                    setActiveIndex((prev) =>
                        prev >= results.length - 1 ? 0 : prev + 1
                    );
                }
                if (e.key === "ArrowUp") {
                    e.preventDefault();
                    setActiveIndex((prev) =>
                        prev <= 0 ? results.length - 1 : prev - 1
                    );
                }
                if (e.key === "Enter" && results[activeIndex]) {
                    e.preventDefault();
                    handleItemClick(results[activeIndex].href);
                }
            }
        };

        document.addEventListener("keydown", handleKeyDown);
        return () => document.removeEventListener("keydown", handleKeyDown);
    }, [open, results, activeIndex]);

    useEffect(() => {
        if (open) {
            setTimeout(() => inputRef.current?.focus(), 50);
            document.body.style.overflow = "hidden";
            setSearch("");
            setResults([]);
            setActiveIndex(0);
        } else {
            document.body.style.overflow = "";
        }
    }, [open]);

    const handleItemClick = useCallback((href: string) => {
        setOpen(false);
        window.location.href = href;
    }, []);

    return (
        <>
            <button
                onClick={() => setOpen(true)}
                className="flex items-center gap-2 text-sm text-muted-foreground border border-border dark:border-border/40 rounded-full px-3 py-1.5 bg-gray-100/20 dark:bg-gray-50/5 hover:bg-muted transition-all duration-200"
            >
                <SearchIcon size={14} />
                <span className="hidden xs:inline">Search</span>
                <div className="flex items-center gap-1">
                    <kbd className="hidden sm:inline-flex items-center justify-center text-xs font-medium text-muted-foreground bg-muted border border-border rounded px-1.5 py-0.5">
                        ⌘
                    </kbd>
                    <kbd className="inline-flex items-center justify-center text-xs font-medium text-muted-foreground bg-muted border border-border rounded px-1.5 py-0.5">
                        K
                    </kbd>
                </div>
            </button>

            {open && (
                <div className="fixed inset-0 z-[9999] flex items-start justify-center p-4 pt-20 md:pt-32">
                    <div
                        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                        onClick={() => setOpen(false)}
                    />
                    <div className="relative bg-background border border-border rounded-xl shadow-2xl w-full max-w-2xl overflow-hidden">
                        <div className="flex items-center gap-3 px-4 py-3 border-b border-border">
                            <SearchIcon size={18} className="text-muted-foreground" />
                            <input
                                ref={inputRef}
                                type="text"
                                placeholder="Search the docs..."
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

                        <div className="max-h-80 overflow-y-auto">
                            {loading ? (
                                <div className="p-8 text-center text-muted-foreground">
                                    Loading search index...
                                </div>
                            ) : !search.trim() ? (
                                <div className="p-8 text-center text-muted-foreground">
                                    Type to search the docs...
                                </div>
                            ) : results.length === 0 ? (
                                <div className="p-8 text-center text-muted-foreground">
                                    No results found
                                </div>
                            ) : (
                                <div className="p-2">
                                    {results.map((item, index) => (
                                        <button
                                            key={item.id}
                                            onClick={() => handleItemClick(item.href)}
                                            onMouseEnter={() => setActiveIndex(index)}
                                            className={`w-full flex items-center justify-between gap-3 px-3 py-2.5 text-left rounded-lg transition-all ${
                                                index === activeIndex
                                                    ? "bg-foreground/5 ring-1 ring-foreground/10"
                                                    : "hover:bg-foreground/5"
                                            }`}
                                        >
                                            <div className="flex items-center gap-3 min-w-0">
                                                <SearchIcon size={16} className="text-muted-foreground shrink-0" />
                                                <span className="font-medium truncate">{item.title}</span>
                                            </div>
                                            <div className="flex items-center gap-1 shrink-0">
                                                <span className="text-xs text-muted-foreground truncate max-w-40 hidden md:inline">
                                                    {item.href}
                                                </span>
                                                <ChevronRight size={14} className="text-muted-foreground" />
                                            </div>
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

export default Search;
