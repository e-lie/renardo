<script lang="ts">
  import type { Snippet } from 'svelte'

  let {
    files = [],
    onloadfile,
    children
  }: {
    files?: string[]
    onloadfile?: (file: string) => void
    children?: Snippet
  } = $props()

  function handleLoadFile(filename: string) {
    onloadfile?.(filename)
  }
</script>

<div class="flex flex-col gap-2">
  {#each files as filename}
    <button
      class="btn btn-sm btn-outline justify-start text-left"
      onclick={() => handleLoadFile(filename)}
      title="Load tutorial"
    >
      {filename}
    </button>
  {/each}
  {#if children}
    {@render children()}
  {/if}
</div>