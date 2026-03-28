<script lang="ts">
  import type { Snippet } from 'svelte'

  let {
    testid = 'not-set',
    type = 'button',
    variant = 'primary',
    disabled = false,
    addCss = '',
    onclick,
    children
  }: {
    testid?: string
    type?: 'button' | 'submit' | 'reset'
    variant?: 'primary' | 'secondary' | 'ghost'
    disabled?: boolean
    addCss?: string
    onclick?: () => void
    children?: Snippet
  } = $props()

  const cssClass = $derived.by(() => {
    const baseClasses = ['btn']

    if (variant === 'primary') {
      baseClasses.push('variant-filled-primary')
    } else if (variant === 'secondary') {
      baseClasses.push('variant-outline-secondary')
    } else if (variant === 'ghost') {
      baseClasses.push('variant-ghost')
    }

    if (addCss) {
      baseClasses.push(addCss)
    }

    return baseClasses.join(' ')
  })
</script>

<button
  {type}
  {disabled}
  data-testid={testid}
  class={cssClass}
  onclick={onclick}
>
  {#if children}
    {@render children()}
  {/if}
</button>
