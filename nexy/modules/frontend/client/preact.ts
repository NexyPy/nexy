// Client navigation for Preact: Link, Image and the hooks of the router.
//
//   import { Link, Image, useRouter, usePathname, useParams, useSearchParams } from '@nexy/client'
//
// Written with h (no JSX) so it needs no compiler setting of its own.
import { h, type JSX, type Ref } from 'preact'
import { forwardRef, useEffect, useMemo, useRef, useState, useSyncExternalStore } from 'preact/compat'
import type { Route } from './routes.auto.ts'
import {
  getRouter,
  serverLocation,
  type Blocker,
  type NavigateOptions,
  type Params,
  type RouterLocation,
  type RouteMatchInfo,
  type TransitionState
} from './router.ts'
import {
  imageAttributes,
  isActive,
  linkClass,
  onceVisible,
  warnMissingAlt,
  type ImageProps,
  type Prefetch
} from './shared.ts'
import {
  createActionState,
  ActionError,
  type Action,
  type ActionOptions,
  type ActionState
} from './action-runtime.ts'

/** A route of the project, with an optional query or fragment, or a link out of the app. */
export type Href =
  | Route
  | `${Route}?${string}`
  | `${Route}#${string}`
  | `${'http' | 'https'}://${string}`
  | `mailto:${string}`
  | `tel:${string}`
  | `#${string}`

const subscribe = (onChange: () => void): (() => void) => getRouter()?.subscribe(onChange) ?? (() => {})
const snapshot = (): RouterLocation => getRouter()?.getLocation() ?? serverLocation()

/** The current location: pathname, search, hash and the params of the matched route. */
export function useLocation(): RouterLocation {
  // In the browser the first render must see the URL the server rendered: the router has it.
  return useSyncExternalStore(subscribe, snapshot, snapshot)
}

export function usePathname(): string {
  return useLocation().pathname
}

export function useParams<T extends Params = Params>(): T {
  return useLocation().params as T
}

export function useSearchParams(): URLSearchParams {
  const { search } = useLocation()
  return useMemo(() => new URLSearchParams(search), [search])
}

const router = {
  push: (href: Href, options?: NavigateOptions) => getRouter()?.navigate(href, options),
  replace: (href: Href, options?: NavigateOptions) => getRouter()?.replace(href, options),
  back: () => getRouter()?.back(),
  forward: () => getRouter()?.forward(),
  refresh: () => getRouter()?.refresh(),
  prefetch: (href: Href) => getRouter()?.prefetch(href)
}

/** Imperative navigation. The object never changes, so it is safe in a dependency list. */
export function useRouter(): typeof router {
  return router
}

export type LinkProps = Omit<JSX.HTMLAttributes<HTMLAnchorElement>, 'href' | 'ref'> & {
  href: Href
  /** Replace the history entry instead of adding one. */
  replace?: boolean
  /** Scroll to the top after navigating. Default: true. */
  scroll?: boolean
  /** When to load the target page: on hover, focus or touch (`'intent'`, the default), when the
   *  link scrolls into view (`'viewport'`), or never (`false`). */
  prefetch?: Prefetch
  /** Added to `class` while the link points at the current page. */
  activeClassName?: string
  /** Active only on the exact page, not on the pages below it. */
  exact?: boolean
}

export const Link = forwardRef<HTMLAnchorElement, LinkProps>(function Link(
  { href, replace, scroll, prefetch = 'intent', activeClassName, exact, class: className, onMouseEnter, onFocus, onTouchStart, ...rest },
  forwardedRef
) {
  const { pathname } = useLocation()
  const own = useRef<HTMLAnchorElement | null>(null)
  const intent = prefetch === 'intent' || prefetch === true
  // `onMouseEnter`, `onFocus` and `onTouchStart` are the moments a click is likely: warm the page.
  const onIntent = <E,>(handler?: (event: E) => void) => (event: E) => {
    handler?.(event)
    if (intent) getRouter()?.prefetch(href)
  }

  useEffect(() => {
    if (prefetch !== 'viewport' || !own.current) return
    return onceVisible(own.current, () => getRouter()?.prefetch(href))
  }, [prefetch, href])

  const setRef: Ref<HTMLAnchorElement> = node => {
    own.current = node
    if (typeof forwardedRef === 'function') forwardedRef(node)
    else if (forwardedRef) (forwardedRef as { current: HTMLAnchorElement | null }).current = node
  }

  return h('a', {
    ...rest,
    ref: setRef,
    href,
    class: linkClass(className as string | undefined, isActive(pathname, href, exact), activeClassName),
    'aria-current': isActive(pathname, href, true) ? 'page' : undefined,
    'data-nexy-link': 'true',
    'data-nexy-replace': replace ? '' : undefined,
    'data-nexy-scroll': scroll === false ? 'false' : undefined,
    onMouseEnter: onIntent(onMouseEnter),
    onFocus: onIntent(onFocus),
    onTouchStart: onIntent(onTouchStart)
  })
})

export type ImageComponentProps = Omit<JSX.HTMLAttributes<HTMLImageElement>, 'src' | 'alt' | 'width' | 'height' | 'loading' | 'sizes' | 'srcSet' | 'ref'> &
  ImageProps

export const Image = forwardRef<HTMLImageElement, ImageComponentProps>(function Image(
  { src, alt, width, height, priority, fill, loading, sizes, srcSet, style, ...rest },
  ref
) {
  warnMissingAlt(alt)
  const { fetchpriority, srcset, style: computed, ...attributes } = imageAttributes({
    src, alt, width, height, priority, fill, loading, sizes, srcSet
  })
  return h('img', {
    ...rest,
    ...attributes,
    ref,
    srcset,
    fetchpriority,
    style: { ...computed, ...(style as object) }
  })
})

/** Match a pathname against the routes: the route and its params, or null when none matches. */
export function useMatch(pathname: string): RouteMatchInfo {
  const router = getRouter()
  return useMemo(() => router?.matchPath(pathname) ?? { match: null, found: false }, [router, pathname])
}

/** Block navigation when `blocker` returns a reason (string) or a promise of one. */
export function useBlocker(blocker: Blocker): void {
  const router = getRouter()
  useEffect(() => {
    if (!router) return
    const stop = router.blocker(blocker)
    return stop
  }, [router, blocker])
}

/** The in-flight navigation state: `{ pending, next }`. Read it for a loading boundary. */
export function useTransition(): TransitionState {
  const router = getRouter()
  return useSyncExternalStore(
    () => {
      if (!router) return () => {}
      return router.subscribe(() => {})
    },
    () => router?.transition() ?? { pending: false, next: null },
    () => ({ pending: false, next: null })
  )
}

/** Catch errors during client rendering and show a fallback instead of crashing the page. */
export type ErrorBoundaryProps = {
  /** Rendered when a descendant throws during client navigation. */
  fallback: (error: Error, reset: () => void) => JSX.Element
  children?: JSX.Element
}

export function ErrorBoundary({ fallback, children }: ErrorBoundaryProps) {
  const [error, setError] = useState<Error | null>(null)
  const reset = () => setError(null)
  if (error) return fallback(error, reset)
  return children ?? null
}

export { ActionError }
export type { Action, ActionOptions, ActionState }

/** Call an action from a component: `const { run, pending, data, error } = useAction(createUser)`. */
export function useAction<Input, Output>(action: Action<Input, Output>, options?: ActionOptions<Output>) {
  const store = useMemo(() => createActionState(action, options), [action])
  const state = useSyncExternalStore(store.subscribe, store.getState, store.getState)
  return { ...state, run: store.run, reset: store.reset }
}
