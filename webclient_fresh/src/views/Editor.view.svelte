<script lang="ts">
  import LayoutGrid from '../components/layout/LayoutGrid.component.svelte';
  import SettingsModal from '../components/shared/SettingsModal.component.svelte';
  import EditorTabs from '../components/editor/EditorTabs.component.svelte';
  import { LayoutManager } from '../lib/layout/LayoutManager';
  import { useEditorStore } from '../store/editor';
  import { logger } from '../services/logger.service';

  const { actions, getters } = useEditorStore();
  const { tabs, buffers, activeBuffer } = getters;

  let layoutManager = $state(new LayoutManager());
  let isSettingsOpen = $state(false);

  function toggleSettings() {
    isSettingsOpen = !isSettingsOpen;
  }

  // Code execution functions
  function executeCode() {
    if ($activeBuffer) {
      actions.executeCode($activeBuffer.content);
    }
  }

  function executeCurrentLine() {
    if ($activeBuffer) {
      // TODO: Implement current line execution
      logger.info('Editor', 'Executing current line');
    }
  }

  function executeAllCode() {
    if ($activeBuffer) {
      actions.executeCode($activeBuffer.content);
    }
  }

  function stopMusic() {
    // TODO: Implement stop music functionality
    logger.info('Editor', 'Stopping music');
  }

  // Tab management
  function handleSwitchTab(tabId: string) {
    actions.switchToTab(tabId);
  }

  function handleCloseTab(tabId: string) {
    actions.closeTab(tabId);
  }

  function handleCreateTab() {
    const bufferId = actions.createBuffer({
      name: 'Untitled',
      content: '',
      language: 'python',
    });
    actions.createTab(bufferId);
  }

  // Keyboard shortcuts
  $effect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      // Ctrl+. or Cmd+. to stop music
      if ((e.ctrlKey || e.metaKey) && e.key === '.') {
        e.preventDefault();
        stopMusic();
        return;
      }
      
      // Ctrl+Enter or Cmd+Enter to execute paragraph/selection
      if ((e.ctrlKey || e.metaKey) && !e.altKey && e.key === 'Enter') {
        e.preventDefault();
        executeCode();
        return;
      }
      
      // Alt+Enter to execute current line
      if (e.altKey && e.key === 'Enter' && !(e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        executeCurrentLine();
        return;
      }
    }

    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  });

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
  <!-- Top Action Bar -->
  <div class="bg-base-300 p-3 flex items-center justify-between border-b border-base-300" style="height: 60px; flex-shrink: 0;">
    <!-- Action Buttons -->
    <div class="flex gap-2">
      <button
        class="btn btn-sm btn-success"
        onclick={executeAllCode}
        title="Run all code in editor"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd" />
        </svg>
        Run Code
      </button>

      <button
        class="btn btn-sm btn-warning"
        onclick={stopMusic}
        title="Stop all music playback"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clip-rule="evenodd" />
        </svg>
        Stop Music
      </button>
    </div>
    
    <!-- Right Side: Keyboard Shortcuts -->
    <div class="flex flex-wrap gap-2 text-xs">
      <span class="badge badge-sm">Alt+Enter: Run current line</span>
      <span class="badge badge-sm">Ctrl+Enter: Run paragraph/selection</span>
      <span class="badge badge-sm">Ctrl+.: Stop music</span>
      <span class="badge badge-sm">Run Code: Execute all</span>
    </div>
  </div>

  <!-- Settings Modal -->
  <SettingsModal
    isOpen={isSettingsOpen}
    onclose={toggleSettings}
    {layoutManager}
  />

  <!-- Floating Settings Button -->
  <button 
    class="fixed top-4 right-4 btn btn-circle btn-primary shadow-lg z-50"
    onclick={toggleSettings}
    title="Configure Layout"
  >
    <!-- Window Icon SVG -->
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
      <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z" />
    </svg>
  </button>

  <!-- Layout Grid -->
  <LayoutGrid 
    {layoutManager} 
    tabs={$tabs} 
    buffers={$buffers} 
    onswitch={handleSwitchTab}
    onclose={handleCloseTab}
    oncreate={handleCreateTab}
    onsettings={toggleSettings}
    activeBuffer={$activeBuffer}
  />
</div>
