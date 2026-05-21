import { glob } from 'glob'
import fs from 'fs'
import path from 'path'
import { pathToFileURL } from 'node:url'
import os from 'os'
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
  c
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
    : allFiles.filter(f => detectTsxFramework(path.resolve(process.cwd(), f)) === 'react')

  if (!files.length) return result

  const tempDir = path.resolve(process.cwd(), 'node_modules/.nexy-temp-ssg')
  fs.mkdirSync(tempDir, { recursive: true })

  const modules = new Map<string, Record<string, any>>()
  let idx = 0

  const worker = async () => {
    while (idx < files.length) {
      const i = idx++
      const file = files[i]
      const outFile = path.join(tempDir, `_c${i}.mjs`)
      try {
        await esbuild.build({
          entryPoints: { [`_c${i}`]: path.resolve(process.cwd(), file) },
          outdir: tempDir,
          bundle: true,
          format: 'esm',
          platform: 'node',
          jsx: 'automatic',
          jsxImportSource: 'react',
          external: ['react', 'react-dom', 'react/jsx-runtime', 'react/jsx-dev-runtime'],
          logLevel: 'silent',
          outExtension: { '.js': '.mjs' },
        })
        if (fs.existsSync(outFile)) {
          const mod = await import(`${pathToFileURL(outFile).href}?t=${Date.now()}`)
          modules.set(file, mod)
        }
      } catch (e) {
        const errMsg = e instanceof Error ? e.message : String(e)
        console.warn(`${c.yellow}⚠ client-only: ${file} — ${errMsg}, no server HTML (client bundle only)${c.reset}`)
      }
    }
  }

  const concurrency = Math.min(os.cpus().length, files.length)
  await Promise.all(Array.from({ length: concurrency }, () => worker()))

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

      const entryId = getEntryId(fileName, exportName, 'react')

      try {
        const { renderToString } = await import('react-dom/server')
        const { createElement } = await import('react')
        const html = renderToString(createElement(Component as any, jinjaProps))
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
