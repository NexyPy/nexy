import { glob } from 'glob'
import fs from 'fs'
import path from 'path'
import { pathToFileURL } from 'node:url'
import esbuild from 'esbuild'
import {
  detectTsxFramework,
  resolveMdxFramework,
  createPropExtractor,
  createJinjaProps,
  restoreJinjaVars,
  isComponent,
  getManifest,
  getAssetTags,
  saveSnippets,
  writeComponent,
  getEntryId,
  globIgnore,
  loadMdxPlugin,
  mapPool,
  type SSGResult,
  c
} from './utils'

/** What differs between the JSX frameworks; everything else is shared below. */
export interface JsxFramework {
  name: 'react' | 'preact' | 'solid'
  /** Whether `.mdx` files are rendered with this framework too. */
  mdx: boolean
  jsxImportSource: string
  external: string[]
  /** The server-rendered HTML of one component. */
  render: (Component: unknown, props: Record<string, unknown>) => Promise<string>
}

const message = (e: unknown) => (e instanceof Error ? e.message : String(e))

function belongsTo(framework: JsxFramework, file: string): boolean {
  const absolute = path.resolve(process.cwd(), file)
  if (path.extname(file) === '.mdx') return resolveMdxFramework(absolute) === framework.name
  return detectTsxFramework(absolute) === framework.name
}

function listFiles(framework: JsxFramework, primary?: boolean): string[] {
  const all = glob.sync(framework.mdx ? '**/*.{tsx,jsx,mdx}' : '**/*.{tsx,jsx}', {
    cwd: process.cwd(),
    ignore: globIgnore()
  })
  return primary ? all : all.filter(file => belongsTo(framework, file))
}

async function bundle(framework: JsxFramework, files: string[], tempDir: string) {
  const entryPoints: Record<string, string> = {}
  for (const [i, file] of files.entries()) {
    entryPoints[`_c${i}`] = path.resolve(process.cwd(), file)
  }
  const plugins = framework.mdx ? await loadMdxPlugin(files, framework.name) : undefined
  try {
    await esbuild.build({
      entryPoints,
      outdir: tempDir,
      bundle: true,
      format: 'esm',
      platform: 'node',
      jsx: 'automatic',
      jsxImportSource: framework.jsxImportSource,
      plugins,
      external: framework.external,
      logLevel: 'silent',
      outExtension: { '.js': '.mjs' },
    })
  } catch (e) {
    console.warn(`${c.yellow}⚠ client-only: ${message(e)} - some files may lack server HTML (client bundle only)${c.reset}`)
  }
}

async function loadModules(files: string[], tempDir: string) {
  const modules = new Map<string, Record<string, any>>()
  for (const [i, file] of files.entries()) {
    const outFile = path.join(tempDir, `_c${i}.mjs`)
    try {
      if (fs.existsSync(outFile)) {
        modules.set(file, await import(`${pathToFileURL(outFile).href}?t=${Date.now()}`))
      }
    } catch (e) {
      console.warn(`${c.yellow}⚠ client-only: ${file} - ${message(e)}, no server HTML (client bundle only)${c.reset}`)
    }
  }
  return modules
}

export async function runJsxFramework(
  framework: JsxFramework,
  options?: { primary?: boolean }
): Promise<SSGResult> {
  const result: SSGResult = { entries: [] }
  const manifest = getManifest()
  const files = listFiles(framework, options?.primary)
  if (!files.length) return result

  const tempDir = path.resolve(process.cwd(), 'node_modules/.nexy-temp-ssg')
  fs.mkdirSync(tempDir, { recursive: true })
  await bundle(framework, files, tempDir)
  const modules = await loadModules(files, tempDir)
  fs.rmSync(tempDir, { recursive: true, force: true })

  const snippets: Record<string, string> = {}
  const getPropPaths = createPropExtractor(files.map(f => path.resolve(process.cwd(), f)))

  const processFile = async (file: string) => {
    const relativeDir = path.dirname(file)
    const fileName = path.basename(file, path.extname(file))
    const propPaths = getPropPaths(path.resolve(process.cwd(), file))
    const jinjaProps = createJinjaProps(propPaths)

    const mod = modules.get(file)
    if (!mod) {
      result.entries.push({ file, component: '*', status: 'not_supported' })
      return
    }

    let hasComponent = false
    for (const [exportName, Component] of Object.entries(mod)) {
      if (!isComponent(exportName, Component, fileName)) continue
      hasComponent = true

      const entryId = getEntryId(fileName, exportName, framework.name)
      const component = exportName === 'default' ? 'Default' : exportName
      const { css } = getAssetTags(manifest, fileName)

      try {
        const html = await framework.render(Component, jinjaProps)
        writeComponent(relativeDir, entryId, `${css}${restoreJinjaVars(html, propPaths)}`, snippets)
        result.entries.push({ file, component, status: 'success' })
      } catch (e) {
        console.warn(`${c.yellow}⚠ client-only: ${file} - ${message(e)}, using client placeholder (no server HTML)${c.reset}`)
        writeComponent(relativeDir, entryId, `${css}<div id="${entryId}-root"></div>`, snippets)
        result.entries.push({ file, component, status: 'not_supported' })
      }
    }
    if (!hasComponent) {
      result.entries.push({ file, component: '*', status: 'not_supported' })
    }
  }

  await mapPool(files, processFile)

  saveSnippets(snippets)
  return result
}
