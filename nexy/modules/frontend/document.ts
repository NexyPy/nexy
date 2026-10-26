// Server-side render of a whole document for client-routed (useCSR) projects.
//
// The root layout owns <html>, <head> and <body>, like Next.js: Nexy renders
// <RootLayout><NestedLayout><Page /></NestedLayout></RootLayout> here, in Node, so the first response
// already carries the real document. React and Solid then hydrate the same tree; Preact, Vue and
// Svelte build the body in the browser and swap it in.
import crypto from 'node:crypto'
import fs from 'node:fs'
import path from 'node:path'
import { pathToFileURL } from 'node:url'
import type { ViteDevServer } from 'vite'

type Mode = { csr: boolean; framework: string }

export function readMode(): Mode {
  try {
    return JSON.parse(fs.readFileSync(path.resolve(process.cwd(), '__nexy__/mode.auto.json'), 'utf8'))
  } catch {
    return { csr: false, framework: '' }
  }
}

// Only route files may be rendered: this runs behind a dev-only endpoint.
const ROUTE_FILE = /^\/src\/routes\/[A-Za-z0-9_\-./[\]()@]+\.(tsx|jsx|vue|svelte)$/

export function assertRouteFile(file: string): void {
  if (!ROUTE_FILE.test(file) || file.includes('..')) {
    throw new Error(`Not a route file: ${file}`)
  }
}

/** Largest body the render endpoint reads: props are data for a page, not an upload. */
export const MAX_RENDER_BODY = 1_000_000

/** True for the addresses a process on this machine connects from. */
export function isLoopback(address: string | undefined | null): boolean {
  return address === '127.0.0.1' || address === '::1' || address === '::ffff:127.0.0.1'
}

/** True when `id` (a Vite module id) is the root `src/routes/layout.<framework>` of the project at `cwd`. */
export function isRootLayout(id: string, framework: string, cwd: string): boolean {
  const normalise = (value: string) => value.split('?')[0].replace(/\\/g, '/')
  const expected = `${normalise(path.resolve(cwd, 'src/routes'))}/layout.${framework}`
  const actual = normalise(id)
  // Windows paths are case-insensitive: Vite may report `d:/app` while the process runs in `D:/app`.
  return process.platform === 'win32' ? actual.toLowerCase() === expected.toLowerCase() : actual === expected
}

/** The URL a page is rendered for: what `usePathname()` and friends answer during the render. */
export type RenderLocation = { pathname: string; search: string }

export type RenderRequest = {
  page: string | null
  layouts: string[]
  props: Record<string, unknown>
  location?: RenderLocation
}

const LOCATION_KEY = '__NEXY_LOCATION__'
let renderQueue: Promise<unknown> = Promise.resolve()

/**
 * Run `render` with the request location published for the hooks of the page.
 *
 * The location is a global, so renders go one at a time: two overlapping requests must never see
 * each other's URL. Rendering is CPU work in one thread anyway, so nothing is lost.
 */
export function withLocation<T>(
  location: RenderLocation,
  params: Record<string, unknown>,
  render: () => Promise<T>
): Promise<T> {
  const strings = Object.fromEntries(
    Object.entries(params).filter(([, value]) => typeof value === 'string')
  )
  const run = async () => {
    const g = globalThis as Record<string, unknown>
    g[LOCATION_KEY] = { ...location, hash: '', params: strings }
    try {
      return await render()
    } finally {
      delete g[LOCATION_KEY]
    }
  }
  const result = renderQueue.then(run, run)
  renderQueue = result.catch(() => undefined)
  return result
}

function parseLocation(value: unknown): RenderLocation | undefined {
  if (value === undefined) return undefined
  const location = value as Record<string, unknown> | null
  if (
    location === null ||
    typeof location !== 'object' ||
    typeof location.pathname !== 'string' ||
    typeof location.search !== 'string'
  ) {
    throw new Error('"location" must be { pathname: string, search: string }')
  }
  return { pathname: location.pathname, search: location.search }
}

/** Parse and validate the JSON body of a render request. Throws on anything unexpected. */
export function parseRenderRequest(text: string): RenderRequest {
  const body = JSON.parse(text) as Record<string, unknown> | null
  if (body === null || typeof body !== 'object' || Array.isArray(body)) {
    throw new Error('The render request must be a JSON object')
  }
  const { page, layouts, props } = body
  const location = parseLocation(body.location)
  if (page !== null && typeof page !== 'string') throw new Error('"page" must be a route file or null')
  if (!Array.isArray(layouts) || layouts.some(layout => typeof layout !== 'string')) {
    throw new Error('"layouts" must be a list of route files')
  }
  if (props === null || typeof props !== 'object' || Array.isArray(props)) {
    throw new Error('"props" must be an object')
  }
  if (page) assertRouteFile(page)
  layouts.forEach(assertRouteFile)
  return (location ? { page, layouts, props, location } : { page, layouts, props }) as RenderRequest
}

type Component = (props: Record<string, unknown>) => unknown

async function load(server: ViteDevServer, file: string): Promise<Component> {
  assertRouteFile(file)
  const mod = await server.ssrLoadModule(file)
  const component = (mod as { default?: Component }).default
  // Vue single-file components export an object; every other framework exports a function.
  if (typeof component !== 'function' && (typeof component !== 'object' || component === null)) {
    throw new Error(`${file} must export a default component`)
  }
  return component
}

/** Render `<layouts><page/></layouts>` as a full HTML document. A null page renders the shell. */
export async function renderDocument(
  server: ViteDevServer,
  page: string | null,
  layouts: string[],
  props: Record<string, unknown>,
  location: RenderLocation = { pathname: '/', search: '' }
): Promise<string> {
  return withLocation(location, props, () => renderWithin(server, page, layouts, props))
}

async function renderWithin(
  server: ViteDevServer,
  page: string | null,
  layouts: string[],
  props: Record<string, unknown>
): Promise<string> {
  const framework = readMode().framework
  if (framework === 'svelte') return '<!DOCTYPE html>' + (await renderSvelte(server, page, layouts, props))

  const { createElement, renderToString } = await engine(framework)
  const chain = await Promise.all(layouts.map(file => load(server, file)))
  let node: unknown = page ? createElement(await load(server, page), props) : null
  for (let i = chain.length - 1; i >= 0; i--) {
    node = createElement(chain[i] as never, { params: props }, node as never)
  }
  return '<!DOCTYPE html>' + (await renderToString(node as never))
}

/**
 * Svelte composes layouts through `children` snippets, which have no public API outside a template.
 * A small generated component states the composition in Svelte's own syntax instead.
 */
async function renderSvelte(
  server: ViteDevServer,
  page: string | null,
  layouts: string[],
  props: Record<string, unknown>
): Promise<string> {
  const files = page ? [...layouts, page] : layouts
  files.forEach(assertRouteFile)
  const names = layouts.map((_, i) => `L${i}`)
  let markup = page ? '<Page {...props} />' : ''
  for (let i = layouts.length - 1; i >= 0; i--) markup = `<${names[i]} params={props}>${markup}</${names[i]}>`
  const imports = [...layouts.map((file, i) => `import L${i} from ${JSON.stringify(file)}`)]
  if (page) imports.push(`import Page from ${JSON.stringify(page)}`)
  const source = `<script>\n${imports.join('\n')}\nlet { props } = $props()\n</script>\n${markup}\n`

  const name = crypto.createHash('sha1').update(source).digest('hex').slice(0, 16)
  const file = `/__nexy__/documents/${name}.svelte`
  const absolute = path.resolve(process.cwd(), '.' + file)
  fs.mkdirSync(path.dirname(absolute), { recursive: true })
  if (!fs.existsSync(absolute)) fs.writeFileSync(absolute, source)

  // Loaded through Vite, like the components: both must share one copy of Svelte's server runtime.
  const { render } = (await server.ssrLoadModule('svelte/server')) as typeof import('svelte/server')
  const module = (await server.ssrLoadModule(file)) as { default: never }
  // Svelte brackets its output with hydration markers; the browser never hydrates it.
  return render(module.default, { props: { props } }).body.replace(/^<!--\[-->/, '').replace(/<!--\]-->$/, '')
}

type Engine = {
  createElement: (type: never, props: Record<string, unknown> | null, ...children: never[]) => unknown
  renderToString: (node: never) => string | Promise<string>
}

/** Frameworks whose root layout can own the document, with the pair that renders them in Node. */
export const DOCUMENT_FRAMEWORKS = ['react', 'solid', 'preact', 'vue', 'svelte']

async function engine(framework: string): Promise<Engine> {
  if (framework === 'solid') {
    // Solid renders a thunk; components are created lazily so they run inside the render root.
    const { createComponent, renderToString } = await import('solid-js/web')
    type Thunk = () => unknown
    const createElement = (type: never, props: Record<string, unknown> | null, child?: unknown) => {
      return () =>
        createComponent(type, {
          ...props,
          get children() {
            return typeof child === 'function' ? (child as Thunk)() : child
          }
        })
    }
    return { createElement: createElement as never, renderToString: renderToString as never }
  }
  if (framework === 'preact') {
    const { h } = await import('preact')
    const { renderToString } = await import('preact-render-to-string')
    return { createElement: h as never, renderToString: renderToString as never }
  }
  if (framework === 'vue') {
    // Like Solid, Vue renders from a function so components run inside the render. A layout receives
    // the route params as its attributes, exactly as the browser passes them.
    const { h, createSSRApp } = await import('vue')
    const { renderToString } = await import('vue/server-renderer')
    type Thunk = () => unknown
    const createElement = (type: never, props: Record<string, unknown> | null, child?: unknown) => {
      const attrs = props && 'params' in props ? (props.params as Record<string, unknown>) : props
      return () =>
        h(type, attrs, {
          default: () => (typeof child === 'function' ? (child as Thunk)() : child)
        })
    }
    return {
      createElement: createElement as never,
      renderToString: (node: never) => renderToString(createSSRApp({ render: node as never }))
    }
  }
  if (framework !== 'react') throw new Error(`The root layout cannot own the document with ${framework}`)
  const { createElement } = await import('react')
  const { renderToString } = await import('react-dom/server')
  return { createElement: createElement as never, renderToString: renderToString as never }
}

type ClientRoute = { path: string; file: string; layouts?: string[] }

/** Pre-render every client route to `__nexy__/client/static/**` for production. */
export async function writeDocuments(): Promise<number> {
  const mode = readMode()
  if (!mode.csr || !DOCUMENT_FRAMEWORKS.includes(mode.framework)) return 0

  const routesFile = path.resolve(process.cwd(), '__nexy__/src/routes.client.auto.ts')
  const { NEXY_ROUTES } = (await import(pathToFileURL(routesFile).href)) as { NEXY_ROUTES: ClientRoute[] }
  const routes = NEXY_ROUTES.filter(route => /\.(tsx|jsx|vue|svelte)$/.test(route.file))

  process.env.NEXY_RENDER_ONLY = '1'
  const { createServer } = await import('vite')
  const server = await createServer({
    configFile: path.resolve(process.cwd(), 'vite.config.ts'),
    server: { middlewareMode: true, hmr: false, watch: null, ws: false },
    appType: 'custom',
    logLevel: 'error',
    // Rendering only: no dependency pre-bundling, which would still be running at exit.
    optimizeDeps: { noDiscovery: true, include: [] }
  })

  let written = 0
  try {
    for (const route of routes) {
      const dynamic = route.path.includes('{')
      const html = await renderDocument(
        server,
        dynamic ? null : route.file,
        route.layouts ?? [],
        {},
        { pathname: route.path, search: '' }
      )
      const out = path.resolve(
        process.cwd(),
        '__nexy__/client/static' + route.file.replace(/\.(tsx|jsx|vue|svelte)$/, dynamic ? '.shell.html' : '.document.html')
      )
      fs.mkdirSync(path.dirname(out), { recursive: true })
      fs.writeFileSync(out, html)
      written++
    }
  } finally {
    await server.close()
  }
  return written
}

// --- Client build of Vue and Svelte root layouts ---------------------------------------------------
//
// Neither framework can create <html>, <head> or <body> in the browser (they build markup with a
// template element, whose parser drops those tags). The server renders the complete document; the
// browser only builds what lives inside <body>. This strips the three tags from the client build of
// the root layout so it compiles to that body content.

type Kind = 'vue' | 'svelte'

/** Index just after the `>` that closes the tag opened at `start`, skipping quotes and braces. */
function tagEnd(source: string, start: number): number {
  let quote = ''
  let depth = 0
  for (let i = start; i < source.length; i++) {
    const ch = source[i]
    if (quote) {
      if (ch === quote) quote = ''
    } else if (ch === '"' || ch === "'") {
      quote = ch
    } else if (ch === '{') {
      depth++
    } else if (ch === '}') {
      depth = Math.max(0, depth - 1)
    } else if (ch === '>' && depth === 0) {
      return i + 1
    }
  }
  return source.length
}

function removeTags(source: string, name: string, withContent: boolean): string {
  const open = new RegExp(`<${name}(?=[\\s>/])`, 'g')
  const close = `</${name}>`
  let out = ''
  let last = 0
  for (let match = open.exec(source); match; match = open.exec(source)) {
    let end = tagEnd(source, match.index)
    if (withContent) {
      const closing = source.indexOf(close, end)
      if (closing !== -1) end = closing + close.length
    }
    out += source.slice(last, match.index)
    last = end
    open.lastIndex = end
  }
  out += source.slice(last)
  return withContent ? out : out.split(close).join('')
}

function stripMarkup(markup: string): string {
  return removeTags(removeTags(markup, 'html', false), 'body', false)
}

/** Source of a root layout for the browser: <html>, <head> and <body> removed. */
export function stripDocumentTags(source: string, kind: Kind): string {
  if (kind === 'svelte') {
    // The component script and style blocks stay; only the markup around them is rewritten.
    const parts = removeTags(source, 'head', true).split(/(<script[\s\S]*?<\/script>|<style[\s\S]*?<\/style>)/g)
    return parts.map(part => (/^<(script|style)[\s>]/.test(part) ? part : stripMarkup(part))).join('')
  }
  const start = source.indexOf('<template')
  const end = source.lastIndexOf('</template>')
  if (start === -1 || end === -1) return source
  const innerStart = tagEnd(source, start)
  const markup = removeTags(source.slice(innerStart, end), 'head', true)
  return source.slice(0, innerStart) + stripMarkup(markup) + source.slice(end)
}
