<script lang="ts">
  import EditorTabs from '../components/editor/EditorTabs.component.svelte';
  import CodeEditor from '../components/editor/CodeEditor.component.svelte';
  import { useEditorStore } from '../store/editor';

  const { actions, getters } = useEditorStore();
  const { activeTab, activeBuffer, tabs, buffers } = getters;

  // Initialize with startup buffer on mount
  $effect(() => {
    // Check if we already have a startup buffer
    const currentBuffers = $buffers;
    const hasStartup = currentBuffers.some((b) => b.isStartupFile);

    if (!hasStartup) {
      // Create startup buffer
      const bufferId = actions.createBuffer({
        name: 'startup.py',
        content: '# Renardo startup file\n# This code runs when Renardo starts\n\n',
        isStartupFile: true,
        language: 'python',
      });

      // Create tab for startup buffer
      actions.createTab(bufferId, 'startup.py');
    }
  });

  function handleSwitchTab(tabId: string) {
    actions.switchToTab(tabId);
  }

  function handleCloseTab(tabId: string) {
    actions.closeTab(tabId);
  }

  function handleCreateTab() {
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
      actions.updateBufferContent($activeBuffer.id, content);
    }
  }

  async function handleExecuteCode(code: string) {
    const result = await actions.executeCode(code);

    if (result.success) {
      console.log('Code executed successfully:', result.message);
    } else {
      console.error('Code execution failed:', result.message);
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
