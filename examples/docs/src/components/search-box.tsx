import { useEffect, useRef, useState, type KeyboardEvent } from "react";

type Hit = { title: string; heading: string; url: string; snippet: string };

// A real form: without JavaScript, Enter opens /search?q=... on the server. Once this island runs,
// results come as you type, from /api/search, the same search as JSON.
export default function SearchBox() {
  const [query, setQuery] = useState("");
  const [hits, setHits] = useState<Hit[]>([]);
  const [active, setActive] = useState(-1);
  const [open, setOpen] = useState(false);
  const input = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const focus = (event: globalThis.KeyboardEvent) => {
      const typing = (event.target as HTMLElement).closest("input, textarea");
      const shortcut = event.key === "k" && (event.ctrlKey || event.metaKey);
      if (shortcut || (event.key === "/" && !typing)) {
        event.preventDefault();
        input.current?.focus();
      }
    };
    document.addEventListener("keydown", focus);
    return () => document.removeEventListener("keydown", focus);
  }, []);

  useEffect(() => {
    if (!query.trim()) return setHits([]);
    const request = new AbortController();
    const timer = setTimeout(async () => {
      try {
        const answer = await fetch(`/api/search?q=${encodeURIComponent(query)}`, { signal: request.signal });
        setHits(await answer.json());
        setActive(-1);
      } catch {
        // Aborted by the next keystroke, or offline: Enter still opens the /search page.
      }
    }, 120);
    return () => {
      clearTimeout(timer);
      request.abort();
    };
  }, [query]);

  function move(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === "Escape") return setOpen(false);
    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      event.preventDefault();
      setOpen(true);
      const step = event.key === "ArrowDown" ? 1 : -1;
      setActive((at) => (hits.length ? (at + step + hits.length) % hits.length : -1));
    }
    if (event.key === "Enter" && active >= 0 && hits[active]) {
      event.preventDefault();
      window.location.assign(hits[active].url);
    }
  }

  const showing = open && query.trim() !== "";
  return (
    <form action="/search" method="get" role="search" className="relative w-full">
      <label htmlFor="docs-search" className="sr-only">Search the docs</label>
      <input
        ref={input}
        id="docs-search"
        name="q"
        type="search"
        autoComplete="off"
        placeholder="Search the docs"
        role="combobox"
        aria-expanded={showing && hits.length > 0}
        aria-controls="docs-search-results"
        aria-autocomplete="list"
        aria-activedescendant={active >= 0 ? `docs-search-hit-${active}` : undefined}
        value={query}
        onChange={(event) => {
          setQuery(event.target.value);
          setOpen(true);
        }}
        onFocus={() => setOpen(true)}
        onBlur={() => setTimeout(() => setOpen(false), 150)}
        onKeyDown={move}
        className="h-11 w-full rounded-lg border border-border bg-background-second pl-10 pr-16 text-sm placeholder:text-foreground-second focus:border-accent focus:outline-none"
      />
      <svg viewBox="0 0 24 24" className="pointer-events-none absolute left-3.5 top-1/2 size-4 -translate-y-1/2 text-foreground-second" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
        <circle cx="11" cy="11" r="7" />
        <path d="M20 20l-3.5-3.5" />
      </svg>
      <kbd className="pointer-events-none absolute right-3 top-1/2 hidden -translate-y-1/2 rounded border border-border px-1.5 font-sans text-xs text-foreground-second sm:block">Ctrl K</kbd>
      {showing && (
        <div className="absolute inset-x-0 top-12 z-30 overflow-hidden rounded-xl border border-border bg-background shadow-xl">
          {hits.length > 0 ? (
            <ul id="docs-search-results" role="listbox" aria-label="Results" className="max-h-[60vh] overflow-y-auto py-1">
              {hits.map((hit, at) => (
                <li key={hit.url} id={`docs-search-hit-${at}`} role="option" aria-selected={at === active}>
                  <a
                    href={hit.url}
                    onMouseDown={(event) => event.preventDefault()}
                    className={`block px-4 py-2.5 ${at === active ? "bg-background-second" : "hover:bg-background-second"}`}
                  >
                    <span className="block text-sm font-medium">
                      {hit.title}
                      {hit.heading !== hit.title && <span className="text-foreground-second"> / {hit.heading}</span>}
                    </span>
                    <span className="mt-0.5 block truncate text-xs text-foreground-second">{hit.snippet}</span>
                  </a>
                </li>
              ))}
            </ul>
          ) : (
            <p role="status" className="px-4 py-3 text-sm text-foreground-second">
              No page has every word of "{query}". Press Enter to see the search page.
            </p>
          )}
        </div>
      )}
    </form>
  );
}
