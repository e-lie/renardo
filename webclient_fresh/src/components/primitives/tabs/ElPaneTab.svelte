<script lang="ts">
  import type { Snippet } from 'svelte'
  import type { PaneTabStateInterface } from '@/store/layout/models'

  let {
    tab,
    onclick,
    onclose
  }: {
    tab: PaneTabStateInterface
    onclick?: () => void
    onclose?: () => void
  } = $props()

  function handleClick() {
    onclick?.()
  }

  function handleClose(e: MouseEvent) {
    e.stopPropagation()
    onclose?.()
  }
</script>

<span
  role="button"
  tabindex="0"
  class="btn btn-primary btn-sm"
  class:btn-primary={tab.isActive}
  onclick={handleClick}
  onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') { handleClick() } }}
>
  {tab.title}
  {#if tab.isCloseable}
    <span
      role="button"
      tabindex="0"
      class="ml-2 w-4 h-4 rounded-full hover:bg-base-300 flex items-center justify-center text-xs"
      onclick={handleClose}
      onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') { handleClose(e) } }}
    >×</span>
  {/if}
</span>