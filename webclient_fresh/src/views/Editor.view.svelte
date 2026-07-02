<script lang="ts">
  import LayoutGrid from '../components/layout/LayoutGrid.component.svelte'
  import SettingsModal from '../components/shared/SettingsModal.component.svelte'

  let isSettingsOpen = $state(false)

  function toggleSettings() {
    isSettingsOpen = !isSettingsOpen
  }
</script>

<div class="flex flex-col h-screen relative">
  <!-- Settings Modal -->
  <SettingsModal
    isOpen={isSettingsOpen}
    onclose={toggleSettings}
  />

  <!-- Layout Grid -->
  <LayoutGrid />
</div>