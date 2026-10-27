<script lang="ts">
  // An <img> that is lazy by default and never shifts the layout when its size is known.
  import type { HTMLImgAttributes } from 'svelte/elements'
  import { cssText, imageAttributes, warnMissingAlt, type ImageProps } from './shared.ts'

  type Props = Omit<HTMLImgAttributes, 'src' | 'alt' | 'width' | 'height' | 'loading' | 'sizes' | 'srcset'> &
    ImageProps

  let { src, alt, width, height, priority, fill, loading, sizes, srcSet, style, ...rest }: Props = $props()

  warnMissingAlt(alt)
  const attributes = $derived(imageAttributes({ src, alt, width, height, priority, fill, loading, sizes, srcSet }))
  const css = $derived([cssText(attributes.style), style].filter(Boolean).join(';') || undefined)
</script>

<img {...rest} {...attributes} style={css} />
