<script lang="ts">
  import { useLogsStore } from '../store/logs'
  import LogsList from '../components/logs/LogsList.component.svelte'
  import ElButton from '../components/primitives/buttons/ElButton.svelte'
  import { onMount, onDestroy } from 'svelte'

  const logsStore = useLogsStore()
  const { loading, filteredLogs, filterLevel } = logsStore.getters

  // Load historical logs and subscribe to new ones on mount
  onMount(() => {
    logsStore.actions.loadLogs(1000)
    logsStore.actions.subscribeToLogs()
  })

  // Unsubscribe when component is destroyed
  onDestroy(() => {
    logsStore.actions.unsubscribeFromLogs()
  })

  function handleFilterChange(level: string | null) {
    logsStore.actions.setFilterLevel(level)
  }

  function handleRefresh() {
    logsStore.actions.loadLogs(1000)
  }

  function handleClear() {
    // This would clear logs - for now just reload
    logsStore.actions.loadLogs(100)
  }
</script>

<div class="container mx-auto p-4">
  <div class="flex justify-between items-center mb-6">
    <div>
      <h1 class="text-3xl font-bold">System Logs</h1>
      <p class="text-sm text-gray-500 mt-1">Real-time log viewer for Renardo</p>
    </div>
    <div class="flex gap-2">
      <ElButton variant="ghost" onclick={handleRefresh} addCss="btn-sm">
        Refresh
      </ElButton>
      <ElButton variant="ghost" onclick={handleClear} addCss="btn-sm">
        Clear & Reload (100)
      </ElButton>
    </div>
  </div>

  {#if $loading}
    <div class="flex justify-center items-center py-12">
      <span class="loading loading-spinner loading-lg"></span>
      <span class="ml-4 text-gray-500">Loading logs...</span>
    </div>
  {:else}
    <LogsList
      logs={$filteredLogs}
      filterLevel={$filterLevel}
      onfilterchange={handleFilterChange}
    />
  {/if}
</div>
