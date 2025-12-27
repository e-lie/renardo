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

<div class="h-full flex flex-col justify-center items-center bg-surface-100 dark:bg-surface-900">
  <!-- Beat Display -->
  <div class="text-6xl font-bold text-primary-500 font-mono">
    {clockState.current_beat}/{clockState.measure_size}
  </div>

  <!-- BPM -->
  <div class="text-sm text-surface-500 mt-2">
    {clockState.bpm} BPM
  </div>
</div>
