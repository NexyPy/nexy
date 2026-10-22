import { glob } from 'glob'
import fs from 'fs'
import path from 'path'
import { pathToFileURL } from 'node:url'
import esbuild from 'esbuild'
import {
  detectTsxFramework,
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
  mapPool,
  type SSGResult,
  c
} from './utils'

export async function run(options?: { primary?: boolean }): Promise<SSGResult> {
  const result: SSGResult = { entries: [] }
  const manifest = getManifest()
  const allFiles = glob.sync('**/*.{tsx,jsx}', {
    cwd: process.cwd(),
    ignore: globIgnore()
  })
  const files = options?.primary
    ? allFiles
    : allFiles.filter(f => detectTsxFramework(path.resolve(process.cwd(), f)) === 'solid')

  if (!files.length) return result

  const tempDir = path.resolve(process.cwd(), 'node_modules/.nexy-temp-ssg')
  fs.mkdirSync(tempDir, { recursive: true })

  const modules = new Map<string, Record<string, any>>()

  const entryPoints: Record<string, string> = {}
  for (const [i, file] of files.entries()) {
    entryPoints[`_c${i}`] = path.resolve(process.cwd(), file)
  }

  try {
    await esbuild.build({
      entryPoints,
      outdir: tempDir,
      bundle: true,
      format: 'esm',
      platform: 'node',
      jsx: 'automatic',
      jsxImportSource: 'solid-js',
      external: ['solid-js', 'solid-js/web', 'solid-js/store'],
      logLevel: 'silent',
      outExtension: { '.js': '.mjs' },
    })
  } catch (e) {
    const errMsg = e instanceof Error ? e.message : String(e)
    console.warn(`${c.yellow}⚠ client-only: ${errMsg} - some files may lack server HTML (client bundle only)${c.reset}`)
  }

  for (const [i, file] of files.entries()) {
    const outFile = path.join(tempDir, `_c${i}.mjs`)
    try {
      if (fs.existsSync(outFile)) {
        const mod = await import(`${pathToFileURL(outFile).href}?t=${Date.now()}`)
        modules.set(file, mod)
      }
    } catch (e) {
      const errMsg = e instanceof Error ? e.message : String(e)
      console.warn(`${c.yellow}⚠ client-only: ${file} - ${errMsg}, no server HTML (client bundle only)${c.reset}`)
    }
  }

  fs.rmSync(tempDir, { recursive: true, force: true })

  const snippets: Record<string, string> = {}

  const getPropPaths = createPropExtractor(files.map(f => path.resolve(process.cwd(), f)))

  const processFile = async (file: string) => {
    const relativeDir = path.dirname(file)
    const ext = path.extname(file)
    const fileName = path.basename(file, ext)

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

      const entryId = getEntryId(fileName, exportName, 'solid')

      try {
        const { renderToString } = await import('solid-js/web')
        const html = renderToString(() => (Component as any)(jinjaProps))
        const out = restoreJinjaVars(html, propPaths)
        const { css } = getAssetTags(manifest, fileName)
        writeComponent(relativeDir, entryId, `${css}${out}`, snippets)
        result.entries.push({ file, component: exportName === 'default' ? 'Default' : exportName, status: 'success' })
      } catch (e) {
        const errMsg = e instanceof Error ? e.message : String(e)
        console.warn(`${c.yellow}⚠ client-only: ${file} - ${errMsg}, using client placeholder (no server HTML)${c.reset}`)
        const { css } = getAssetTags(manifest, fileName)
        writeComponent(relativeDir, entryId, `${css}<div id="${entryId}-root"></div>`, snippets)
        result.entries.push({ file, component: exportName === 'default' ? 'Default' : exportName, status: 'not_supported' })
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
