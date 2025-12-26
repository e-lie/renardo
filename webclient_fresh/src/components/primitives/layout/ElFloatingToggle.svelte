<script lang="ts">
  import type { Snippet } from 'svelte'

  let {
    position = 'left',
    onclick,
    onmouseenter,
    onmouseleave,
    title = '',
    testid = 'floating-toggle',
    children,
    offset = 0
  }: {
    position?: 'left' | 'right' | 'bottom'
    onclick?: () => void
    onmouseenter?: () => void
    onmouseleave?: () => void
    title?: string
    testid?: string
    children?: Snippet
    offset?: number
  } = $props()

  const positionClasses = $derived.by(() => {
    if (position === 'left') return `fixed top-1/2 -translate-y-1/2`
    if (position === 'right') return `fixed top-1/2 -translate-y-1/2`
    return `fixed left-1/2 -translate-x-1/2`
  })

  const positionStyles = $derived.by(() => {
    if (position === 'left') return `left: ${offset + 16}px`
    if (position === 'right') return `right: ${offset + 16}px`
    return `bottom: ${offset + 8}px`
  })

  const cssClass = $derived(
    `btn btn-icon variant-filled-primary shadow-xl z-50 ${positionClasses}`
  )
</script>

<button
  data-testid={testid}
  class={cssClass}
  style={positionStyles}
  {onclick}
  {onmouseenter}
  {onmouseleave}
  {title}
>
  {#if children}
    {@render children()}
  {/if}
</button>
