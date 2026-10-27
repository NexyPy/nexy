// Calling the @Action functions of the Python server from the browser.
//
//   import { createUser } from '@nexy/actions'
//   const user = await createUser({ name: 'Ada' })
//
// `@nexy/actions` is generated from the Python signatures, so inputs and results are typed.
// The framework adapters add `useAction`, which tracks pending, data and error for a component.
import { getRouter } from './router.ts'

/** What the server answered when an action failed. */
export class ActionError extends Error {
  readonly status: number
  readonly detail: unknown

  constructor(status: number, detail: unknown) {
    super(typeof detail === 'string' ? detail : `Action failed with status ${status}`)
    this.name = 'ActionError'
    this.status = status
    this.detail = detail
  }

  /** The message of each invalid field, by name, for a 422 answer. */
  get fields(): Record<string, string> {
    const fields: Record<string, string> = {}
    if (!Array.isArray(this.detail)) return fields
    for (const item of this.detail as { loc?: unknown[]; msg?: string }[]) {
      const name = String(item.loc?.[item.loc.length - 1] ?? '')
      if (name && item.msg) fields[name] = item.msg
    }
    return fields
  }
}

export type Action<Input, Output> = ((input: Input) => Promise<Output>) & {
  /** Where the action lives: use it as the `action` of a `<form method="post">` that works without JavaScript. */
  readonly url: string
  readonly id: string
}

const REVALIDATE = 'x-nexy-revalidate'

async function refreshPage(header: string | null): Promise<void> {
  if (!header) return
  const paths = header.split(',')
  if (!paths.includes('*') && !paths.includes(location.pathname)) return
  const router = getRouter()
  if (router) await router.refresh()
  else location.reload()
}

async function detailOf(response: Response): Promise<unknown> {
  const text = await response.text()
  try {
    return (JSON.parse(text) as { detail?: unknown }).detail ?? text
  } catch {
    return text || response.statusText
  }
}

export function defineAction<Input = void, Output = unknown>(url: string, id: string): Action<Input, Output> {
  async function call(input?: Input): Promise<Output> {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'content-type': 'application/json', accept: 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify(input ?? {})
    })
    if (!response.ok) throw new ActionError(response.status, await detailOf(response))
    const body = response.headers.get('content-type')?.includes('json') ? await response.json() : undefined
    await refreshPage(response.headers.get(REVALIDATE))
    return body as Output
  }
  return Object.assign(call, { url, id }) as Action<Input, Output>
}

export type ActionState<Output> = {
  pending: boolean
  data: Output | undefined
  error: ActionError | Error | undefined
}

export type ActionOptions<Output> = {
  onSuccess?: (data: Output) => void
  onError?: (error: ActionError | Error) => void
}

/** The state of one action, outside any framework: the adapters wrap it for theirs. */
export function createActionState<Input, Output>(
  action: Action<Input, Output>,
  options: ActionOptions<Output> = {}
) {
  let state: ActionState<Output> = { pending: false, data: undefined, error: undefined }
  let latest = 0
  const listeners = new Set<() => void>()

  function set(next: ActionState<Output>): void {
    state = next
    listeners.forEach(listener => listener())
  }

  async function run(input: Input): Promise<Output | undefined> {
    const mine = ++latest
    set({ pending: true, data: state.data, error: undefined })
    try {
      const data = await action(input)
      if (mine === latest) set({ pending: false, data, error: undefined })
      options.onSuccess?.(data)
      return data
    } catch (caught) {
      const error = caught instanceof Error ? caught : new Error(String(caught))
      if (mine === latest) set({ pending: false, data: state.data, error })
      options.onError?.(error)
      return undefined
    }
  }

  return {
    getState: (): ActionState<Output> => state,
    subscribe(listener: () => void): () => void {
      listeners.add(listener)
      return () => void listeners.delete(listener)
    },
    run,
    reset(): void {
      latest++
      set({ pending: false, data: undefined, error: undefined })
    }
  }
}

export type ActionStore<Input, Output> = ReturnType<typeof createActionState<Input, Output>>
