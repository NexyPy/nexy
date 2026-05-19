import { glob } from 'glob'
import fs from 'fs'
import path from 'path'
import { pathToFileURL } from 'node:url'
import esbuild from 'esbuild'
import {
  detectTsxFramework,
  extractPropPaths,
  createJinjaProps,
  restoreJinjaVars,
  isComponent,
  getManifest,
  getAssetTags,
  saveSnippets,
  writeComponent,
  getEntryId,
  type SSGResult,
  c,
} from './utils'

export async function run(options?: { primary?: boolean }): Promise<SSGResult> {
  const result: SSGResult = { entries: [] }
  const manifest = getManifest()
  const allFiles = glob.sync('**/*.{tsx,jsx}', {
    cwd: process.cwd(),
    ignore: ['node_modules/**', 'dist/**', '__nexy__/**', '.git/**', 'public/**']
  })
  const files = options?.primary
    ? allFiles
    : allFiles.filter(f => detectTsxFramework(path.resolve(process.cwd(), f)) === 'preact')

  if (!files.length) return result

  const tempDir = path.resolve(process.cwd(), 'node_modules/.nexy-temp-ssg')
  fs.mkdirSync(tempDir, { recursive: true })

  const modules = new Map<string, Record<string, any>>()
  const ts = Date.now()

  for (let i = 0; i < files.length; i++) {
    const outFile = path.join(tempDir, `_c${i}.mjs`)
    try {
      await esbuild.build({
        entryPoints: { [`_c${i}`]: path.resolve(process.cwd(), files[i]) },
        outdir: tempDir,
        bundle: true,
        format: 'esm',
        platform: 'node',
        jsx: 'automatic',
        jsxImportSource: 'preact',
        external: ['preact', 'preact/jsx-runtime'],
        logLevel: 'silent',
        outExtension: { '.js': '.mjs' },
      })

      if (fs.existsSync(outFile)) {
        const mod = await import(`${pathToFileURL(outFile).href}?t=${ts}`)
        modules.set(files[i], mod)
      }
    } catch (e) {
      const errMsg = e instanceof Error ? e.message : String(e)
      console.warn(`${c.yellow}⚠ client-only: ${files[i]} — ${errMsg}, no server HTML (client bundle only)${c.reset}`)
    }
  }

  fs.rmSync(tempDir, { recursive: true, force: true })

  const snippets: Record<string, string> = {}

  for (const file of files) {
    const relativeDir = path.dirname(file)
    const ext = path.extname(file)
    const fileName = path.basename(file, ext)

    const propPaths = extractPropPaths(path.resolve(process.cwd(), file))
    const jinjaProps = createJinjaProps(propPaths)

    const mod = modules.get(file)
    if (!mod) {
      result.entries.push({ file, component: '*', status: 'not_supported' })
      continue
    }

    let hasComponent = false
    for (const [exportName, Component] of Object.entries(mod)) {
      if (!isComponent(exportName, Component, fileName)) continue
      hasComponent = true

      const entryId = getEntryId(fileName, exportName, 'preact')

      try {
        const { renderToString } = await import('preact-render-to-string')
        const { h } = await import('preact')
        const html = renderToString(h(Component as any, jinjaProps))
        const out = restoreJinjaVars(html, propPaths)
        const { css } = getAssetTags(manifest, fileName)
        writeComponent(relativeDir, entryId, `${css}${out}`, snippets)
        result.entries.push({ file, component: exportName === 'default' ? 'Default' : exportName, status: 'success' })
      } catch (e) {
        const errMsg = e instanceof Error ? e.message : String(e)
        console.warn(`${c.yellow}⚠ client-only: ${file} — ${errMsg}, using client placeholder (no server HTML)${c.reset}`)
        const { css } = getAssetTags(manifest, fileName)
        writeComponent(relativeDir, entryId, `${css}<div id="${entryId}-root"></div>`, snippets)
        result.entries.push({ file, component: exportName === 'default' ? 'Default' : exportName, status: 'not_supported' })
      }
    }
    if (!hasComponent) {
      result.entries.push({ file, component: '*', status: 'not_supported' })
    }
  }

  saveSnippets(snippets)
  return result
}
