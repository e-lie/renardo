<script lang="ts">
  import type { Snippet } from 'svelte'

  let {
    position = 'left',
    onclick,
    onmouseenter,
    onmouseleave,
    title = '',
    testid = 'floating-toggle',
    children
  }: {
    position?: 'left' | 'right' | 'bottom'
    onclick?: () => void
    onmouseenter?: () => void
    onmouseleave?: () => void
    title?: string
    testid?: string
    children?: Snippet
  } = $props()

  const positionClasses = $derived.by(() => {
    if (position === 'left') return 'fixed left-4 top-1/2 -translate-y-1/2'
    if (position === 'right') return 'fixed right-4 top-1/2 -translate-y-1/2'
    return 'fixed bottom-2 left-1/2 -translate-x-1/2'
  })

  const cssClass = $derived(
    `w-8 h-8 rounded-full bg-transparent border-2 border-primary-500 text-primary-500 shadow-xl z-50 flex items-center justify-center hover:bg-primary-500/10 transition-colors ${positionClasses}`
  )
</script>

<button
  data-testid={testid}
  class={cssClass}
  {onclick}
  {onmouseenter}
  {onmouseleave}
  {title}
>
  {#if children}
    {@render children()}
  {/if}
</button>
