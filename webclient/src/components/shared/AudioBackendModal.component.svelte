<script lang="ts">
  import { useAudioBackendStore } from '../../store/audio-backend/AudioBackend.store'
  import { useAbletonStore } from '../../store/ableton/Ableton.store'
  import { useI18nStore } from '../../store/i18n/I18n.store'

  let {
    isOpen = false,
    onclose
  }: {
    isOpen?: boolean
    onclose?: () => void
  } = $props()

  // ── SuperCollider store ──────────────────────────────────────────────
  const { actions, getters } = useAudioBackendStore()
  const { getters: i18nGetters } = useI18nStore()
  const { translate } = i18nGetters

  const {
    status,
    devices,
    selectedDeviceIndex,
    isLoading,
    error,
    showDeviceSelector,
    scLogs,
    channels
  } = getters

  let numOutputChannels = $state(8)
  let numInputChannels = $state(8)

  $effect(() => {
    if ($channels) {
      numOutputChannels = $channels.numOutputChannels
      numInputChannels = $channels.numInputChannels
    }
  })

  // ── Ableton store ────────────────────────────────────────────────────
  const { actions: ablActions, getters: ablGetters } = useAbletonStore()
  const { status: abletonStatus, startupEnabled, isLoading: ablLoading, error: ablError } = ablGetters

  // ── Tab state ────────────────────────────────────────────────────────
  let activeTab = $state<'sc' | 'ableton'>('sc')

  // ── Load data on open ────────────────────────────────────────────────
  $effect(() => {
    if (isOpen) {
      actions.loadStatus()
      actions.loadAudioDevices()
      actions.loadChannels()
      ablActions.loadStatus()
      ablActions.loadStartupEnabled()
    }
  })

  // ── SC handlers ──────────────────────────────────────────────────────
  function handleClose() { onclose?.() }
  function handleBackdropClick(e: MouseEvent) {
    if (e.target === e.currentTarget) handleClose()
  }
  async function handleStart() { await actions.startBackend($selectedDeviceIndex) }
  async function handleStop() { await actions.stopRenardoOnly() }
  async function handleStopAll() { await actions.stopBackend() }
  async function handleDeviceChange(e: Event) {
    const index = parseInt((e.target as HTMLSelectElement).value)
    await actions.setAudioDevice(index)
  }
  async function handleLaunchIDE() { await actions.launchIDE() }
  async function handleChannelsChange() {
    await actions.setChannels(numOutputChannels, numInputChannels)
  }
  async function handleReconfigure() { await actions.reconfigureBackend() }

  // ── Ableton handlers ─────────────────────────────────────────────────
  async function handleAbletonStart() { await ablActions.start() }
  async function handleAbletonStop() { await ablActions.stop() }
  async function handleAbletonRestart() { await ablActions.restart() }
  async function handleStartupToggle() {
    await ablActions.setStartupEnabled(!$startupEnabled)
  }
</script>

{#if isOpen}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
    onclick={handleBackdropClick}
    role="dialog"
    aria-modal="true"
  >
    <div class="card bg-surface-100 dark:bg-surface-800 w-full max-w-4xl p-6 space-y-4">

      <!-- Header -->
      <div class="flex justify-between items-center">
        <h2 class="h2">Audio Backend</h2>
        <button
          class="btn variant-ghost w-8 h-8 p-0 rounded-full"
          onclick={handleClose}
          aria-label="Close"
        >✕</button>
      </div>

      <!-- Tab bar -->
      <div class="flex border-b border-surface-300 dark:border-surface-600">
        <button
          class="px-5 py-2 text-sm font-medium transition-colors {activeTab === 'sc'
            ? 'border-b-2 border-primary-500 text-primary-500'
            : 'text-surface-500 hover:text-surface-900 dark:hover:text-surface-50'}"
          onclick={() => (activeTab = 'sc')}
        >
          SuperCollider
        </button>
        <button
          class="px-5 py-2 text-sm font-medium transition-colors {activeTab === 'ableton'
            ? 'border-b-2 border-primary-500 text-primary-500'
            : 'text-surface-500 hover:text-surface-900 dark:hover:text-surface-50'}"
          onclick={() => (activeTab = 'ableton')}
        >
          Ableton
        </button>
      </div>

      <!-- ══════════════════ SuperCollider tab ══════════════════ -->
      {#if activeTab === 'sc'}

        {#if $error}
          <div class="alert variant-filled-error">
            <span>{$error}</span>
            <button onclick={() => actions.clearError()}>✕</button>
          </div>
        {/if}

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <!-- Controls -->
          <div class="lg:col-span-2">
            <div class="card bg-surface-100 dark:bg-surface-800 shadow-xl h-full p-4 space-y-4">

              {#if $showDeviceSelector && $devices}
                <div>
                  <label class="label"><span>Audio Output Device</span></label>
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

              <div class="space-y-3">
                <h3 class="h4">Bus Channels Configuration</h3>
                <div class="grid grid-cols-2 gap-3">
                  <div>
                    <label class="label"><span>Output Channels</span></label>
                    <input type="number" class="input variant-form-material" min="2" max="128"
                      bind:value={numOutputChannels} disabled={$isLoading || !isOpen} />
                  </div>
                  <div>
                    <label class="label"><span>Input Channels</span></label>
                    <input type="number" class="input variant-form-material" min="2" max="128"
                      bind:value={numInputChannels} disabled={$isLoading || !isOpen} />
                  </div>
                </div>
                <div class="flex gap-2">
                  <button class="btn variant-filled-secondary flex-1"
                    onclick={handleChannelsChange} disabled={$isLoading || !isOpen}>
                    💾 Save Channels
                  </button>
                  <button class="btn variant-filled-warning flex-1"
                    onclick={handleReconfigure} disabled={$isLoading || !isOpen}>
                    {#if $isLoading}<span class="animate-spin">⏳</span>{:else}🔄{/if}
                    Reconfigure Backend
                  </button>
                </div>
                <p class="text-xs opacity-70">
                  ℹ️ Changes require backend restart. Use "Reconfigure Backend" to apply automatically.
                </p>
              </div>

              <div class="flex gap-2">
                <button class="btn variant-filled-primary flex-1"
                  onclick={handleStart} disabled={$isLoading || $status.running || !isOpen}>
                  {#if $isLoading && !$status.running}<span class="animate-spin">⏳</span>{:else}▶{/if}
                  Start
                </button>
                <button class="btn variant-filled-error flex-1"
                  onclick={handleStop} disabled={$isLoading || !$status.running || !isOpen}
                  title="Stop only the sclang process Renardo started (by PID)">
                  {#if $isLoading && $status.running}<span class="animate-spin">⏳</span>{:else}⏹{/if}
                  Stop
                </button>
              </div>

              <button class="btn variant-outline-error w-full text-sm"
                onclick={handleStopAll} disabled={$isLoading || !isOpen}
                title="Kill all sclang and scsynth processes on this machine">
                ☠ Stop All SuperCollider Processes
              </button>

              <button class="btn variant-outline w-full"
                onclick={handleLaunchIDE} disabled={$isLoading || !isOpen}>
                🎹 Launch SuperCollider IDE
              </button>
            </div>
          </div>

          <!-- Status pastille -->
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

        <!-- Logs -->
        <div class="card bg-surface-100 dark:bg-surface-800 shadow-xl">
          <div class="card-body p-0">
            <div class="bg-surface-200 dark:bg-surface-900 rounded-lg p-4 h-[220px] overflow-y-auto font-mono text-sm">
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

        <details class="collapse bg-surface-200 dark:bg-surface-700 rounded-lg">
          <summary class="collapse-title text-sm font-medium cursor-pointer">
            ℹ️ Manual Setup Instructions
          </summary>
          <div class="collapse-content p-4 bg-surface-100 dark:bg-surface-800">
            <p class="mb-2">If automatic initialization fails, start SuperCollider backend manually:</p>
            <ol class="list-decimal list-inside space-y-2">
              <li>Launch SuperCollider IDE using the button above</li>
              <li>In SC IDE, execute the following code (Ctrl+Enter):</li>
            </ol>
            <div class="bg-surface-200 dark:bg-surface-900 p-2 rounded mt-2 font-mono text-sm">
              {#if $showDeviceSelector}
                <div>Renardo.listAudioDevices()</div>
                <div>Renardo.start(audio_output_index: -1)</div>
              {:else}
                <div>Renardo.start()</div>
              {/if}
              <div>Renardo.midi()</div>
            </div>
          </div>
        </details>

      {/if}

      <!-- ══════════════════ Ableton tab ══════════════════ -->
      {#if activeTab === 'ableton'}

        {#if $ablError}
          <div class="alert variant-filled-error">
            <span>{$ablError}</span>
            <button onclick={() => ablActions.clearError()}>✕</button>
          </div>
        {/if}

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <!-- Controls -->
          <div class="lg:col-span-2">
            <div class="card bg-surface-100 dark:bg-surface-800 shadow-xl h-full p-4 space-y-4">

              <p class="text-sm opacity-70">
                Scans Ableton Live tracks via the OSC/Live API, creates a
                <code class="font-mono">Player</code> instance for each track, and binds
                each one to a global variable named after the track. Bus/audio tracks are
                included — they just won't play notes.
              </p>

              <!-- Enable at startup toggle -->
              <label class="flex items-center gap-3 cursor-pointer select-none">
                <input
                  type="checkbox"
                  class="checkbox"
                  checked={$startupEnabled}
                  onchange={handleStartupToggle}
                />
                <span class="text-sm">Enable Ableton backend at startup</span>
              </label>

              <!-- Action buttons -->
              <div class="flex gap-2">
                <button
                  class="btn variant-filled-primary flex-1"
                  onclick={handleAbletonStart}
                  disabled={$ablLoading || $abletonStatus.status === 'running' || !isOpen}
                >
                  {#if $ablLoading && $abletonStatus.status !== 'running'}
                    <span class="animate-spin">⏳</span>
                  {:else}
                    ▶
                  {/if}
                  Start
                </button>

                <button
                  class="btn variant-filled-warning flex-1"
                  onclick={handleAbletonRestart}
                  disabled={$ablLoading || !isOpen}
                >
                  {#if $ablLoading}<span class="animate-spin">⏳</span>{:else}🔄{/if}
                  Restart
                </button>

                <button
                  class="btn variant-filled-error flex-1"
                  onclick={handleAbletonStop}
                  disabled={$ablLoading || $abletonStatus.status === 'stopped' || !isOpen}
                >
                  {#if $ablLoading && $abletonStatus.status !== 'stopped'}
                    <span class="animate-spin">⏳</span>
                  {:else}
                    ⏹
                  {/if}
                  Stop
                </button>
              </div>

              <p class="text-xs opacity-60">
                Stop clears <code class="font-mono">ableton_instruments</code> and all
                per-track global variables from the runtime.
              </p>
            </div>
          </div>

          <!-- Status pastille -->
          <div class="card bg-surface-100 dark:bg-surface-800 shadow-xl">
            <div class="card-body flex flex-col items-center justify-center p-4 gap-3">
              {#if $abletonStatus.status === 'running'}
                <div class="text-center">
                  <div class="relative mb-3">
                    <span class="relative flex h-16 w-16">
                      <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-success-500 opacity-75"></span>
                      <span class="relative inline-flex rounded-full h-16 w-16 bg-success-500"></span>
                    </span>
                  </div>
                  <p class="text-success-500 font-bold">Running</p>
                </div>
              {:else if $abletonStatus.status === 'error'}
                <div class="text-center">
                  <div class="relative mb-3">
                    <span class="relative inline-flex rounded-full h-16 w-16 bg-error-500"></span>
                  </div>
                  <p class="text-error-500 font-bold">Error</p>
                </div>
              {:else}
                <div class="text-center">
                  <div class="relative mb-3">
                    <span class="relative inline-flex rounded-full h-16 w-16 bg-surface-300 dark:bg-surface-600"></span>
                  </div>
                  <p class="text-surface-500 font-bold">Stopped</p>
                </div>
              {/if}
              <p class="text-xs opacity-60 text-center">{$abletonStatus.message}</p>
            </div>
          </div>
        </div>

      {/if}

    </div>
  </div>
{/if}
