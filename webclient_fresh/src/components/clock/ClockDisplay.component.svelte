<script lang="ts">
  import { useAppStore } from '../../store/root/Root.store'
  import { onMount, onDestroy } from 'svelte'

  let {
    componentId = 'clock-display',
    title = 'Clock'
  }: {
    componentId?: string
    title?: string
  } = $props()

  const appStore = useAppStore()
  const { connectionStatus } = appStore.webSocketBackendStore.getters

  // État de l'horloge
  let clockState = $state({
    current_beat: 1,
    measure_size: 4,
    bpm: 120,
    ticking: false
  })

  // Écouter les messages WebSocket
  function handleMessage(event: MessageEvent) {
    try {
      const data = JSON.parse(event.data)
      if (data.type === 'clock_update') {
        clockState = data.data
      }
    } catch (e) {
      // Ignore parsing errors
    }
  }

  onMount(() => {
    window.addEventListener('message', handleMessage)

    // Charger l'état initial
    fetch('http://localhost:8000/api/clock/state')
      .then(r => r.json())
      .then(data => {
        clockState = data
      })
      .catch(e => console.error('Failed to load initial clock state:', e))
  })

  onDestroy(() => {
    window.removeEventListener('message', handleMessage)
  })

  // Actions
  async function setMeasureSize(size: number) {
    try {
      const response = await fetch(`http://localhost:8000/api/clock/set-measure-size?size=${size}`, { method: 'POST' })
      const data = await response.json()
      if (data.success) {
        console.log('Measure size set:', data)
      }
    } catch (e) {
      console.error('Failed to set measure size:', e)
    }
  }

  async function reset() {
    try {
      const response = await fetch('http://localhost:8000/api/clock/reset', { method: 'POST' })
      const data = await response.json()
      if (data.success) {
        console.log('Reset:', data)
      }
    } catch (e) {
      console.error('Failed to reset:', e)
    }
  }
</script>

<div class="h-full flex flex-col p-4 bg-surface-100 dark:bg-surface-900">
  <!-- Header -->
  <div class="mb-4 pb-2 border-b border-surface-300 dark:border-surface-700">
    <h2 class="text-lg font-semibold">{title}</h2>
    <div class="flex items-center gap-2 mt-1">
      <div class="w-2 h-2 rounded-full {$connectionStatus === 'connected' ? 'bg-success-500' : 'bg-error-500'}"></div>
      <span class="text-xs text-surface-500">{$connectionStatus}</span>
    </div>
  </div>

  <!-- Clock Display -->
  <div class="flex-1 flex flex-col justify-center items-center gap-8">
    <!-- Beat Display: 1/4, 2/4, 3/4, 4/4 -->
    <div class="text-center">
      <div class="text-8xl font-bold text-primary-500 font-mono">
        {clockState.current_beat}/{clockState.measure_size}
      </div>
      <div class="text-sm text-surface-500 uppercase tracking-wide mt-2">Current Beat</div>
    </div>

    <!-- BPM -->
    <div class="text-center">
      <div class="text-3xl font-semibold">{clockState.bpm} BPM</div>
    </div>

    <!-- Status -->
    <div class="flex items-center gap-2">
      {#if clockState.ticking}
        <div class="w-3 h-3 rounded-full bg-success-500 animate-pulse"></div>
        <span class="text-sm text-success-500">Ticking</span>
      {:else}
        <div class="w-3 h-3 rounded-full bg-surface-400"></div>
        <span class="text-sm text-surface-500">Idle</span>
      {/if}
    </div>
  </div>

  <!-- Controls -->
  <div class="mt-auto pt-4 border-t border-surface-300 dark:border-surface-700 space-y-3">
    <!-- Measure Size -->
    <div class="flex gap-2">
      <button
        class="flex-1 btn variant-ghost text-xs"
        onclick={() => setMeasureSize(3)}
        class:variant-filled-secondary={clockState.measure_size === 3}
      >
        3/4
      </button>
      <button
        class="flex-1 btn variant-ghost text-xs"
        onclick={() => setMeasureSize(4)}
        class:variant-filled-secondary={clockState.measure_size === 4}
      >
        4/4
      </button>
      <button
        class="flex-1 btn variant-ghost text-xs"
        onclick={() => setMeasureSize(5)}
        class:variant-filled-secondary={clockState.measure_size === 5}
      >
        5/4
      </button>
      <button
        class="flex-1 btn variant-ghost text-xs"
        onclick={() => setMeasureSize(6)}
        class:variant-filled-secondary={clockState.measure_size === 6}
      >
        6/4
      </button>
    </div>

    <!-- Reset -->
    <button
      class="w-full btn variant-ghost-surface text-xs"
      onclick={reset}
    >
      Reset
    </button>
  </div>
</div>
