// The snapshots of an island rendered with the literal props the pages give it (#554).
// `nx build` lists those props in __nexy__/island-props.json, by island file, imported
// symbol and key. Each snapshot is written next to the default one as <entry>.<key>.html: the
// name the server looks up for those props, falling back to the default snapshot.
import fs from 'fs'
import path from 'path'

type Props = Record<string, unknown>
export type IslandProps = Record<string, Record<string, Record<string, Props>>>

/** The props the pages give each island, or none when the build listed nothing. */
export function readIslandProps(root: string = process.cwd()): IslandProps {
  try {
    const file = path.join(root, '__nexy__/island-props.json')
    return JSON.parse(fs.readFileSync(file, 'utf-8')) as IslandProps
  } catch {
    return {}
  }
}

/**
 * The props of each snapshot of one export of a file. A page imports a symbol: the export of that
 * name, else the default export, as the server looks them up.
 */
export function propsFor(
  all: IslandProps,
  file: string,
  exportName: string,
  exportNames: string[]
): Record<string, Props> {
  const picked: Record<string, Props> = {}
  for (const [symbol, byKey] of Object.entries(all[file.replace(/\\/g, '/')] ?? {})) {
    const target = exportNames.includes(symbol) ? symbol : 'default'
    if (target === exportName) Object.assign(picked, byKey)
  }
  return picked
}

/** The HTML of each snapshot by key. One that fails is reported; its island keeps the default. */
export async function renderVariants(
  file: string,
  render: (props: Props) => Promise<string>,
  picked: Record<string, Props>,
  warn: (message: string) => void = console.warn
): Promise<Array<[string, string]>> {
  const rendered: Array<[string, string]> = []
  for (const [key, props] of Object.entries(picked)) {
    try {
      rendered.push([key, await render(props)])
    } catch (e) {
      const reason = e instanceof Error ? e.message : String(e)
      const given = JSON.stringify(props)
      warn(`warning: ${file} with ${given} - ${reason}, using its default server HTML`)
    }
  }
  return rendered
}
