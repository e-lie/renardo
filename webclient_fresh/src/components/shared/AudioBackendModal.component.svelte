<script lang="ts">
  import { useAudioBackendStore } from '../../store/audio-backend/AudioBackend.store'
  import { useI18nStore } from '../../store/i18n/I18n.store'

  let {
    isOpen = false,
    onclose
  }: {
    isOpen?: boolean
    onclose?: () => void
  } = $props()

  const { actions, getters } = useAudioBackendStore()
  const { getters: i18nGetters } = useI18nStore()
  const { translate } = i18nGetters

  // Getters
  const {
    status,
    devices,
    selectedDeviceIndex,
    isLoading,
    error,
    showDeviceSelector,
    scLogs
  } = getters

  // Local state
  let showManualSetup = $state(false)

  // Load data on modal open
  $effect(() => {
    if (isOpen) {
      actions.loadStatus()
      actions.loadAudioDevices()
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

  async function handleStart() {
    await actions.startBackend($selectedDeviceIndex)
  }

  async function handleStop() {
    await actions.stopBackend()
  }

  async function handleDeviceChange(e: Event) {
    const target = e.target as HTMLSelectElement
    const index = parseInt(target.value)
    await actions.setAudioDevice(index)
  }

  async function handleLaunchIDE() {
    await actions.launchIDE()
  }
</script>

{#if isOpen}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
    onclick={handleBackdropClick}
    role="dialog"
    aria-modal="true"
  >
    <div class="card variant-glass-surface w-full max-w-4xl p-6 space-y-6">
      <!-- Header -->
      <div class="flex justify-between items-center">
        <h2 class="h2">SuperCollider Backend</h2>
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
        <!-- Left: Controls -->
        <div class="lg:col-span-2">
          <div class="card bg-surface-100 dark:bg-surface-800 shadow-xl h-full p-4 space-y-4">
            <!-- Audio Device Selector (non-Linux) -->
            {#if $showDeviceSelector && $devices}
              <div>
                <label class="label">
                  <span>Audio Output Device</span>
                </label>
                <select
                  class="select variant-form-material w-full"
                  value={$selectedDeviceIndex}
                  onchange={handleDeviceChange}
                  disabled={$isLoading || !isOpen}
                >
                  <option value={-1}>System Default</option>
                  {#each $devices.output as device}
                    <option value={device.index}>{device.index}: {device.name}</option>
                  {/each}
                </select>
              </div>
            {/if}

            <!-- Action Buttons -->
            <div class="flex gap-2">
              <button
                class="btn variant-filled-primary flex-1"
                onclick={handleStart}
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
                onclick={handleStop}
                disabled={$isLoading || !$status.running || !isOpen}
              >
                {#if $isLoading && $status.running}
                  <span class="animate-spin">⏳</span>
                {:else}
                  ⏹
                {/if}
                Stop
              </button>
            </div>

            <!-- Launch IDE Button -->
            <button
              class="btn variant-outline w-full"
              onclick={handleLaunchIDE}
              disabled={$isLoading || !isOpen}
            >
              🎹 Launch SuperCollider IDE
            </button>
          </div>
        </div>

        <!-- Right: Status Indicator -->
        <div class="card bg-surface-100 dark:bg-surface-800 shadow-xl">
          <div class="card-body flex flex-col items-center justify-center p-4">
            {#if $status.running}
              <div class="text-center">
                <div class="relative mb-3">
                  <span class="relative flex h-16 w-16">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-success-500 opacity-75"></span>
                    <span class="relative inline-flex rounded-full h-16 w-16 bg-success-500"></span>
                  </span>
                </div>
                <p class="text-success-500 font-bold">Running</p>
              </div>
            {:else}
              <div class="text-center">
                <div class="relative mb-3">
                  <span class="relative inline-flex rounded-full h-16 w-16 bg-surface-300 dark:bg-surface-600"></span>
                </div>
                <p class="text-surface-500 font-bold">Stopped</p>
              </div>
            {/if}
          </div>
        </div>
      </div>

      <!-- Logs Console -->
      <div class="card bg-surface-100 dark:bg-surface-800 shadow-xl">
        <div class="card-body p-0">
          <div class="bg-surface-200 dark:bg-surface-900 rounded-lg p-4 h-[300px] overflow-y-auto font-mono text-sm">
            {#if $scLogs.length === 0}
              <div class="flex justify-center items-center h-full">
                <p class="opacity-50 italic">No log messages yet</p>
              </div>
            {:else}
              {#each $scLogs as log}
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

      <!-- Manual Setup Collapsed -->
      <details class="collapse bg-surface-200 dark:bg-surface-700 rounded-lg">
        <summary class="collapse-title text-sm font-medium cursor-pointer">
          ℹ️ Manual Setup Instructions
        </summary>
        <div class="collapse-content p-4 bg-surface-100 dark:bg-surface-800">
          <p class="mb-2">
            If automatic initialization fails, you can start SuperCollider backend manually:
          </p>
          <ol class="list-decimal list-inside space-y-2">
            <li>Launch SuperCollider IDE using the button above</li>
            <li>In SC IDE, execute the following code (Ctrl+Enter):</li>
          </ol>
          <div class="bg-surface-200 dark:bg-surface-900 p-2 rounded mt-2 font-mono text-sm">
            {#if $showDeviceSelector}
              <div>Renardo.listAudioDevices()</div>
              <div>Renardo.start(audio_output_index: -1) // -1 for default</div>
            {:else}
              <div>Renardo.start()</div>
            {/if}
            <div>Renardo.midi()</div>
          </div>
        </div>
      </details>
    </div>
  </div>
{/if}
