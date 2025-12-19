<script lang="ts">
  import { useEditorStore } from '../../../store/editor'
  import SettingsModal from '../../shared/SettingsModal.component.svelte'

  let {
    componentId,
    title = 'Top Menu'
  }: {
    componentId: string
    title?: string
  } = $props()

  const { getters, actions } = useEditorStore()
  const { settings } = getters

  let showSettings = $state(false)

  function toggleSettings() {
    showSettings = !showSettings
  }
</script>

<div class="h-full flex items-center justify-between px-4 bg-surface-200 dark:bg-surface-800">
  <div class="text-lg font-bold text-surface-900 dark:text-surface-50">
    Renardo
  </div>

  <button
    class="btn variant-filled-primary"
    onclick={toggleSettings}
  >
    Settings
  </button>
</div>

<SettingsModal isOpen={showSettings} onclose={() => showSettings = false} />
