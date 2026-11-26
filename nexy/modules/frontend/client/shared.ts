// Logic every framework adapter shares, so Link and Image behave the same in React, Preact, Solid,
// Vue and Svelte. No framework API appears here.

import { withBase } from './router.ts'
import type { RouterLocation } from './router.ts'
import { BASE_PATH } from './base-path.auto.ts'
import { IMAGE_VARIANTS } from './image-manifest.auto.ts'

/** The href the browser sees; a route string stays prefix-free inside the application. */
export function withBaseHref(href: string, base: string = BASE_PATH): string {
  return withBase(href, base)
}

function prefixedSrcSet(value: string): string {
  return value
    .split(',')
    .map(candidate => {
      const [url, ...descriptors] = candidate.trim().split(/\s+/)
      return [withBaseHref(url), ...descriptors].join(' ')
    })
    .join(', ')
}

/** The path of an href, without query, fragment or trailing slash ("/" stays "/"). */
export function pathOf(href: string): string {
  const path = href.split('#')[0].split('?')[0]
  return path.length > 1 ? path.replace(/\/+$/, '') : path || '/'
}

/** True when `href` points at the page `pathname`, or (unless `exact`) at one of its parents. */
export function isActive(pathname: string, href: string, exact = false): boolean {
  const current = pathOf(pathname)
  const target = pathOf(href)
  if (current === target) return true
  if (exact || target === '/') return false
  return current.startsWith(target + '/')
}

export type ImageProps = {
  src: string
  /** Required: an empty string marks a decorative image. */
  alt: string
  width?: number
  height?: number
  /** Load now, at high priority: for the image that is visible on arrival. */
  priority?: boolean
  /** Fill the positioned parent instead of using width and height. */
  fill?: boolean
  loading?: 'lazy' | 'eager'
  sizes?: string
  srcSet?: string
}

export type ImageAttributes = {
  src: string
  alt: string
  width?: number
  height?: number
  loading: 'lazy' | 'eager'
  decoding: 'async' | 'auto'
  fetchpriority?: 'high'
  sizes?: string
  srcset?: string
  /** camelCase CSS properties. */
  style?: Record<string, string>
}

const FILL_STYLE: Record<string, string> = {
  position: 'absolute',
  inset: '0',
  width: '100%',
  height: '100%',
  objectFit: 'cover'
}

/** The generated variants of a local image, when `nx build` has seen it. */
function imageVariant(src: string) {
  const key = src.split('?')[0].split('#')[0].replace(/^\.\//, '').replace(/^\//, '')
  return IMAGE_VARIANTS[key]
}

/** The attributes of the `<img>` an Image component renders. */
export function imageAttributes(props: ImageProps): ImageAttributes {
  const variant = imageVariant(props.src)
  const attributes: ImageAttributes = {
    src: withBaseHref(variant ? variant.src : props.src),
    alt: props.alt,
    loading: props.loading ?? (props.priority ? 'eager' : 'lazy'),
    decoding: props.priority ? 'auto' : 'async'
  }
  if (props.priority) attributes.fetchpriority = 'high'
  if (props.sizes) attributes.sizes = props.sizes
  else if (variant) attributes.sizes = variant.sizes
  if (props.srcSet) attributes.srcset = prefixedSrcSet(props.srcSet)
  else if (variant) attributes.srcset = prefixedSrcSet(variant.srcset)
  if (props.fill) {
    attributes.style = { ...FILL_STYLE }
  } else {
    const width = props.width ?? variant?.width
    const height = props.height ?? variant?.height
    if (width !== undefined) attributes.width = width
    if (height !== undefined) attributes.height = height
    // The attributes give the browser the aspect ratio; this keeps it when CSS resizes the width.
    if (width !== undefined && height !== undefined) {
      attributes.style = { height: 'auto', maxWidth: '100%' }
    }
  }
  return attributes
}

/** `{ maxWidth: '100%' }` as `max-width:100%` for frameworks that take a style string. */
export function cssText(style: Record<string, string> | undefined): string {
  if (!style) return ''
  return Object.entries(style)
    .map(([name, value]) => `${name.replace(/[A-Z]/g, letter => '-' + letter.toLowerCase())}:${value}`)
    .join(';')
}

let warnedAlt = false

/** Development hint, once: an image without alt text is invisible to screen readers. */
export function warnMissingAlt(alt: unknown): void {
  if (alt !== undefined || warnedAlt) return
  warnedAlt = true
  console.warn('[Nexy] <Image> needs an alt attribute. Use alt="" for a decorative image.')
}

/** Call `callback` once when `element` first scrolls into view. Returns a function that stops. */
export function onceVisible(element: Element, callback: () => void): () => void {
  if (typeof IntersectionObserver === 'undefined') return () => {}
  const observer = new IntersectionObserver(entries => {
    if (entries.some(entry => entry.isIntersecting)) {
      observer.disconnect()
      callback()
    }
  })
  observer.observe(element)
  return () => observer.disconnect()
}

export type Prefetch = boolean | 'intent' | 'viewport'

/** The class names of a link: its own, plus `active` when the page is the link's target. */
export function linkClass(base: string | undefined, active: boolean, activeClass: string | undefined): string | undefined {
  const names = [base, active ? activeClass : undefined].filter(Boolean)
  return names.length ? names.join(' ') : undefined
}

/** The query string of a location as URLSearchParams. */
export function searchParamsOf(location: RouterLocation): URLSearchParams {
  return new URLSearchParams(location.search)
}
