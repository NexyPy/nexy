import { runJsxFramework } from './ssg.runner'
import type { SSGResult } from './utils'

export const run = (options?: { primary?: boolean }): Promise<SSGResult> =>
  runJsxFramework(
    {
      name: 'react',
      mdx: true,
      jsxImportSource: 'react',
      external: ['react', 'react-dom', 'react/jsx-runtime', 'react/jsx-dev-runtime'],
      render: async (Component, props) => {
        const { renderToString } = await import('react-dom/server')
        const { createElement } = await import('react')
        return renderToString(createElement(Component as any, props))
      }
    },
    options
  )
