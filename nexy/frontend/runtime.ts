type CompMod = { default: unknown }
type Importer = () => Promise<CompMod>
type Importers = Record<string, Importer>
import { __NEXY_KEYS } from '@nexy/keys.auto.ts';
const importers: Importers = import.meta.glob('/src/**/*.{tsx,jsx,ts,js,vue,svelte}', { eager: false }) as Record<string, Importer>
const norm = (p: string) => p && p.startsWith('/') ? p : '/' + p
const w: any = window as any;
w.__nexy_import = (p: string) => {
    let key = p;
    if (!key.startsWith('/')) {
        const mapped = (__NEXY_KEYS as any)[key];
        if (mapped) key = mapped;
    }
    const k1 = norm(key);
    const k2 = k1.startsWith('/') ? k1.slice(1) : k1;
    const imp = (importers as any)[k1] || (importers as any)[k2];
    if (!imp) return Promise.reject(new Error('Component not found: ' + p));
    return imp();
}

// Next.js-like Navigation & Prefetching
const prefetched = new Set<string>();
w.__nexy_prefetch = (href: string) => {
    if (!href || href.startsWith('http') || href.startsWith('#') || prefetched.has(href)) return;
    prefetched.add(href);
    const link = document.createElement('link');
    link.rel = 'prefetch';
    link.href = href;
    link.as = 'document';
    document.head.appendChild(link);
};

// Client-side SPA Routing (like Next.js/Turbo)
document.addEventListener('click', async (e: MouseEvent) => {
    const target = e.target as HTMLElement;
    const a = target.closest('a[data-nexy-link]');
    if (!a) return;
    
    const href = a.getAttribute('href');
    if (!href || href.startsWith('http') || href.startsWith('#') || a.getAttribute('target') === '_blank') return;
    if (e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return; // Allow opening in new tab
    
    e.preventDefault();
    
    try {
        const res = await fetch(href);
        if (!res.ok) throw new Error('Fetch failed');
        const html = await res.text();
        
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        
        // Push state
        window.history.pushState({}, '', href);
        
        // Update Title
        if (doc.title) document.title = doc.title;
        
        // Replace body content (preserving layout if possible)
        // If Nexy has a <main id="nexy-layout"> or similar, we could just replace that.
        // For now, replacing body or a specific root.
        const newMain = doc.querySelector('main') || doc.body;
        const currentMain = document.querySelector('main') || document.body;
        
        // View Transitions API for smooth transitions
        if (document.startViewTransition) {
            document.startViewTransition(() => {
                currentMain.innerHTML = newMain.innerHTML;
                window.scrollTo(0, 0);
            });
        } else {
            currentMain.innerHTML = newMain.innerHTML;
            window.scrollTo(0, 0);
        }
        
        // Re-execute scripts in the new content
        const scripts = currentMain.querySelectorAll('script');
        scripts.forEach(oldScript => {
            const newScript = document.createElement('script');
            Array.from(oldScript.attributes).forEach(attr => newScript.setAttribute(attr.name, attr.value));
            newScript.appendChild(document.createTextNode(oldScript.innerHTML));
            oldScript.parentNode?.replaceChild(newScript, oldScript);
        });
    } catch (err) {
        console.error('Navigation failed, falling back to full reload', err);
        window.location.href = href;
    }
});

window.addEventListener('popstate', () => {
    window.location.reload();
});

export { }