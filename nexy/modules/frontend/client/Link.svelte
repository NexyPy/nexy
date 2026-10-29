<script lang="ts">
  // A client-side link. It renders a normal <a>: without JavaScript it is still a link.
  import type { Snippet } from 'svelte'
  import type { HTMLAnchorAttributes } from 'svelte/elements'
  import { location, type Href } from './client.ts'
  import { getRouter } from './router.ts'
  import { isActive, linkClass, onceVisible, type Prefetch } from './shared.ts'

  type Props = Omit<HTMLAnchorAttributes, 'href'> & {
    href: Href
    /** Replace the history entry instead of adding one. */
    replace?: boolean
    /** Scroll to the top after navigating. */
    scroll?: boolean
    /** On hover, focus or touch ('intent'), when scrolled into view ('viewport'), or never. */
    prefetch?: Prefetch
    /** Added to `class` while the link points at the current page. */
    activeClass?: string
    /** Alias for `activeClass`. */
    activeClassName?: string
    /** Active only on the exact page, not on the pages below it. */
    exact?: boolean
    children?: Snippet
  }

  let {
    href,
    replace = false,
    scroll = true,
    prefetch = 'intent',
    activeClass,
    activeClassName,
    exact = false,
    class: className,
    children,
    onmouseenter,
    onfocus,
    ontouchstart,
    ...rest
  }: Props = $props()

  let anchor: HTMLAnchorElement | undefined = $state()
  const warm = () => {
    if (prefetch === 'intent' || prefetch === true) getRouter()?.prefetch(href)
  }

  $effect(() => {
    if (prefetch === 'viewport' && anchor) return onceVisible(anchor, () => getRouter()?.prefetch(href))
  })
</script>

<a
  bind:this={anchor}
  {...rest}
  {href}
  class={linkClass(className ?? undefined, isActive($location.pathname, href, exact), activeClass ?? activeClassName)}
  aria-current={isActive($location.pathname, href, true) ? 'page' : undefined}
  data-nexy-link="true"
  data-nexy-replace={replace ? '' : undefined}
  data-nexy-scroll={scroll ? undefined : 'false'}
  onmouseenter={(event) => {
    onmouseenter?.(event)
    warm()
  }}
  onfocus={(event) => {
    onfocus?.(event)
    warm()
  }}
  ontouchstart={(event) => {
    ontouchstart?.(event)
    warm()
  }}
>
  {@render children?.()}
</a>
