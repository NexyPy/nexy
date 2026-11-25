// Default template. The generator writes the project's responsive images here.
export type ImageVariant = {
  src: string
  srcset: string
  sizes: string
  width: number
  height: number
}
export const IMAGE_VARIANTS: Record<string, ImageVariant> = {}
