<script lang="ts">
  import EditorTabs from '../components/editor/EditorTabs.component.svelte';
  import CodeEditor from '../components/editor/CodeEditor.component.svelte';
  import SettingsModal from '../components/shared/SettingsModal.component.svelte';
  import { ElConfirmModal } from '../components/primitives';
  import { useEditorStore } from '../store/editor';
  import { useI18nStore } from '../store/i18n/I18n.store';
  import { logger } from '../services/logger.service';

  const { actions, getters } = useEditorStore();
  const { activeTab, activeBuffer, tabs, buffers } = getters;

  const { getters: i18nGetters } = useI18nStore();
  const { translate } = i18nGetters;

  let isSettingsOpen = $state(false);
  let showConfirmClose = $state(false);
  let pendingCloseTabId = $state<string | null>(null);

  function toggleSettings() {
    isSettingsOpen = !isSettingsOpen;
  }

  // Initialize with at least one tab
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

  function handleSwitchTab(tabId: string) {
    logger.debug('Editor', 'Switching tab', { tabId });
    actions.switchToTab(tabId);
  }

  function handleCloseTab(tabId: string) {
    logger.debug('Editor.view', 'handleCloseTab called', { tabId });

    // Find the tab and its buffer
    const tab = $tabs.find(t => t.id === tabId);
    logger.debug('Editor.view', 'Found tab', { tab });
    if (!tab) {
      logger.warn('Editor.view', 'Tab not found, returning');
      return;
    }

    const buffer = $buffers.find(b => b.id === tab.bufferId);
    logger.debug('Editor.view', 'Found buffer for closing tab', { bufferId: buffer?.id, isDirty: buffer?.isDirty });

    if (buffer?.isDirty) {
      logger.debug('Editor.view', 'Buffer is dirty, showing confirmation modal');
      pendingCloseTabId = tabId;
      showConfirmClose = true;
      logger.debug('Editor.view', 'showConfirmClose set to', { showConfirmClose });
    } else {
      logger.debug('Editor.view', 'Buffer is clean, closing directly');
      actions.closeTab(tabId);
    }
  }

  function handleConfirmClose() {
    if (pendingCloseTabId) {
      logger.debug('Editor', 'Confirmed close', { tabId: pendingCloseTabId });
      actions.closeTab(pendingCloseTabId);
    }
    showConfirmClose = false;
    pendingCloseTabId = null;
  }

  function handleCancelClose() {
    logger.debug('Editor', 'Cancelled close');
    showConfirmClose = false;
    pendingCloseTabId = null;
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


  <!-- Settings Modal -->
  <SettingsModal isOpen={isSettingsOpen} onclose={toggleSettings} />

  <!-- Confirm Close Modal -->
  <ElConfirmModal
    isOpen={showConfirmClose}
    title={$translate('unsavedChanges')}
    message={$translate('unsavedChangesMessage')}
    confirmText={$translate('close')}
    cancelText={$translate('cancel')}
    variant="warning"
    onconfirm={handleConfirmClose}
    oncancel={handleCancelClose}
  />

  <!-- Tabs -->
  <EditorTabs
    tabs={$tabs}
    buffers={$buffers}
    onswitch={handleSwitchTab}
    onclose={handleCloseTab}
    oncreate={handleCreateTab}
    onsettings={toggleSettings}
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
