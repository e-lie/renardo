<script lang="ts">
  import type { Snippet } from 'svelte'

  let {
    testid = 'not-set',
    addCss = '',
    children
  }: {
    testid?: string
    addCss?: string
    children?: Snippet
  } = $props()

  const cssClass = $derived.by(() => {
    const baseClasses = ['card bg-base-100 shadow-xl']

    if (addCss) {
      baseClasses.push(addCss)
    }

    return baseClasses.join(' ')
  })
</script>

<div data-testid={testid} class={cssClass}>
  {#if children}
    {@render children()}
  {/if}
</div>
