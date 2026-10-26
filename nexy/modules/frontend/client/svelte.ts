// Client navigation for Svelte: stores for the location, and the router object.
//
//   import { router, pathname, params, searchParams } from '@nexy/client'
//   import Link from '@nexy/Link.svelte'
//   import Image from '@nexy/Image.svelte'
//
// Link and Image are components, so they keep their .svelte extension; the stores are read with
// the usual `$pathname` syntax.
import type { Readable } from 'svelte/store'
import type { Route } from './routes.auto.ts'
import {
  getRouter,
  serverLocation,
  type NavigateOptions,
  type Params,
  type RouterLocation
} from './router.ts'
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

/** Derive a store from the location. Computed per subscriber: a server renders many requests. */
function select<T>(read: (location: RouterLocation) => T): Readable<T> {
  return {
    subscribe(run) {
      const router = getRouter()
      run(read(router?.getLocation() ?? serverLocation()))
      return router ? router.subscribe(() => run(read(router.getLocation()))) : () => {}
    }
  }
}

/** The current location: pathname, search, hash and the params of the matched route. */
export const location: Readable<RouterLocation> = select(value => value)
export const pathname: Readable<string> = select(value => value.pathname)
export const params: Readable<Params> = select(value => value.params)
export const searchParams: Readable<URLSearchParams> = select(value => new URLSearchParams(value.search))

/** Imperative navigation. */
export const router = {
  push: (href: Href, options?: NavigateOptions) => getRouter()?.navigate(href, options),
  replace: (href: Href, options?: NavigateOptions) => getRouter()?.replace(href, options),
  back: () => getRouter()?.back(),
  forward: () => getRouter()?.forward(),
  refresh: () => getRouter()?.refresh(),
  prefetch: (href: Href) => getRouter()?.prefetch(href)
}

export { ActionError }
export type { Action, ActionOptions, ActionState }

/** Call an action from a component: `const save = useAction(createUser)`, then `$save.pending` and `save.run(input)`. */
export function useAction<Input, Output>(action: Action<Input, Output>, options?: ActionOptions<Output>) {
  const store = createActionState(action, options)
  return {
    subscribe(run: (state: ActionState<Output>) => void): () => void {
      run(store.getState())
      return store.subscribe(() => run(store.getState()))
    },
    run: store.run,
    reset: store.reset
  }
}
