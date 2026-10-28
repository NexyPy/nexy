// Client navigation for Vue: Link, Image and the composables of the router.
//
//   import { Link, Image, useRouter, usePathname, useParams, useSearchParams } from '@nexy/client'
//
// The components are written with h(), so they are plain TypeScript and need no SFC setup.
import {
  computed,
  defineComponent,
  getCurrentScope,
  h,
  onMounted,
  onScopeDispose,
  ref,
  shallowRef,
  type ComputedRef,
  type PropType,
  type Ref
} from 'vue'
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

/** The current location as a ref: pathname, search, hash and the params of the route. */
export function useLocation(): Readonly<Ref<RouterLocation>> {
  const router = getRouter()
  const location = shallowRef<RouterLocation>(router?.getLocation() ?? serverLocation())
  if (router && getCurrentScope()) {
    onScopeDispose(router.subscribe(() => (location.value = router.getLocation())))
  }
  return location
}

export function usePathname(): ComputedRef<string> {
  const location = useLocation()
  return computed(() => location.value.pathname)
}

export function useParams<T extends Params = Params>(): ComputedRef<T> {
  const location = useLocation()
  return computed(() => location.value.params as T)
}

export function useSearchParams(): ComputedRef<URLSearchParams> {
  const location = useLocation()
  return computed(() => new URLSearchParams(location.value.search))
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

/** Run a listener a user gave to the component (a function or a list of them). */
function callAll(listener: unknown, event: unknown): void {
  for (const fn of Array.isArray(listener) ? listener : [listener]) {
    if (typeof fn === 'function') fn(event)
  }
}

export const Link = defineComponent({
  name: 'Link',
  inheritAttrs: false,
  props: {
    href: { type: String as unknown as PropType<Href>, required: true },
    /** Replace the history entry instead of adding one. */
    replace: Boolean,
    /** Scroll to the top after navigating. */
    scroll: { type: Boolean, default: true },
    /** On hover, focus or touch ('intent'), when scrolled into view ('viewport'), or never. */
    prefetch: { type: [Boolean, String] as PropType<Prefetch>, default: 'intent' },
    /** Added to `class` while the link points at the current page. */
    activeClass: String,
    /** Alias for `activeClass`. */
    activeClassName: String,
    /** Active only on the exact page, not on the pages below it. */
    exact: Boolean
  },
  setup(props, { attrs, slots }) {
    const location = useLocation()
    const element = ref<HTMLAnchorElement | null>(null)
    const warm = () => {
      if (props.prefetch === 'intent' || props.prefetch === true) getRouter()?.prefetch(props.href)
    }
    onMounted(() => {
      if (props.prefetch === 'viewport' && element.value) {
        const stop = onceVisible(element.value, () => getRouter()?.prefetch(props.href))
        if (getCurrentScope()) onScopeDispose(stop)
      }
    })
    const intent = (name: string) => (event: unknown) => {
      callAll(attrs[name], event)
      warm()
    }

    return () => {
      const className = linkClass(
        attrs.class as string | undefined,
        isActive(location.value.pathname, props.href, props.exact),
        props.activeClass ?? props.activeClassName
      )
      const anchor: Record<string, unknown> = {
        ...attrs,
        ref: element,
        href: props.href,
        'aria-current': isActive(location.value.pathname, props.href, true) ? 'page' : undefined,
        'data-nexy-link': 'true',
        'data-nexy-replace': props.replace ? '' : undefined,
        'data-nexy-scroll': props.scroll ? undefined : 'false',
        onMouseenter: intent('onMouseenter'),
        onFocus: intent('onFocus'),
        onTouchstart: intent('onTouchstart')
      }
      // Vue writes class="" for an undefined class: leave the attribute out instead.
      if (className) anchor.class = className
      else delete anchor.class
      return h('a', anchor, slots.default?.())
    }
  }
})

export const Image = defineComponent({
  name: 'Image',
  inheritAttrs: false,
  props: {
    src: { type: String, required: true },
    /** Required: an empty string marks a decorative image. */
    alt: { type: String, required: true },
    width: Number,
    height: Number,
    /** Load now, at high priority: for the image that is visible on arrival. */
    priority: Boolean,
    /** Fill the positioned parent instead of using width and height. */
    fill: Boolean,
    loading: String as PropType<'lazy' | 'eager'>,
    sizes: String,
    srcSet: String
  },
  setup(props, { attrs }) {
    warnMissingAlt(props.alt)
    return () => {
      const { style, srcset, fetchpriority, ...attributes } = imageAttributes({ ...props })
      return h('img', {
        ...attrs,
        ...attributes,
        srcset,
        fetchpriority,
        style: [cssText(style), attrs.style]
      })
    }
  }
})

export { ActionError }
export type { Action, ActionOptions, ActionState }

/** Call an action from a component. Each field is a ref: `pending.value`, `data.value`, `error.value`. */
export function useAction<Input, Output>(action: Action<Input, Output>, options?: ActionOptions<Output>) {
  const store = createActionState(action, options)
  const state = shallowRef(store.getState())
  const stop = store.subscribe(() => (state.value = store.getState()))
  if (getCurrentScope()) onScopeDispose(stop)
  return {
    pending: computed(() => state.value.pending),
    data: computed(() => state.value.data),
    error: computed(() => state.value.error),
    run: store.run,
    reset: store.reset
  }
}
