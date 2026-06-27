<script lang="ts">
  import { useAppStore } from '../../store/root/Root.store'

  let {
    componentId = 'clock-display',
    title = 'Clock'
  }: {
    componentId?: string
    title?: string
  } = $props()

  const appStore = useAppStore()
  const { clockState } = appStore.webSocketBackendStore.getters

  // Actions
  async function setMeasureSize(size: number) {
    try {
      await fetch(`http://localhost:8000/api/clock/set-measure-size?size=${size}`, { method: 'POST' })
    } catch (e) {
      console.error('Failed to set measure size:', e)
    }
  }

  async function reset() {
    try {
      await fetch('http://localhost:8000/api/clock/reset', { method: 'POST' })
    } catch (e) {
      console.error('Failed to reset:', e)
    }
  }
</script>

<div class="h-full flex flex-col justify-center items-center bg-surface-100 dark:bg-surface-900">
  <!-- Beat Display -->
  <div class="text-6xl font-bold text-primary-500 font-mono">
    {$clockState.current_beat}/{$clockState.measure_size}
  </div>

  <!-- BPM -->
  <div class="text-sm text-surface-500 mt-2">
    {$clockState.bpm} BPM
  </div>
</div>
