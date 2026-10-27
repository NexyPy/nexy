import { runJsxFramework } from './ssg.runner'
import type { SSGResult } from './utils'

export const run = (options?: { primary?: boolean }): Promise<SSGResult> =>
  runJsxFramework(
    {
      name: 'solid',
      mdx: false,
      jsxImportSource: 'solid-js',
      external: ['solid-js', 'solid-js/web', 'solid-js/store'],
      render: async (Component, props) => {
        const { renderToString } = await import('solid-js/web')
        return renderToString(() => (Component as any)(props))
      }
    },
    options
  )
