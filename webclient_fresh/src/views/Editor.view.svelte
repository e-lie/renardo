<script lang="ts">
  import EditorTabs from '../components/editor/EditorTabs.component.svelte';
  import CodeEditor from '../components/editor/CodeEditor.component.svelte';
  import SettingsModal from '../components/shared/SettingsModal.component.svelte';
  import { useEditorStore } from '../store/editor';
  import { logger } from '../services/logger.service';

  const { actions, getters } = useEditorStore();
  const { activeTab, activeBuffer, tabs, buffers } = getters;

  let isSettingsOpen = $state(false);

  function toggleSettings() {
    isSettingsOpen = !isSettingsOpen;
  }

  // Initialize with startup buffer on mount
  $effect(() => {
    logger.debug('Editor', 'Editor view effect triggered');
    // Check if we already have a startup buffer
    const currentBuffers = $buffers;
    const hasStartup = currentBuffers.some((b) => b.isStartupFile);

    if (!hasStartup) {
      logger.info('Editor', 'Creating startup buffer');
      // Create startup buffer
      const bufferId = actions.createBuffer({
        name: 'startup.py',
        content: '# Renardo startup file\n# This code runs when Renardo starts\n\n',
        isStartupFile: true,
        language: 'python',
      });

      // Create tab for startup buffer
      actions.createTab(bufferId, 'startup.py');
    } else {
      logger.debug('Editor', 'Startup buffer already exists');
    }
  });

  function handleSwitchTab(tabId: string) {
    logger.debug('Editor', 'Switching tab', { tabId });
    actions.switchToTab(tabId);
  }

  function handleCloseTab(tabId: string) {
    logger.debug('Editor', 'Closing tab', { tabId });
    actions.closeTab(tabId);
  }

  function handleCreateTab() {
    logger.debug('Editor', 'Creating new tab');
    // Create new buffer
    const bufferId = actions.createBuffer({
      name: `Untitled-${Date.now()}`,
      content: '',
      language: 'python',
    });

    // Create tab for the buffer
    actions.createTab(bufferId);
  }

  function handleContentChange(content: string) {
    if ($activeBuffer) {
      logger.debug('Editor', 'Content changed', {
        bufferId: $activeBuffer.id,
        contentLength: content.length,
      });
      actions.updateBufferContent($activeBuffer.id, content);
    }
  }

  async function handleExecuteCode(code: string) {
    logger.info('Editor', 'Executing code', { codeLength: code.length });
    const result = await actions.executeCode(code);

    if (result.success) {
      logger.info('Editor', 'Code executed successfully', { message: result.message });
    } else {
      logger.error('Editor', 'Code execution failed', { message: result.message });
    }
  }
</script>

<div class="flex flex-col h-screen relative">
  <!-- Floating Settings Button -->
  <button
    class="btn btn-circle btn-primary fixed top-4 right-4 z-40 shadow-lg"
    onclick={toggleSettings}
    aria-label="Settings"
  >
    <svg
      xmlns="http://www.w3.org/2000/svg"
      class="h-6 w-6"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
    >
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
        d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
      />
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
        d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
      />
    </svg>
  </button>

  <!-- Settings Modal -->
  <SettingsModal isOpen={isSettingsOpen} onclose={toggleSettings} />

  <!-- Tabs -->
  <EditorTabs
    tabs={$tabs}
    buffers={$buffers}
    onswitch={handleSwitchTab}
    onclose={handleCloseTab}
    oncreate={handleCreateTab}
  />

  <!-- Editor -->
  <div class="flex-1 overflow-hidden">
    <CodeEditor
      buffer={$activeBuffer}
      onchange={handleContentChange}
      onexecute={handleExecuteCode}
    />
  </div>
</div>
