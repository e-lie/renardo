<script lang="ts">
  import EditorTabs from '../components/editor/EditorTabs.component.svelte';
  import CodeEditor from '../components/editor/CodeEditor.component.svelte';
  import { useEditorStore } from '../store/editor';
  import { logger } from '../services/logger.service';

  const { actions, getters } = useEditorStore();
  const { activeTab, activeBuffer, tabs, buffers } = getters;

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

<div class="flex flex-col h-screen">
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
