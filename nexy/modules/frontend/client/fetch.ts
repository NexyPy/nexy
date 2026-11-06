// Reading JSON from the Python server in a component.
//
//   const { data, error, pending, refresh } = useFetch<User[]>('/api/users')
//
// One state per URL, shared by every component that reads it: the first one sends the request, the
// others reuse the answer. A refresh keeps the data until the new answer arrives, and two refreshes
// at once send one request. The framework adapters wrap it as `useFetch`.

/** What the server answered when a request failed. */
export class FetchError extends Error {
  readonly status: number
  readonly detail: unknown

  constructor(status: number, detail: unknown) {
    super(typeof detail === 'string' ? detail : `Request failed with status ${status}`)
    this.name = 'FetchError'
    this.status = status
    this.detail = detail
  }
}

export type FetchState<Data> = {
  data: Data | undefined
  error: FetchError | Error | undefined
  pending: boolean
}

type Entry = {
  state: FetchState<unknown>
  listeners: Set<() => void>
  running: Promise<void> | undefined
}

const entries = new Map<string, Entry>()

function entryOf(url: string): Entry {
  let entry = entries.get(url)
  if (!entry) {
    entry = { state: { data: undefined, error: undefined, pending: true }, listeners: new Set(), running: undefined }
    entries.set(url, entry)
  }
  return entry
}

function set(entry: Entry, state: FetchState<unknown>): void {
  entry.state = state
  entry.listeners.forEach(listener => listener())
}

async function detailOf(response: Response): Promise<unknown> {
  const text = await response.text()
  try {
    return (JSON.parse(text) as { detail?: unknown }).detail ?? text
  } catch {
    return text || response.statusText
  }
}

async function request(url: string): Promise<unknown> {
  const response = await fetch(url, { headers: { accept: 'application/json' }, credentials: 'same-origin' })
  if (!response.ok) throw new FetchError(response.status, await detailOf(response))
  return response.status === 204 ? undefined : response.json()
}

async function load(url: string, entry: Entry): Promise<void> {
  set(entry, { ...entry.state, pending: true })
  try {
    set(entry, { data: await request(url), error: undefined, pending: false })
  } catch (caught) {
    const error = caught instanceof Error ? caught : new Error(String(caught))
    set(entry, { data: entry.state.data, error, pending: false })
  }
}

/** Fetch *url* again; a refresh already running is the one returned. */
export function refresh(url: string): Promise<void> {
  const entry = entryOf(url)
  entry.running ??= load(url, entry).finally(() => (entry.running = undefined))
  return entry.running
}

/** Fetch again every URL read on this page: what an action calls after `revalidate()`. */
export function refreshAll(): Promise<void> {
  return Promise.all([...entries.keys()].map(refresh)).then(() => undefined)
}

// An action that calls `revalidate()` announces it with this event: the data on the page reloads.
if (typeof window !== 'undefined') window.addEventListener('nexy:revalidate', () => void refreshAll())

/** The state of one URL, outside any framework: the adapters wrap it for theirs. */
export function createFetchState<Data>(url: string) {
  const entry = entryOf(url)
  const loaded = () => entry.state.data !== undefined || entry.state.error !== undefined
  return {
    getState: (): FetchState<Data> => entry.state as FetchState<Data>,
    subscribe(listener: () => void): () => void {
      entry.listeners.add(listener)
      return () => void entry.listeners.delete(listener)
    },
    /** Send the first request, unless another component already did. */
    start: (): Promise<void> => (loaded() ? Promise.resolve() : refresh(url)),
    refresh: (): Promise<void> => refresh(url)
  }
}

export type FetchStore<Data> = ReturnType<typeof createFetchState<Data>>
