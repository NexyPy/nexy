import { createLogger, type Logger, type Plugin } from 'vite'
import path from 'node:path'
import { execSync } from 'child_process'
import { createRequire } from 'module'
import { pathToFileURL } from 'url'
import { transform } from 'esbuild'
import { __NEXY_DEPS } from './src/deps.auto.ts'
import {
  DOCUMENT_FRAMEWORKS,
  isLoopback,
  isRootLayout,
  MAX_RENDER_BODY,
  parseRenderRequest,
  readMode,
  renderDocument,
  stripDocumentTags
} from './document'

const c = {
  reset:  '\x1b[0m',
  dim:    '\x1b[2m',
  yellow: '\x1b[33m',
  red:    '\x1b[31m',
  green:  '\x1b[32m',
}

const require = createRequire(import.meta.url)

function getTsxPath(): string {
  try {
    const resolved = require.resolve('tsx/esm')
    return pathToFileURL(resolved).href
  } catch {
    throw new Error(' "tsx" is required. Install it with your package manager: bun add -d tsx')
  }
}

async function compileMdxToJs(source: string, id: string, importSource: string): Promise<string> {
  const { code } = await transform(source, {
    loader: 'jsx',
    jsx: 'automatic',
    jsxImportSource: importSource,
    sourcefile: id
  })
  return code
}

function isInstalled(name: string): boolean {
  try {
    require.resolve(name)
    return true
  } catch {
    return false
  }
}

let nexySSGDone = false
let isSSRBuild = false
let isProduction = false

// MDX is optional: a project that never uses .mdx must not need the MDX
// packages installed, or the Vite config fails to load before it can start.
type MdxFactory = (options: Record<string, unknown>) => Plugin
type MdxModule = { default: MdxFactory }
type GfmModule = { default: unknown }

// Non-literal specifiers keep Vite's config bundler from trying to resolve
// packages the project may not have installed.
const MDX_PACKAGE = '@mdx-js/rollup'
const GFM_PACKAGE = 'remark-gfm'

let mdxDeps: Promise<{ mdx: MdxFactory; remarkGfm: unknown }> | null = null

function loadMdxDeps(): Promise<{ mdx: MdxFactory; remarkGfm: unknown }> {
  if (!mdxDeps) {
    mdxDeps = Promise.all([
      (0, eval)(`import(${JSON.stringify(MDX_PACKAGE)})`) as Promise<MdxModule>,
      (0, eval)(`import(${JSON.stringify(GFM_PACKAGE)})`) as Promise<GfmModule>
    ])
      .then(([mdx, gfm]) => ({ mdx: mdx.default, remarkGfm: gfm.default }))
      .catch(() => {
        throw new Error(
          '[nexy] MDX support requires optional packages that are not installed.\n' +
          'Install them with your package manager:\n' +
          '  bun add -d @mdx-js/rollup remark-gfm @mdx-js/react\n' +
          '  pnpm add -D @mdx-js/rollup remark-gfm @mdx-js/react\n' +
          '  npm install -D @mdx-js/rollup remark-gfm @mdx-js/react'
        )
      })
  }
  return mdxDeps
}

function makeMdxTransform(jsx: boolean, importSource: string) {
  return async function mdxTransform(this: any, source: string, id: string) {
    if (!id.endsWith('.mdx')) return null
    const { mdx, remarkGfm } = await loadMdxDeps()
    const inner = jsx
      ? mdx({ jsx: true, jsxImportSource: importSource, remarkPlugins: [remarkGfm] })
      : mdx({ providerImportSource: importSource, remarkPlugins: [remarkGfm] })
    const out = await (inner.transform as any).call(this, source, id)
    if (!out) return null
    if (!jsx) return out
    return {
      code: await compileMdxToJs(out.code, id, importSource),
      map: (out as any).map ?? null
    }
  }
}

const mdxProdTransform = makeMdxTransform(true, 'react')
const mdxDevTransform = makeMdxTransform(false, '@mdx-js/react')

/**
 * The browser build of a Vue or Svelte root layout holds the body content only: those frameworks cannot
 * create <html>, <head> or <body> in the browser, and the server already sent them.
 */
function documentForBrowser(source: string, id: string, ssr: boolean): string | null {
  if (ssr) return null
  const { csr, framework } = readMode()
  if (!csr || (framework !== 'vue' && framework !== 'svelte')) return null
  if (!isRootLayout(id, framework, process.cwd())) return null
  return stripDocumentTags(source, framework)
}

function nexyPlugin(): Plugin {
  return {
    name: 'nexy',
    enforce: 'pre',

    transform(source, id, options) {
      const stripped = documentForBrowser(source, id, options?.ssr === true)
      if (stripped !== null) return { code: stripped, map: null }
      if (!id.split('?')[0].endsWith('.mdx')) return null
      return (isProduction ? mdxProdTransform : mdxDevTransform).call(this, source, id)
    },

    // --- Automatic Configuration ---
    // Injects Nexy settings directly into Vite
    config({ mode }) {
      isProduction = mode === 'production'
      return {
        logLevel: 'info',
        base: mode === 'production' ? '/__nexy__/client/' : '/',

        resolve: {
          alias: [
            { find: /^@nexy\//, replacement: path.resolve(process.cwd(), '__nexy__/src') + '/' },
            { find: /^@\//, replacement: path.resolve(process.cwd(), 'src') + '/' }
          ]
        },

        clearScreen: false,
        // The host server owns HTML: Vite must never answer a page request, or
        // it would shadow a Nexy route with its own index.html fallback.
        appType: 'custom',
        server: {
          strictPort: true,
          cors: {
            // Loopback origins only: the app always reaches Vite through the
            // Nexy origin, so reflecting arbitrary origins would let any
            // website read project files from 127.0.0.1/@fs/ during dev.
            origin: /^https?:\/\/(?:(?:[^:]+\.)?localhost|127\.0\.0\.1|\[::1\])(?::\d+)?$/,
            methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
          },
          warmup: {
            clientFiles: [
              '__nexy__/main.ts',
              '__nexy__/src/runtime.ts',
              '__nexy__/src/ff.auto.ts',
              'src/**/*.{tsx,jsx,vue,svelte,ts,js}'
            ]
          },
          watch: {
            // Prevent infinite rebuild loops during SSG
            ignored: [
              '**/node_modules/**',
              '**/.venv/**',
              '**/venv/**',
              '**/__pycache__/**',
              '**/__nexy__/client/**',
              '**/__nexy__/**/*.{html,py}',
              '**/.git/**'
            ]
          }
        },

        optimizeDeps: {
          entries: ['__nexy__/main.ts'],
          include: __NEXY_DEPS.filter(isInstalled)
        },

        build: {
          manifest: true,
          outDir: '__nexy__/client',
          rollupOptions: {
            input: {
              main: path.resolve(process.cwd(), '__nexy__/main.ts')
            }
          }
        }
      }
    },

    configResolved(config) {
      isSSRBuild = !!config.build?.ssr
    },

    // --- HMR for non-JS files (Python, Nexy, MDX) ---
    configureServer(server) {
      // Full-document render for client-routed projects: the Python server POSTs a route and gets
      // its HTML back. Only a process on this machine may ask (the app's dev proxy forwards GET
      // and HEAD only, never this), only for route files, and the body is size-limited.
      server.middlewares.use('/__nexy__/render', async (req, res) => {
        const reply = (status: number, text: string, type = 'text/plain') => {
          res.statusCode = status
          res.setHeader('content-type', `${type}; charset=utf-8`)
          res.end(text)
        }
        try {
          if (!isLoopback(req.socket.remoteAddress)) return reply(403, 'forbidden')
          if (req.method !== 'POST') return reply(405, 'use POST')
          const mode = readMode()
          if (!mode.csr || !DOCUMENT_FRAMEWORKS.includes(mode.framework)) {
            return reply(404, 'document rendering is not enabled')
          }
          const chunks: Buffer[] = []
          let size = 0
          for await (const chunk of req) {
            size += (chunk as Buffer).length
            if (size > MAX_RENDER_BODY) return reply(413, 'request too large')
            chunks.push(chunk as Buffer)
          }
          let request
          try {
            request = parseRenderRequest(Buffer.concat(chunks).toString('utf8'))
          } catch (error) {
            return reply(400, (error as Error).message)
          }
          const html = await renderDocument(
            server,
            request.page,
            request.layouts,
            request.props,
            request.location
          )
          reply(200, html, 'text/html')
        } catch (error) {
          const err = error as Error
          if (err.stack) server.ssrFixStacktrace(err)
          reply(500, String(err.stack ?? err))
        }
      })

      server.watcher.add([
        path.resolve(process.cwd(), 'src/**/*.py'),
        path.resolve(process.cwd(), 'src/**/*.nexy'),
        path.resolve(process.cwd(), 'src/**/*.mdx'),
        path.resolve(process.cwd(), '*.py')
      ])

      // Vite owns HMR for framework files (.tsx/.vue/.svelte/.jsx) natively.
      // MDX is routed through Vite here; .nexy/.md are served via the Nexy
      // body-swap WebSocket, and .py changes restart the uvicorn process.
      const reloadExts = (file: string) => file.endsWith('.mdx')

      server.watcher.on('change', (file) => {
        if (reloadExts(file)) {
          server.ws.send({ type: 'full-reload', path: '*' })
        }
      })

      server.watcher.on('add', (file) => {
        if (reloadExts(file)) {
          server.ws.send({ type: 'full-reload', path: '*' })
        }
      })
    },

    // Python files restart the server and .nexy/.md pages refresh over the Nexy socket: Vite must
    // not also reload the browser, which would hit the server while it is still restarting.
    handleHotUpdate({ file }) {
      if (/\.(py|nexy|md)$/.test(file)) return []
    },

    // --- Entry Generation (Client side) ---
    buildStart() {
      if (isSSRBuild || process.env.NEXY_RENDER_ONLY) return
      nexySSGDone = false
      const isDev = process.env.NODE_ENV === 'development'
      // Server components are the islands a server-rendered page embeds. A client-routed project
      // has none: its documents are rendered once, after the bundle (see document.ts).
      const { csr, framework } = readMode()
      const hasIslands = !(csr && DOCUMENT_FRAMEWORKS.includes(framework))
      if (!isDev && hasIslands) {
        console.log(`${c.dim}[nexy] Building server components...${c.reset}`)
        const tsxPath = getTsxPath()
        execSync(`node --import "${tsxPath}" __nexy__/scripts/entries.ts`, {
          stdio: 'inherit',
          cwd: process.cwd()
        })
        console.log(`${c.green}[nexy] Server components built${c.reset}`)
      }
    },

    // --- Static Site Generation (SSG) ---
    closeBundle() {
      if (isSSRBuild || nexySSGDone || process.env.NEXY_RENDER_ONLY) return
      nexySSGDone = true

      console.log(`${c.dim}[nexy] Building client bundles...${c.reset}`)
      const tsxPath = getTsxPath()
      execSync(`node --import "${tsxPath}" __nexy__/scripts/ssg.ts`, {
        stdio: 'inherit',
        cwd: process.cwd()
      })
      console.log(`${c.green}[nexy] Client bundles built${c.reset}`)
    }
  }
}

const nexyLogger = (): Logger => {
  const logger = createLogger()
  const prefix = `${c.reset}${c.dim}vite »${c.reset}`
  return {
    ...logger,
    info: (msg) => {
      const silentMessages = ['Local', 'Network', 'ready in', 'press', 'watching']
      if (silentMessages.some(m => msg.includes(m))) return
      console.info(`${prefix} ${msg.replace("/", "")}`)
    },
    warn: (msg) => console.warn(`${prefix} ${c.yellow}${msg}${c.reset}`),
    error: (msg) => console.error(`${prefix} ${c.red}${msg}${c.reset}`),
  }
}

const nexy = Object.assign(nexyPlugin, {
  log: nexyLogger
})

export default nexy

