import { createLogger, type Logger, type Plugin } from 'vite'
import mdx from '@mdx-js/rollup'
import remarkGfm from 'remark-gfm'
import path from 'node:path'
import { execSync } from 'child_process'
import { createRequire } from 'module'
import { pathToFileURL } from 'url'
import { transform } from 'esbuild'
import { __NEXY_DEPS } from './src/deps.auto.ts'

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
    throw new Error(' "tsx" is required. Run: pnpm add -D tsx')
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

function makeMdxTransform(jsx: boolean, importSource: string) {
  const inner = jsx
    ? mdx({ jsx: true, jsxImportSource: importSource, remarkPlugins: [remarkGfm] })
    : mdx({ providerImportSource: importSource, remarkPlugins: [remarkGfm] })
  return async function mdxTransform(this: any, source: string, id: string) {
    if (!id.endsWith('.mdx')) return null
    const out = await inner.transform.call(this, source, id)
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

function nexyPlugin(): Plugin {
  return {
    name: 'nexy',

    transform(source, id) {
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
            origin: true,
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

    // --- Entry Generation (Client side) ---
    buildStart() {
      if (isSSRBuild) return
      nexySSGDone = false
      const isDev = process.env.NODE_ENV === 'development'
      if (!isDev) {
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
      if (isSSRBuild || nexySSGDone) return
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
  const prefix = `${c.reset}${c.yellow}${c.dim}VITE${c.reset} »`
  return {
    ...logger,
    info: (msg) => {
      const silentMessages = ['Local', 'Network', 'ready in', 'press', 'watching']
      if (silentMessages.some(m => msg.includes(m))) return
      console.info(`${prefix} ${msg.replace("/", "")}`)
    },
    warn: (msg) => console.warn(`${prefix} ${c.yellow}WARN ${msg}${c.reset}`),
    error: (msg) => console.error(`${prefix} ${c.red}ERR ${msg}${c.reset}`),
  }
}

const nexy = Object.assign(nexyPlugin, {
  log: nexyLogger
})

export default nexy

