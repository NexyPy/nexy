import * as esbuild from 'esbuild'
import * as fs from 'fs'
import * as http from 'http'
import * as path from 'path'

const ROOT = process.cwd()
const OUT_DIR = path.resolve(ROOT, '__nexy__/client')
const MAIN_ENTRY = path.resolve(ROOT, '__nexy__/main.ts')
const RUNTIME_TS = path.resolve(ROOT, '__nexy__/src/runtime.ts')

const port = parseInt(process.argv[2] || String(5173), 10)

interface SSEClient {
  id: number
  res: http.ServerResponse
}
const clients: SSEClient[] = []
let nextId = 1

function notifyReload(): void {
  const msg = 'event: reload\ndata: {}\n\n'
  for (const client of clients) {
    try {
      client.res.write(msg)
    } catch {
      // client gone
    }
  }
}

const MIME: Record<string, string> = {
  '.js': 'application/javascript',
  '.css': 'text/css',
  '.html': 'text/html',
  '.json': 'application/json',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.ts': 'application/x-typescript',
  '.tsx': 'application/x-typescript',
}

function getContentType(filePath: string): string {
  const ext = path.extname(filePath).toLowerCase()
  return MIME[ext] || 'application/octet-stream'
}

function serveFile(res: http.ServerResponse, fullPath: string, contentType?: string): void {
  fs.readFile(fullPath, (err, data) => {
    if (err) {
      res.writeHead(404)
      res.end('Not found')
      return
    }
    res.writeHead(200, { 'Content-Type': contentType || getContentType(fullPath) })
    res.end(data)
  })
}

async function main(): Promise<void> {
  // Ensure client output directory exists for Uvicorn static serving
  fs.mkdirSync(OUT_DIR, { recursive: true })

  // Ensure __nexy__/src directory for runtime files
  fs.mkdirSync(path.resolve(ROOT, '__nexy__/src'), { recursive: true })

  // Write port file (for inter-process communication)
  fs.writeFileSync(path.resolve(ROOT, '__nexy__/client.port'), String(port), 'utf-8')

  // Patch runtime.ts to remove import.meta.glob (esbuild does not support it)
  let runtimeBackup: string | null = null
  if (fs.existsSync(RUNTIME_TS)) {
    runtimeBackup = fs.readFileSync(RUNTIME_TS, 'utf-8')
    const patched = runtimeBackup.replace(
      /import\.meta\.glob\(['"][^'"]+['"],\s*\{[^}]+\}\) as Record<string, Importer>/,
      '({} as Record<string, Importer>)',
    )
    if (patched !== runtimeBackup) {
      fs.writeFileSync(RUNTIME_TS, patched, 'utf-8')
    }
  }

  // Restore runtime.ts on exit
  function restoreRuntime(): void {
    if (runtimeBackup && fs.existsSync(RUNTIME_TS)) {
      const current = fs.readFileSync(RUNTIME_TS, 'utf-8')
      const restored = current.replace(
        '({} as Record<string, Importer>)',
        "import.meta.glob('/src/**/*.{tsx,jsx,ts,js,vue,svelte}', { eager: false }) as Record<string, Importer>",
      )
      if (restored !== current) {
        fs.writeFileSync(RUNTIME_TS, restored, 'utf-8')
      }
    }
  }

  const ctx = await esbuild.context({
    entryPoints: [MAIN_ENTRY],
    outdir: OUT_DIR,
    bundle: true,
    format: 'esm',
    splitting: true,
    sourcemap: 'inline',
    logLevel: 'warning',
    entryNames: '[name]',
    conditions: ['style'],
    loader: {
      '.ttf': 'file',
      '.otf': 'file',
      '.woff': 'file',
      '.woff2': 'file',
      '.eot': 'file',
      '.vue': 'empty',
      '.svelte': 'empty',
    },
    plugins: [
      {
        name: 'nexy-aliases',
        setup(build) {
          // Stub Vite-specific dynamic imports (e.g. React Fast Refresh)
          // MUST be before the catch-all /^\// handler
          build.onResolve({ filter: /^\/@react-refresh$/ }, () => {
            return { path: '/@react-refresh', namespace: 'nexy-stub' }
          })
          build.onLoad({ filter: /.*/, namespace: 'nexy-stub' }, () => {
            return { contents: 'export default { injectIntoGlobalHook() {} }', loader: 'js' }
          })
          build.onResolve({ filter: /^@nexy\// }, (args) => {
            const rest = args.path.slice('/@nexy'.length)
            return { path: path.resolve(ROOT, '__nexy__/src', rest) }
          })
          build.onResolve({ filter: /^@\// }, (args) => {
            const rest = args.path.slice('/@'.length)
            return { path: path.resolve(ROOT, 'src', rest) }
          })
          build.onResolve({ filter: /^\// }, (args) => {
            return { path: path.resolve(ROOT, '.' + args.path) }
          })
        },
      },
      {
        name: 'nexy-watch',
        setup(build) {
          build.onEnd((result) => {
            if (result.errors.length === 0) {
              notifyReload()
            }
          })
        },
      },
    ],
  })

  await ctx.watch()

  // Wait for main.js to exist on disk before signaling readiness
  const mainJs = path.resolve(OUT_DIR, 'main.js')
  while (!fs.existsSync(mainJs)) {
    await new Promise(r => setTimeout(r, 50))
  }

  // HTTP server: serve source files + bundled output + SSE endpoint
  const server = http.createServer((req, res) => {
    // CORS for all origins (dev mode — resources loaded from esbuild port by Uvicorn-served HTML)
    res.setHeader('Access-Control-Allow-Origin', '*')
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS')
    if (req.method === 'OPTIONS') { res.writeHead(204); res.end(); return }

    const url = new URL(req.url || '/', `http://localhost:${port}`)

    // SSE endpoint for live reload
    if (url.pathname === '/__nexy__/__reload') {
      res.writeHead(200, {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      })
      const id = nextId++
      clients.push({ id, res })
      req.on('close', () => {
        const idx = clients.findIndex((c) => c.id === id)
        if (idx !== -1) clients.splice(idx, 1)
      })
      return
    }

    // Map /@nexy/ => __nexy__/src/
    let filePath = url.pathname
    if (filePath.startsWith('/@nexy/')) {
      filePath = '/__nexy__/src' + filePath.slice('/@nexy'.length)
    } else if (filePath.startsWith('/@/')) {
      // Map @/ to src/
      filePath = '/src' + filePath.slice('/@'.length)
    }

    const fullPath = path.resolve(ROOT, filePath.slice(1))

    // Try exact path, then client dir as fallback
    fs.access(fullPath, fs.constants.F_OK, (accessErr) => {
      if (accessErr) {
        // Fallback: serve from client output dir
        const clientPath = path.resolve(OUT_DIR, filePath.slice(1))
        serveFile(res, clientPath)
        return
      }
      serveFile(res, fullPath)
    })
  })

  server.listen(port, () => {
    // Write port again after listening (confirms server is ready)
    fs.writeFileSync(path.resolve(ROOT, '__nexy__/client.port'), String(port), 'utf-8')
    console.log(String(port))
  })

  // Watch .py, .nexy, .mdx files for full reload
  const watchDirs: string[] = [
    path.resolve(ROOT, 'src'),
    path.resolve(ROOT, 'pages'),
  ]
  for (const dir of watchDirs) {
    if (fs.existsSync(dir)) {
      fs.watch(dir, { recursive: true }, (_event, filename) => {
        if (!filename) return
        if (/\.(py|nexy|mdx)$/i.test(filename)) {
          notifyReload()
        }
      })
    }
  }

  // Watch project root for .nexy files
  fs.watch(ROOT, { recursive: false }, (_event, filename) => {
    if (!filename) return
    if (/\.nexy$/i.test(filename)) {
      notifyReload()
    }
  })

  // Graceful shutdown
  const shutdown = async (): Promise<void> => {
    restoreRuntime()
    await ctx.dispose()
    server.close()
    process.exit(0)
  }
  process.on('SIGINT', shutdown)
  process.on('SIGTERM', shutdown)
}

main().catch((err) => {
  console.error('[nexy] Dev server error:', err)
  process.exit(1)
})
