// The HTML an island carries before hydration: what a visitor without JavaScript, or a crawler,
// reads. No imports: it renders with whatever renderer the framework gives it.

type Render = (Component: unknown, props: Record<string, unknown>) => Promise<string>

/** Collapse the whitespace inside class attributes, so the server HTML is stable. */
export const normalizeClassWhitespace = (html: string): string =>
  html.replace(
    /(\sclass(?:Name)?=")([^"]+)(")/g,
    (_, prefix, classes, suffix) => `${prefix}${classes.trim().replace(/\s+/g, ' ')}${suffix}`
  )

/**
 * The snapshot of one component. With no props it shows its own defaults (#591); with the literal
 * props a page gives it, what that page shows before hydration (#554).
 */
export async function renderSnapshot(
  render: Render,
  Component: unknown,
  props: Record<string, unknown> = {}
): Promise<string> {
  return normalizeClassWhitespace(await render(Component, props))
}
