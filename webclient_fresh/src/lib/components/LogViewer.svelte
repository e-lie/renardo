<script lang="ts">
  import { onMount, onDestroy } from 'svelte'
  import { subscriptionStore, getContextClient } from '@urql/svelte'
  import { currentPage } from '../stores'

  interface LogEntry {
    id: string
    timestamp: string
    level: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL'
    logger: string
    source: string
    message: string
    extra?: any
  }

  let logs: LogEntry[] = []
  let filteredLogs: LogEntry[] = []
  let autoScroll = true
  let connected = false
  let logContainer: HTMLDivElement

  // Filters
  let searchQuery = ''
  let selectedLoggers: Set<string> = new Set()
  let selectedSources: Set<string> = new Set()
  let selectedLevels: Set<string> = new Set(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
  let showFilters = true

  // Available loggers and sources (will be populated from logs)
  let availableLoggers: string[] = []
  let availableSources: string[] = []

  // Color schemes for different loggers
  const loggerColors: Record<string, string> = {
    'renardo.main': 'text-blue-500',
    'renardo.process_manager': 'text-green-500',
    'renardo.webserver': 'text-purple-500',
    'renardo.logger': 'text-yellow-500',
    'renardo.reaper': 'text-pink-500',
    'BACKEND': 'text-orange-500',
    'FRONTEND': 'text-cyan-500',
    'FLOK': 'text-indigo-500',
    'default': 'text-base-content'
  }

  // Color schemes for log levels
  const levelColors: Record<string, string> = {
    'DEBUG': 'badge-ghost',
    'INFO': 'badge-info',
    'WARNING': 'badge-warning',
    'ERROR': 'badge-error',
    'CRITICAL': 'badge-error font-bold'
  }

  function getLoggerColor(logger: string): string {
    return loggerColors[logger] || loggerColors['default']
  }

  function getLevelColor(level: string): string {
    return levelColors[level] || ''
  }

  // GraphQL subscription for logs
  const client = getContextClient()
  const logsSubscription = subscriptionStore({
    client,
    query: `
      subscription {
        logs {
          id
          timestamp
          level
          logger
          source
          message
          extra
        }
      }
    `
  })

  // React to subscription updates
  $: if ($logsSubscription.data?.logs) {
    const logEntry = $logsSubscription.data.logs as LogEntry

    // Add to logs
    logs = [...logs, logEntry]

    // Keep only last 1000 logs in memory
    if (logs.length > 1000) {
      logs = logs.slice(-1000)
    }

    // Update available loggers and sources
    if (!availableLoggers.includes(logEntry.logger)) {
      availableLoggers = [...availableLoggers, logEntry.logger].sort()
      // Auto-select new loggers
      if (selectedLoggers.size === 0) {
        selectedLoggers.add(logEntry.logger)
      }
    }
    if (!availableSources.includes(logEntry.source)) {
      availableSources = [...availableSources, logEntry.source].sort()
      // Auto-select new sources
      if (selectedSources.size === 0) {
        selectedSources.add(logEntry.source)
      }
    }

    // Apply filters
    applyFilters()

    // Auto-scroll to bottom
    if (autoScroll && logContainer) {
      setTimeout(() => {
        logContainer.scrollTop = logContainer.scrollHeight
      }, 10)
    }
  }

  // Connection status
  $: connected = !$logsSubscription.error && !$logsSubscription.fetching

  function applyFilters() {
    filteredLogs = logs.filter(log => {
      // Level filter
      if (!selectedLevels.has(log.level)) return false

      // Logger filter
      if (selectedLoggers.size > 0 && !selectedLoggers.has(log.logger)) return false

      // Source filter
      if (selectedSources.size > 0 && !selectedSources.has(log.source)) return false

      // Search filter
      if (searchQuery) {
        const query = searchQuery.toLowerCase()
        return log.message.toLowerCase().includes(query) ||
               log.logger.toLowerCase().includes(query) ||
               log.source.toLowerCase().includes(query)
      }

      return true
    })
  }

  function clearLogs() {
    logs = []
    filteredLogs = []
  }

  function exportLogs() {
    const dataStr = JSON.stringify(filteredLogs, null, 2)
    const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr)

    const exportFileDefaultName = `renardo-logs-${new Date().toISOString()}.json`

    const linkElement = document.createElement('a')
    linkElement.setAttribute('href', dataUri)
    linkElement.setAttribute('download', exportFileDefaultName)
    linkElement.click()
  }

  function toggleLogger(logger: string) {
    if (selectedLoggers.has(logger)) {
      selectedLoggers.delete(logger)
    } else {
      selectedLoggers.add(logger)
    }
    selectedLoggers = selectedLoggers
    applyFilters()
  }

  function toggleSource(source: string) {
    if (selectedSources.has(source)) {
      selectedSources.delete(source)
    } else {
      selectedSources.add(source)
    }
    selectedSources = selectedSources
    applyFilters()
  }

  function toggleLevel(level: string) {
    if (selectedLevels.has(level)) {
      selectedLevels.delete(level)
    } else {
      selectedLevels.add(level)
    }
    selectedLevels = selectedLevels
    applyFilters()
  }

  function selectAllLoggers() {
    selectedLoggers = new Set(availableLoggers)
    applyFilters()
  }

  function deselectAllLoggers() {
    selectedLoggers = new Set()
    applyFilters()
  }

  function goBack() {
    currentPage.set('posts')
  }

  // Watch for search query changes
  $: if (searchQuery !== undefined) {
    applyFilters()
  }

  onMount(() => {
    // Subscription starts automatically
    console.log('LogViewer mounted, subscription starting...')
  })

  onDestroy(() => {
    // Subscription cleanup is handled by URQL
    console.log('LogViewer destroyed')
  })
</script>

<div class="h-full flex flex-col bg-base-100">
  <!-- Header -->
  <div class="navbar bg-base-200 border-b border-base-300">
    <div class="navbar-start">
      <button class="btn btn-ghost btn-sm" on:click={goBack}>
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        Back
      </button>

      <div class="divider divider-horizontal"></div>

      <h2 class="text-lg font-semibold">Renardo Logs</h2>

      {#if connected}
        <div class="badge badge-success ml-3">Connected</div>
      {:else}
        <div class="badge badge-error ml-3">Disconnected</div>
      {/if}

      <div class="badge badge-ghost ml-2">{filteredLogs.length} / {logs.length} logs</div>
    </div>

    <div class="navbar-end space-x-2">
      <button
        class="btn btn-ghost btn-sm"
        class:btn-active={showFilters}
        on:click={() => showFilters = !showFilters}
      >
        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
        </svg>
        Filters
      </button>

      <button
        class="btn btn-ghost btn-sm"
        class:btn-active={autoScroll}
        on:click={() => autoScroll = !autoScroll}
      >
        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
        </svg>
        Auto-scroll
      </button>

      <button class="btn btn-ghost btn-sm" on:click={exportLogs}>
        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
        </svg>
        Export
      </button>

      <button class="btn btn-ghost btn-sm" on:click={clearLogs}>
        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
        </svg>
        Clear
      </button>
    </div>
  </div>

  <div class="flex flex-1 overflow-hidden">
    <!-- Filters Panel -->
    {#if showFilters}
      <div class="w-80 bg-base-200 p-4 overflow-y-auto border-r border-base-300">
        <!-- Search -->
        <div class="form-control mb-4">
          <label class="label">
            <span class="label-text">Search</span>
          </label>
          <input
            type="text"
            placeholder="Filter messages..."
            class="input input-bordered input-sm w-full"
            bind:value={searchQuery}
          />
        </div>

        <!-- Log Levels -->
        <div class="form-control mb-4">
          <label class="label">
            <span class="label-text">Log Levels</span>
          </label>
          <div class="space-y-1">
            {#each ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] as level}
              <label class="label cursor-pointer justify-start space-x-2">
                <input
                  type="checkbox"
                  class="checkbox checkbox-sm"
                  checked={selectedLevels.has(level)}
                  on:change={() => toggleLevel(level)}
                />
                <span class="label-text">
                  <span class="badge {getLevelColor(level)} badge-sm">{level}</span>
                </span>
              </label>
            {/each}
          </div>
        </div>

        <!-- Loggers -->
        <div class="form-control mb-4">
          <label class="label">
            <span class="label-text">Loggers</span>
            <div class="space-x-1">
              <button class="btn btn-ghost btn-xs" on:click={selectAllLoggers}>All</button>
              <button class="btn btn-ghost btn-xs" on:click={deselectAllLoggers}>None</button>
            </div>
          </label>
          <div class="space-y-1 max-h-60 overflow-y-auto">
            {#each availableLoggers as logger}
              <label class="label cursor-pointer justify-start space-x-2">
                <input
                  type="checkbox"
                  class="checkbox checkbox-sm"
                  checked={selectedLoggers.has(logger)}
                  on:change={() => toggleLogger(logger)}
                />
                <span class="label-text {getLoggerColor(logger)}">{logger}</span>
              </label>
            {/each}
          </div>
        </div>

        <!-- Sources -->
        {#if availableSources.length > 0}
          <div class="form-control">
            <label class="label">
              <span class="label-text">Sources</span>
            </label>
            <div class="space-y-1 max-h-40 overflow-y-auto">
              {#each availableSources as source}
                <label class="label cursor-pointer justify-start space-x-2">
                  <input
                    type="checkbox"
                    class="checkbox checkbox-sm"
                    checked={selectedSources.has(source)}
                    on:change={() => toggleSource(source)}
                  />
                  <span class="label-text text-xs">{source}</span>
                </label>
              {/each}
            </div>
          </div>
        {/if}
      </div>
    {/if}

    <!-- Logs Display -->
    <div class="flex-1 overflow-y-auto p-4 font-mono text-sm" bind:this={logContainer}>
      {#if filteredLogs.length === 0}
        <div class="text-center py-8 text-base-content/60">
          {#if logs.length === 0}
            <p>Waiting for logs...</p>
          {:else}
            <p>No logs match the current filters</p>
          {/if}
        </div>
      {:else}
        <div class="space-y-1">
          {#each filteredLogs as log}
            <div class="flex items-start space-x-2 hover:bg-base-200/50 px-2 py-1 rounded">
              <!-- Timestamp -->
              <span class="text-base-content/50 text-xs whitespace-nowrap">
                {new Date(log.timestamp).toLocaleTimeString('en-US', {
                  hour12: false,
                  hour: '2-digit',
                  minute: '2-digit',
                  second: '2-digit',
                  fractionalSecondDigits: 3
                })}
              </span>

              <!-- Level Badge -->
              <span class="badge {getLevelColor(log.level)} badge-xs">
                {log.level}
              </span>

              <!-- Logger Name -->
              <span class="{getLoggerColor(log.logger)} font-semibold whitespace-nowrap">
                [{log.logger}]
              </span>

              <!-- Message -->
              <span class="flex-1 break-all">
                {log.message}
              </span>

              <!-- Source (if different from logger) -->
              {#if log.source && log.source !== log.logger}
                <span class="text-base-content/40 text-xs">
                  ({log.source})
                </span>
              {/if}
            </div>
          {/each}
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  /* Custom scrollbar for log container */
  :global(.dark) {
    --scrollbar-thumb: oklch(var(--b3));
    --scrollbar-track: oklch(var(--b1));
  }

  :global(.light) {
    --scrollbar-thumb: #d1d5db;
    --scrollbar-track: #f3f4f6;
  }

  div::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }

  div::-webkit-scrollbar-track {
    background: var(--scrollbar-track);
  }

  div::-webkit-scrollbar-thumb {
    background: var(--scrollbar-thumb);
    border-radius: 4px;
  }

  div::-webkit-scrollbar-thumb:hover {
    background: var(--scrollbar-thumb);
    opacity: 0.8;
  }
</style>