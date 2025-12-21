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
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      {filename}
    </button>
  {/each}
  {#if children}
    {@render children()}
  {/if}
</div>