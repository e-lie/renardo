<script lang="ts">
  import type { Snippet } from 'svelte'
  import type { PaneStateInterface } from '@/store/layout/models'

  let {
    pane,
    children,
    onclose
  }: {
    pane: PaneStateInterface
    children?: Snippet
    onclose?: () => void
  } = $props()

  function handleClose() {
    onclose?.()
  }
</script>

<div class="pane border border-base-300 overflow-hidden flex flex-col">
  {#if children}
    {@render children()}
  {:else}
    <div class="p-4 text-center text-base-content/50">
      No content for {pane.title}
    </div>
  {/if}
</div>