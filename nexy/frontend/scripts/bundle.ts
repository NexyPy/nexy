import esbuild from 'esbuild'
import fs from 'fs'
import path from 'path'

const ROOT = process.cwd()
const OUT_DIR = path.resolve(ROOT, '__nexy__/client')
const MANIFEST_DIR = path.resolve(OUT_DIR, '.vite')
const RUNTIME_TS = path.resolve(ROOT, '__nexy__/src/runtime.ts')

const ALIAS_PLUGIN: esbuild.Plugin = {
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
      return { path: path.resolve(ROOT, '__nexy__/src', args.path.slice('/@nexy'.length)) }
    })
    build.onResolve({ filter: /^@\// }, (args) => {
      return { path: path.resolve(ROOT, 'src', args.path.slice('/@'.length)) }
    })
    build.onResolve({ filter: /^\// }, (args) => {
      return { path: path.resolve(ROOT, '.' + args.path) }
    })
  },
}

function generateManifest(metafile: esbuild.Metafile): void {
  const manifest: Record<string, { file: string; css: string[]; src: string; isEntry: boolean }> = {}

  for (const [outPath, meta] of Object.entries(metafile.outputs)) {
    if (!meta.entryPoint) continue
    const relPath = path.relative(OUT_DIR, outPath).replace(/\\/g, '/')
    const entryKey = path.relative(ROOT, meta.entryPoint).replace(/\\/g, '/')

    manifest[entryKey] = {
      file: relPath,
      css: [],
      src: entryKey,
      isEntry: true,
    }
  }

  fs.mkdirSync(MANIFEST_DIR, { recursive: true })
  fs.writeFileSync(
    path.join(MANIFEST_DIR, 'manifest.json'),
    JSON.stringify(manifest, null, 2)
  )
}

const FONT_EXTS = /\.(ttf|otf|woff|woff2|eot)$/
const COMPONENT_EXTS = /\.(tsx|jsx|ts|js)$/i

function scanComponentFiles(): string[] {
  const results: string[] = []
  const srcDir = path.resolve(ROOT, 'src')
  if (!fs.existsSync(srcDir)) return results
  function walk(dir: string) {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name)
      if (entry.isDirectory()) {
        if (!entry.name.startsWith('_')) walk(full)
      } else if (entry.isFile() && COMPONENT_EXTS.test(entry.name)) {
        results.push(full)
      }
    }
  }
  walk(srcDir)
  return results
}

function buildStaticImporters(files: string[]): string {
  const entries = files.map(f => {
    const rel = '/' + path.relative(ROOT, f).replace(/\\/g, '/')
    return `  "${rel}": () => import("${rel}")`
  })
  return `{\n${entries.join(',\n')}\n} as Record<string, Importer>`
}

async function bundle(): Promise<void> {
  if (fs.existsSync(RUNTIME_TS)) {
    const componentFiles = scanComponentFiles()
    const importersReplace = buildStaticImporters(componentFiles)
    const original = fs.readFileSync(RUNTIME_TS, 'utf-8')
    const prod = original.replace(
      /import\.meta\.glob\(['"][^'"]+['"],\s*\{[^}]+\}\) as Record<string, Importer>/,
      importersReplace
    )
    fs.writeFileSync(RUNTIME_TS, prod, 'utf-8')
  }

  try {
    const result = await esbuild.build({
      entryPoints: [path.resolve(ROOT, '__nexy__/main.ts')],
      outdir: OUT_DIR,
      bundle: true,
      format: 'esm',
      splitting: true,
      metafile: true,
      entryNames: 'assets/[name]-[hash]',
      chunkNames: 'assets/[name]-[hash]',
      assetNames: 'assets/[name]-[hash]',
      logLevel: 'info',
      sourcemap: false,
      conditions: ['style'],
      define: { 'import.meta.env.DEV': 'false' },
      plugins: [ALIAS_PLUGIN],
      loader: {
        '.ttf': 'file',
        '.otf': 'file',
        '.woff': 'file',
        '.woff2': 'file',
        '.eot': 'file',
        '.vue': 'empty',
        '.svelte': 'empty',
      },
    })

    generateManifest(result.metafile)
    console.log(`[nexy] Client bundle complete: ${Object.keys(result.metafile.outputs).length} outputs`)
  } finally {
    if (fs.existsSync(RUNTIME_TS)) {
      const backup = fs.readFileSync(RUNTIME_TS, 'utf-8')
      const restored = backup.replace(
        '({} as Record<string, Importer>)',
        "import.meta.glob('/src/**/*.{tsx,jsx,ts,js,vue,svelte}', { eager: false }) as Record<string, Importer>"
      )
      if (restored !== backup) {
        fs.writeFileSync(RUNTIME_TS, restored, 'utf-8')
      }
    }
  }
}

bundle().catch(err => {
  console.error('[nexy] Bundle failed:', err)
  process.exit(1)
})
