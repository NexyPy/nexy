import { glob } from 'glob'
import fs from 'fs'
import path from 'path'
import { pathToFileURL } from 'node:url'
import esbuild, { type Plugin } from 'esbuild'
import { renderSnapshot } from './ssg.snapshot'
import { propsFor, readIslandProps, renderVariants } from './ssg.variants'
import {
  detectTsxFramework,
  resolveMdxFramework,
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
  /** esbuild plugins that compile this framework's JSX, when esbuild's own transform does not. */
  plugins?: () => Plugin[]
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

/** The bundle of every file; on failure, the message of esbuild, for the files it left out. */
async function bundle(framework: JsxFramework, files: string[], tempDir: string): Promise<string> {
  const entryPoints: Record<string, string> = {}
  for (const [i, file] of files.entries()) {
    entryPoints[`_c${i}`] = path.resolve(process.cwd(), file)
  }
  const mdx = framework.mdx ? await loadMdxPlugin(files, framework.name) : undefined
  const plugins = [...(framework.plugins?.() ?? []), ...(mdx ?? [])]
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
    return ''
  } catch (e) {
    console.warn(`${c.yellow}warning:${c.reset} client-only: ${message(e)} - some files may lack server HTML (client bundle only)${c.reset}`)
    return message(e)
  }
}

async function loadModules(files: string[], tempDir: string, reasons: Map<string, string>) {
  const modules = new Map<string, Record<string, any>>()
  for (const [i, file] of files.entries()) {
    const outFile = path.join(tempDir, `_c${i}.mjs`)
    try {
      if (fs.existsSync(outFile)) {
        modules.set(file, await import(`${pathToFileURL(outFile).href}?t=${Date.now()}`))
      }
    } catch (e) {
      console.warn(`${c.yellow}warning:${c.reset} client-only: ${file} - ${message(e)}, no server HTML (client bundle only)${c.reset}`)
      reasons.set(file, message(e))
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
  const reasons = new Map<string, string>()
  const bundleError = await bundle(framework, files, tempDir)
  const modules = await loadModules(files, tempDir, reasons)
  fs.rmSync(tempDir, { recursive: true, force: true })

  const snippets: Record<string, string> = {}
  const islandProps = readIslandProps()

  const processFile = async (file: string) => {
    const relativeDir = path.dirname(file)
    const fileName = path.basename(file, path.extname(file))

    const mod = modules.get(file)
    if (!mod) {
      const reason = reasons.get(file) || bundleError || 'the module could not be built'
      result.entries.push({ file, component: '*', status: 'not_supported', reason })
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
        const html = await renderSnapshot(framework.render, Component)
        writeComponent(relativeDir, entryId, `${css}${html}`, snippets)
        const picked = propsFor(islandProps, file, exportName, Object.keys(mod))
        const render = (props: Record<string, unknown>) =>
          renderSnapshot(framework.render, Component, props)
        for (const [key, variant] of await renderVariants(file, render, picked)) {
          writeComponent(relativeDir, `${entryId}.${key}`, `${css}${variant}`, snippets)
        }
        result.entries.push({ file, component, status: 'success' })
      } catch (e) {
        console.warn(`${c.yellow}warning:${c.reset} client-only: ${file} - ${message(e)}, using client placeholder (no server HTML)${c.reset}`)
        writeComponent(relativeDir, entryId, `${css}<div id="${entryId}-root"></div>`, snippets)
        result.entries.push({ file, component, status: 'not_supported', reason: message(e) })
      }
    }
    if (!hasComponent) {
      const reason = 'it exports no component (a function whose name starts with a capital)'
      result.entries.push({ file, component: '*', status: 'not_supported', reason })
    }
  }

  await mapPool(files, processFile)

  saveSnippets(snippets)
  return result
}
