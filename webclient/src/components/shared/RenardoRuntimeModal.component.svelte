<script lang="ts">
  import { useRenardoRuntimeStore } from '../../store/renardo-runtime'

  let {
    isOpen = false,
    onclose
  }: {
    isOpen?: boolean
    onclose?: () => void
  } = $props()

  const { actions, getters } = useRenardoRuntimeStore()
  const { status, isLoading, error, runtimeLogs } = getters

  $effect(() => {
    if (isOpen) {
      actions.loadStatus()
    }
  })

  function handleClose() {
    onclose?.()
  }

  function handleBackdropClick(e: MouseEvent) {
    if (e.target === e.currentTarget) {
      handleClose()
    }
  }

  // Derive indicator style from subprocess status string
  function statusColor(s: string): string {
    if (s === 'running') return 'bg-success-500'
    if (s === 'starting' || s === 'stopping') return 'bg-warning-500'
    if (s === 'error' || s === 'crashed') return 'bg-error-500'
    return 'bg-surface-300 dark:bg-surface-600'
  }

  function statusLabel(s: string): string {
    return s.charAt(0).toUpperCase() + s.slice(1)
  }
</script>

{#if isOpen}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
    onclick={handleBackdropClick}
    role="dialog"
    aria-modal="true"
  >
    <div class="card bg-surface-100 dark:bg-surface-800 w-full max-w-3xl p-6 space-y-6">

      <!-- Header -->
      <div class="flex justify-between items-center">
        <h2 class="h2">Renardo Runtime</h2>
        <button
          class="btn variant-ghost w-8 h-8 p-0 rounded-full"
          onclick={handleClose}
          aria-label="Close"
        >
          ✕
        </button>
      </div>

      <!-- Error Alert -->
      {#if $error}
        <div class="alert variant-filled-error">
          <span>{$error}</span>
          <button onclick={() => actions.clearError()}>✕</button>
        </div>
      {/if}

      <!-- Status & Controls -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">

        <!-- Left: Controls + meta -->
        <div class="lg:col-span-2">
          <div class="card bg-surface-100 dark:bg-surface-800 shadow-xl h-full p-4 space-y-4">

            <!-- Meta info -->
            <div class="space-y-1 text-sm">
              <div>
                <span class="opacity-60">Status: </span>
                <span class="font-semibold">{statusLabel($status.status)}</span>
              </div>
              {#if $status.pid !== null}
                <div>
                  <span class="opacity-60">PID: </span>
                  <span class="font-mono">{$status.pid}</span>
                </div>
              {/if}
            </div>

            <!-- Action Buttons -->
            <div class="flex gap-2">
              <button
                class="btn variant-filled-primary flex-1"
                onclick={() => actions.startRuntime()}
                disabled={$isLoading || $status.running || !isOpen}
              >
                {#if $isLoading && !$status.running}
                  <span class="animate-spin">⏳</span>
                {:else}
                  ▶
                {/if}
                Start
              </button>

              <button
                class="btn variant-filled-error flex-1"
                onclick={() => actions.stopRuntime()}
                disabled={$isLoading || !$status.running || !isOpen}
              >
                {#if $isLoading && $status.running}
                  <span class="animate-spin">⏳</span>
                {:else}
                  ⏹
                {/if}
                Stop
              </button>

              <button
                class="btn variant-filled-warning flex-1"
                onclick={() => actions.restartRuntime()}
                disabled={$isLoading || !isOpen}
              >
                {#if $isLoading}
                  <span class="animate-spin">⏳</span>
                {:else}
                  🔄
                {/if}
                Restart
              </button>
            </div>

            <p class="text-xs opacity-60">
              Le runtime tourne dans un subprocess isolé. Start charge <code>renardo.runtime</code> et démarre le Clock.
            </p>
          </div>
        </div>

        <!-- Right: Status Indicator -->
        <div class="card bg-surface-100 dark:bg-surface-800 shadow-xl">
          <div class="card-body flex flex-col items-center justify-center gap-3 p-4">
            {#if $status.running}
              <span class="relative flex h-16 w-16">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-success-500 opacity-75"></span>
                <span class="relative inline-flex rounded-full h-16 w-16 bg-success-500"></span>
              </span>
              <p class="text-success-500 font-bold text-center">Running</p>
            {:else if $status.status === 'starting' || $status.status === 'stopping'}
              <span class="relative flex h-16 w-16">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-warning-500 opacity-75"></span>
                <span class="relative inline-flex rounded-full h-16 w-16 bg-warning-500"></span>
              </span>
              <p class="text-warning-500 font-bold text-center">{statusLabel($status.status)}</p>
            {:else if $status.status === 'error' || $status.status === 'crashed'}
              <span class="relative inline-flex rounded-full h-16 w-16 bg-error-500"></span>
              <p class="text-error-500 font-bold text-center">{statusLabel($status.status)}</p>
            {:else}
              <span class="relative inline-flex rounded-full h-16 w-16 bg-surface-300 dark:bg-surface-600"></span>
              <p class="text-surface-500 font-bold text-center">Stopped</p>
            {/if}
          </div>
        </div>
      </div>

      <!-- Runtime Logs Console -->
      <div class="card bg-surface-100 dark:bg-surface-800 shadow-xl">
        <div class="card-body p-0">
          <div class="bg-surface-200 dark:bg-surface-900 rounded-lg p-4 h-[260px] overflow-y-auto font-mono text-sm">
            {#if $runtimeLogs.length === 0}
              <div class="flex justify-center items-center h-full">
                <p class="opacity-50 italic">No runtime log messages yet</p>
              </div>
            {:else}
              {#each $runtimeLogs as log}
                <div class="mb-1 text-{log.level === 'error' ? 'error' : log.level === 'warn' ? 'warning' : 'info'}-500">
                  <span class="opacity-70 mr-2">[{log.timestamp.toLocaleTimeString()}]</span>
                  <span class="font-bold mr-2">[{log.level.toUpperCase()}]</span>
                  <span>{log.message}</span>
                </div>
              {/each}
            {/if}
          </div>
        </div>
      </div>

    </div>
  </div>
{/if}
