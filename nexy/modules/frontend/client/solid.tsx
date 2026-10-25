// Client navigation for Solid: Link, Image and the hooks of the router.
//
//   import { Link, Image, useRouter, usePathname, useParams, useSearchParams } from '@nexy/client'
//
// Solid has no hook rules: each `use*` returns an accessor, read it by calling it.
import { createMemo, createSignal, onCleanup, onMount, splitProps, type Accessor, type JSX } from 'solid-js'
import { isServer } from 'solid-js/web'
import type { Route } from './routes.auto.ts'
import {
  getRouter,
  serverLocation,
  type NavigateOptions,
  type Params,
  type RouterLocation
} from './router.ts'
import {
  cssText,
  imageAttributes,
  isActive,
  linkClass,
  onceVisible,
  warnMissingAlt,
  type ImageProps,
  type Prefetch
} from './shared.ts'

/** A route of the project, with an optional query or fragment, or a link out of the app. */
export type Href =
  | Route
  | `${Route}?${string}`
  | `${Route}#${string}`
  | `${'http' | 'https'}://${string}`
  | `mailto:${string}`
  | `tel:${string}`
  | `#${string}`

/** The current location as an accessor: pathname, search, hash and the params of the route. */
export function useLocation(): Accessor<RouterLocation> {
  const router = getRouter()
  const [location, setLocation] = createSignal<RouterLocation>(router?.getLocation() ?? serverLocation())
  if (!isServer && router) {
    const stop = router.subscribe(() => setLocation(router.getLocation()))
    onCleanup(stop)
  }
  return location
}

export function usePathname(): Accessor<string> {
  const location = useLocation()
  return () => location().pathname
}

export function useParams<T extends Params = Params>(): Accessor<T> {
  const location = useLocation()
  return () => location().params as T
}

export function useSearchParams(): Accessor<URLSearchParams> {
  const location = useLocation()
  return createMemo(() => new URLSearchParams(location().search))
}

const router = {
  push: (href: Href, options?: NavigateOptions) => getRouter()?.navigate(href, options),
  replace: (href: Href, options?: NavigateOptions) => getRouter()?.replace(href, options),
  back: () => getRouter()?.back(),
  forward: () => getRouter()?.forward(),
  refresh: () => getRouter()?.refresh(),
  prefetch: (href: Href) => getRouter()?.prefetch(href)
}

/** Imperative navigation. */
export function useRouter(): typeof router {
  return router
}

export type LinkProps = Omit<JSX.AnchorHTMLAttributes<HTMLAnchorElement>, 'href' | 'ref'> & {
  href: Href
  ref?: (element: HTMLAnchorElement) => void
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

function call<E>(handler: unknown, event: E): void {
  if (typeof handler === 'function') handler(event)
}

export function Link(props: LinkProps): JSX.Element {
  const [own, rest] = splitProps(props, [
    'href', 'replace', 'scroll', 'prefetch', 'activeClassName', 'exact', 'class', 'ref',
    'onMouseEnter', 'onFocus', 'onTouchStart'
  ])
  const location = useLocation()
  const mode = () => own.prefetch ?? 'intent'
  const warm = () => {
    if (mode() === 'intent' || mode() === true) getRouter()?.prefetch(own.href)
  }
  let anchor: HTMLAnchorElement | undefined

  onMount(() => {
    if (mode() === 'viewport' && anchor) onCleanup(onceVisible(anchor, () => getRouter()?.prefetch(own.href)))
  })

  return (
    <a
      {...rest}
      ref={element => {
        anchor = element
        own.ref?.(element)
      }}
      href={own.href}
      class={linkClass(own.class, isActive(location().pathname, own.href, own.exact), own.activeClassName)}
      aria-current={isActive(location().pathname, own.href, true) ? 'page' : undefined}
      data-nexy-link="true"
      data-nexy-replace={own.replace ? '' : undefined}
      data-nexy-scroll={own.scroll === false ? 'false' : undefined}
      onMouseEnter={event => (call(own.onMouseEnter, event), warm())}
      onFocus={event => (call(own.onFocus, event), warm())}
      onTouchStart={event => (call(own.onTouchStart, event), warm())}
    />
  )
}

export type ImageComponentProps = Omit<
  JSX.ImgHTMLAttributes<HTMLImageElement>,
  'src' | 'alt' | 'width' | 'height' | 'loading' | 'sizes' | 'srcset'
> &
  ImageProps

export function Image(props: ImageComponentProps): JSX.Element {
  const [own, rest] = splitProps(props, [
    'src', 'alt', 'width', 'height', 'priority', 'fill', 'loading', 'sizes', 'srcSet', 'style'
  ])
  warnMissingAlt(own.alt)
  const attributes = () => {
    const { style, ...others } = imageAttributes({
      src: own.src, alt: own.alt, width: own.width, height: own.height, priority: own.priority,
      fill: own.fill, loading: own.loading, sizes: own.sizes, srcSet: own.srcSet
    })
    const given = typeof own.style === 'string' ? own.style : cssText(own.style as Record<string, string>)
    return { ...others, style: [cssText(style), given].filter(Boolean).join(';') || undefined }
  }
  return <img {...rest} {...attributes()} />
}
