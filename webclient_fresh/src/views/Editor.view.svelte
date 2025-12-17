<script lang="ts">
  import LayoutGrid from '../components/layout/LayoutGrid.component.svelte';
  import SettingsModal from '../components/shared/SettingsModal.component.svelte';
  import { LayoutManager } from '../lib/layout/LayoutManager';
  import { useEditorStore } from '../store/editor';
  import { logger } from '../services/logger.service';

  const { actions, getters } = useEditorStore();
  const { tabs } = getters;

  let layoutManager = $state(new LayoutManager());
  let isSettingsOpen = $state(false);

  function toggleSettings() {
    isSettingsOpen = !isSettingsOpen;
  }

  // Initialize with at least one tab in EditorStore
  $effect(() => {
    const currentTabs = $tabs;
    if (currentTabs.length === 0) {
      logger.info('Editor', 'Creating initial tab');
      const bufferId = actions.createBuffer({
        name: 'Untitled',
        content: '',
        language: 'python',
      });
      actions.createTab(bufferId);
    }
  });
</script>

<div class="flex flex-col h-screen relative">
  <!-- Settings Modal -->
  <SettingsModal
    isOpen={isSettingsOpen}
    onclose={toggleSettings}
    {layoutManager}
  />

  <!-- Layout Grid -->
  <LayoutGrid {layoutManager} />
</div>
