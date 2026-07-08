import { SearchIcon, X, ChevronRight } from "lucide-react";
import { useState, useEffect, useRef, useCallback } from "react";

const SEARCH_ITEMS = [
    { title: "Introduction", href: "/docs" },
    { title: "Getting Started", href: "/docs/getting-started" },
    { title: "Components - Usage", href: "/docs/components/usage" },
    { title: "Components - Image", href: "/docs/components/image" },
    { title: "Components - Video", href: "/docs/components/video" },
    { title: "Components - Audio", href: "/docs/components/audio" },
    { title: "Components - Link", href: "/docs/components/link" },
    { title: "Components - Form", href: "/docs/components/form" },
    { title: "Components - Script", href: "/docs/components/script" },
    { title: "Components - Import", href: "/docs/components/import" },
    { title: "Components - Template", href: "/docs/components/template" },
    { title: "Vite", href: "/docs/frontend/vite" },
    { title: "Configuration", href: "/docs/config" },
    { title: "CLI Commands", href: "/docs/cli" },
];

function Search() {
    const [open, setOpen] = useState(false);
    const [search, setSearch] = useState("");
    const [activeIndex, setActiveIndex] = useState(0);
    const inputRef = useRef<HTMLInputElement>(null);

    const filteredItems = SEARCH_ITEMS.filter((item) =>
        item.title.toLowerCase().includes(search.toLowerCase())
    );

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
                        prev >= filteredItems.length - 1 ? 0 : prev + 1
                    );
                }
                if (e.key === "ArrowUp") {
                    e.preventDefault();
                    setActiveIndex((prev) =>
                        prev <= 0 ? filteredItems.length - 1 : prev - 1
                    );
                }
                if (e.key === "Enter" && filteredItems[activeIndex]) {
                    e.preventDefault();
                    handleItemClick(filteredItems[activeIndex].href);
                }
            }
        };

        document.addEventListener("keydown", handleKeyDown);
        return () => document.removeEventListener("keydown", handleKeyDown);
    }, [open, filteredItems, activeIndex]);

    useEffect(() => {
        if (open) {
            setTimeout(() => inputRef.current?.focus(), 50);
            document.body.style.overflow = "hidden";
            setActiveIndex(0);
        } else {
            setSearch("");
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
                            {filteredItems.length === 0 ? (
                                <div className="p-8 text-center text-muted-foreground">
                                    No results found
                                </div>
                            ) : (
                                <div className="p-2">
                                    {filteredItems.map((item, index) => (
                                        <button
                                            key={item.href}
                                            onClick={() => handleItemClick(item.href)}
                                            onMouseEnter={() => setActiveIndex(index)}
                                            className={`w-full flex items-center justify-between gap-3 px-3 py-2.5 text-left rounded-lg transition-all ${
                                                index === activeIndex 
                                                    ? "bg-foreground/5 ring-1 ring-foreground/10" 
                                                    : "hover:bg-foreground/5"
                                            }`}
                                        >
                                            <div className="flex items-center gap-3">
                                                <SearchIcon size={16} className="text-muted-foreground" />
                                                <span className="font-medium">{item.title}</span>
                                            </div>
                                            <div className="flex items-center gap-1">
                                                <span className="text-xs text-muted-foreground">
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