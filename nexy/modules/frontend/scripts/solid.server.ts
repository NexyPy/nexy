// Solid JSX is not a call to a `jsx()` function: Solid's own Babel preset compiles it, into string
// templates for the server. esbuild's JSX transform only fits React-like runtimes (#563), so this
// plugin hands every `.tsx`/`.jsx` file to the preset before esbuild bundles it.
import fs from 'node:fs'
import path from 'node:path'
import { createRequire } from 'node:module'
import type { Plugin } from 'esbuild'

type Babel = { transformAsync: (code: string, options: object) => Promise<{ code?: string | null } | null> }

/** A package of the project, or one that vite-plugin-solid brought (pnpm does not hoist those). */
function load(name: string): unknown {
  const project = createRequire(path.resolve(process.cwd(), 'package.json'))
  try {
    return project(name)
  } catch {
    return createRequire(project.resolve('vite-plugin-solid'))(name)
  }
}

export function solidServerJsx(): Plugin {
  return {
    name: 'nexy-solid-server-jsx',
    setup(build) {
      const babel = load('@babel/core') as Babel
      const preset = load('babel-preset-solid')
      build.onLoad({ filter: /\.[jt]sx$/ }, async (args) => {
        const source = await fs.promises.readFile(args.path, 'utf8')
        const loader = args.path.endsWith('.tsx') ? 'tsx' : 'jsx'
        // Types out first, JSX kept: the preset reads JSX, not TypeScript.
        const plain = await build.esbuild.transform(source, { loader, jsx: 'preserve' })
        const compiled = await babel.transformAsync(plain.code, {
          filename: args.path,
          babelrc: false,
          configFile: false,
          presets: [[preset, { generate: 'ssr', hydratable: false }]],
        })
        return { contents: compiled?.code ?? '', loader: 'js', resolveDir: path.dirname(args.path) }
      })
    },
  }
}
