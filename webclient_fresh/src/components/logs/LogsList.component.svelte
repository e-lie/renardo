<script lang="ts">
  import type { LogEntryInterface } from '../../models/logs'
  import LogCard from './children/LogCard.component.svelte'
  import ElButton from '../primitives/buttons/ElButton.svelte'

  let {
    logs,
    filterLevel,
    onfilterchange
  }: {
    logs: LogEntryInterface[]
    filterLevel: string | null
    onfilterchange?: (level: string | null) => void
  } = $props()

  const logLevels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

  function handleFilterClick(level: string | null) {
    onfilterchange?.(level)
  }
</script>

<div class="flex flex-col gap-4">
  <!-- Filter buttons -->
  <div class="flex gap-2 flex-wrap">
    <ElButton
      variant={filterLevel === null ? 'primary' : 'ghost'}
      onclick={() => handleFilterClick(null)}
      addCss="btn-sm"
    >
      All
    </ElButton>
    {#each logLevels as level}
      <ElButton
        variant={filterLevel === level ? 'primary' : 'ghost'}
        onclick={() => handleFilterClick(level)}
        addCss="btn-sm"
      >
        {level}
      </ElButton>
    {/each}
  </div>

  <!-- Logs count -->
  <div class="text-sm text-gray-500">
    Showing {logs.length} log{logs.length !== 1 ? 's' : ''}
  </div>

  <!-- Logs list -->
  <div class="flex flex-col">
    {#if logs.length === 0}
      <div class="text-center py-8 text-gray-500">
        No logs to display
      </div>
    {:else}
      {#each logs as log (log.id)}
        <LogCard {log} />
      {/each}
    {/if}
  </div>
</div>
