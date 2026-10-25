// Client router shared by every framework adapter (React, Preact, Solid, Vue, Svelte).
//
// One store holds the current location; `navigate` renders the next page and only then moves the
// URL, so a failed render never leaves the address bar on a page that is not shown. A newer
// navigation cancels an older one that is still rendering. The adapters (Link, Image, hooks) are
// thin: they read this store and call these functions.

export type Params = Record<string, string>

export type RouterLocation = {
  pathname: string
  search: string
  hash: string
  params: Params
}

export type RouteMatch = { file: string; layouts: string[]; params: Params }

export type NavigateOptions = {
  /** Replace the current history entry instead of adding one. */
  replace?: boolean
  /** Scroll to the top (or to the hash target) once the page is shown. Default: true. */
  scroll?: boolean
}

export type RouterOptions = {
  /** The route that serves a pathname, or null when the server must answer it. */
  match: (pathname: string) => RouteMatch | null
  /** Show the page of a route. Rejects when it cannot. */
  render: (match: RouteMatch) => Promise<void>
  /** Warm the modules of a route. A rejection lets a later hover try again. */
  prefetch?: (match: RouteMatch) => unknown
  /** The window to drive. Default: the global one. */
  win?: Window & typeof globalThis
}

type HistoryState = { nexy: true; scroll?: { x: number; y: number } }

export type Router = ReturnType<typeof createRouter>

/** Location a server-rendered page sees: the request URL, set by the document renderer. */
export const SERVER_LOCATION_KEY = '__NEXY_LOCATION__'

function parse(win: Window, href: string): URL | null {
  try {
    return new URL(href, win.location.href)
  } catch {
    return null
  }
}

/** Query string as an object; a key given twice keeps its last value. */
export function searchParamsOf(search: string): Record<string, string> {
  const out: Record<string, string> = {}
  new URLSearchParams(search).forEach((value, key) => {
    out[key] = value
  })
  return out
}

export function createRouter(options: RouterOptions) {
  const win = options.win ?? (window as Window & typeof globalThis)
  const listeners = new Set<() => void>()
  const prefetched = new Set<string>()
  let navigation = 0
  let location = read()

  function read(): RouterLocation {
    const { pathname, search, hash } = win.location
    return { pathname, search, hash, params: options.match(pathname)?.params ?? {} }
  }

  function commit(next: RouterLocation): void {
    const same =
      next.pathname === location.pathname &&
      next.search === location.search &&
      next.hash === location.hash
    if (same) return
    location = next
    listeners.forEach(listener => listener())
  }

  function saveScroll(): void {
    const state = (win.history.state ?? {}) as Partial<HistoryState>
    win.history.replaceState(
      { ...state, nexy: true, scroll: { x: win.scrollX, y: win.scrollY } },
      ''
    )
  }

  function scrollAfter(hash: string, scroll: boolean, saved?: { x: number; y: number }): void {
    if (saved) return void win.scrollTo(saved.x, saved.y)
    if (!scroll) return
    const id = decodeURIComponent(hash.replace(/^#/, ''))
    const target = id ? win.document.getElementById(id) : null
    if (target) target.scrollIntoView()
    else win.scrollTo(0, 0)
  }

  function announce(next: RouterLocation): void {
    win.document.dispatchEvent(
      new win.CustomEvent('nexy:navigated', {
        detail: { pathname: next.pathname, params: next.params }
      })
    )
  }

  /** Show `url` without touching history; resolves false when the server has to take over. */
  async function show(url: URL, id: number): Promise<boolean> {
    const match = options.match(url.pathname)
    if (!match) {
      win.location.assign(url.href)
      return false
    }
    try {
      await options.render(match)
    } catch (error) {
      console.error('[Nexy] Client navigation failed:', error)
      if (id === navigation) win.location.assign(url.href)
      return false
    }
    return id === navigation
  }

  async function navigate(href: string, opts: NavigateOptions = {}): Promise<boolean> {
    const url = parse(win, href)
    if (!url || url.origin !== win.location.origin) {
      if (url) win.location.assign(url.href)
      return false
    }
    const current = win.location
    const samePage = url.pathname === current.pathname && url.search === current.search
    if (samePage && url.hash === current.hash) return true

    const id = ++navigation
    saveScroll()

    if (samePage) {
      // Only the fragment changes: the browser scrolls, there is nothing to render.
      win.history[opts.replace ? 'replaceState' : 'pushState']({ nexy: true }, '', url.href)
      commit(read())
      scrollAfter(url.hash, opts.scroll !== false)
      return true
    }

    if (!(await show(url, id))) return false
    win.history[opts.replace ? 'replaceState' : 'pushState']({ nexy: true }, '', url.href)
    commit(read())
    announce(location)
    scrollAfter(url.hash, opts.scroll !== false)
    return true
  }

  async function restore(): Promise<void> {
    const url = new URL(win.location.href)
    const state = win.history.state as Partial<HistoryState> | null
    const samePage = url.pathname === location.pathname && url.search === location.search
    if (samePage) {
      commit(read())
      scrollAfter(url.hash, true, state?.scroll)
      return
    }
    const id = ++navigation
    if (!(await show(url, id))) return
    commit(read())
    announce(location)
    scrollAfter(url.hash, true, state?.scroll)
  }

  function prefetch(href: string): void {
    const url = parse(win, href)
    if (!url || url.origin !== win.location.origin) return
    const match = options.match(url.pathname)
    if (!match || prefetched.has(match.file)) return
    prefetched.add(match.file)
    const warming = options.prefetch?.(match)
    if (warming instanceof Promise) warming.catch(() => prefetched.delete(match.file))
  }

  /** True when a click on `anchor` should be a client navigation. */
  function shouldIntercept(event: MouseEvent, anchor: HTMLAnchorElement): boolean {
    if (event.defaultPrevented || event.button !== 0) return false
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return false
    if (anchor.hasAttribute('download') || anchor.hasAttribute('data-nexy-reload')) return false
    const target = anchor.getAttribute('target')
    if (target && target !== '_self') return false
    if ((anchor.getAttribute('rel') ?? '').split(/\s+/).includes('external')) return false
    const href = anchor.getAttribute('href')
    if (!href || href.startsWith('#')) return false
    const url = parse(win, href)
    if (!url || url.origin !== win.location.origin) return false
    return options.match(url.pathname) !== null
  }

  function onClick(event: MouseEvent): void {
    const origin = event.target as Element | null
    const anchor = origin?.closest?.('a[href]') as HTMLAnchorElement | null
    if (!anchor || !shouldIntercept(event, anchor)) return
    event.preventDefault()
    // A Link states its options as attributes: the click is handled here, once, for every framework.
    void navigate(anchor.getAttribute('href') as string, {
      replace: anchor.hasAttribute('data-nexy-replace'),
      scroll: anchor.getAttribute('data-nexy-scroll') !== 'false'
    })
  }

  function onPop(): void {
    void restore()
  }

  function start(): () => void {
    win.document.addEventListener('click', onClick)
    win.addEventListener('popstate', onPop)
    // The browser would restore the scroll before the page is rendered: do it ourselves.
    if ('scrollRestoration' in win.history) win.history.scrollRestoration = 'manual'
    return () => {
      win.document.removeEventListener('click', onClick)
      win.removeEventListener('popstate', onPop)
    }
  }

  return {
    /** The current location. The object changes identity only when the location changes. */
    getLocation: (): RouterLocation => location,
    subscribe(listener: () => void): () => void {
      listeners.add(listener)
      return () => void listeners.delete(listener)
    },
    navigate,
    push: (href: string, opts?: NavigateOptions) => navigate(href, opts),
    replace: (href: string, opts?: NavigateOptions) => navigate(href, { ...opts, replace: true }),
    back: () => win.history.back(),
    forward: () => win.history.forward(),
    refresh: async () => {
      const url = new URL(win.location.href)
      const id = ++navigation
      return show(url, id)
    },
    prefetch,
    start,
    shouldIntercept
  }
}

/** The router the runtime installed, or null before it starts and during server rendering. */
export function getRouter(): Router | null {
  const g = globalThis as unknown as { __nexy_router?: Router }
  return g.__nexy_router ?? null
}

const ROOT: RouterLocation = Object.freeze({ pathname: '/', search: '', hash: '', params: {} })

/** What a page sees during server rendering: the request location, or the root. */
export function serverLocation(): RouterLocation {
  const g = globalThis as unknown as Record<string, RouterLocation | undefined>
  return g[SERVER_LOCATION_KEY] ?? ROOT
}
