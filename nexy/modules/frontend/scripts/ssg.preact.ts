import { runJsxFramework } from './ssg.runner'
import type { SSGResult } from './utils'

export const run = (options?: { primary?: boolean }): Promise<SSGResult> =>
  runJsxFramework(
    {
      name: 'preact',
      mdx: true,
      jsxImportSource: 'preact',
      external: ['preact', 'preact/jsx-runtime'],
      render: async (Component, props) => {
        const { renderToString } = await import('preact-render-to-string')
        const { h } = await import('preact')
        return renderToString(h(Component as any, props))
      }
    },
    options
  )
