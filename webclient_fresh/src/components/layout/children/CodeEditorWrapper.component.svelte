<script lang="ts">
  import CodeEditor from '../../editor/CodeEditor.component.svelte';
  import SaveFileModal from '../../shared/SaveFileModal.component.svelte';
  import { ElConfirmModal } from '../../primitives';
  import { useEditorStore } from '../../../store/editor';
  import { useProjectStore } from '../../../store/project';
  import { useI18nStore } from '../../../store/i18n/I18n.store';
  import logger from '../../../services/logger.service';
  import { onMount, onDestroy } from 'svelte';

  let {
    componentId = 'code-editor',
    title = 'Code Editor',
  }: {
    componentId?: string;
    title?: string;
  } = $props();

  const { actions, getters } = useEditorStore();
  const { tabs, buffers } = getters;

  const { getters: projectGetters } = useProjectStore();
  const { currentProject } = projectGetters;

  const { getters: i18nGetters } = useI18nStore();
  const { translate } = i18nGetters;

  // Track local tab IDs for this editor instance
  let localTabIds = $state<string[]>([]);
  let activeLocalTabId = $state<string | null>(null);
  let showConfirmClose = $state(false);
  let pendingCloseTabId = $state<string | null>(null);

  // Get active buffer from active local tab
  let activeBuffer = $derived.by(() => {
    if (!activeLocalTabId) return null;
    const tab = $tabs.find((t) => t.id === activeLocalTabId);
    if (!tab) return null;
    return $buffers.find((b) => b.id === tab.bufferId) || null;
  });

  // Get local tabs
  let localTabs = $derived($tabs.filter((t) => localTabIds.includes(t.id)));

  // Create initial buffer for this code editor instance
  $effect(() => {
    if (localTabIds.length === 0) {
      const newBufferId = actions.createBuffer({
        name: title || 'Code Editor',
        content: '',
        language: 'python',
      });
      const newTabId = actions.createTab(newBufferId);
      localTabIds = [newTabId];
      activeLocalTabId = newTabId;
    }
  });

  // Sync new tabs created globally to local tab list
  $effect(() => {
    const allTabIds = $tabs.map(t => t.id);
    const newTabs = allTabIds.filter(id => !localTabIds.includes(id));

    if (newTabs.length > 0) {
      localTabIds = [...localTabIds, ...newTabs];
      // Switch to the newest tab
      const newestTab = $tabs.find(t => t.isActive);
      if (newestTab) {
        activeLocalTabId = newestTab.id;
      }
    }
  });

  function handleChange(value: string) {
    if (activeBuffer) {
      actions.updateBufferContent(activeBuffer.id, value);
    }
  }

  function handleExecute(code: string) {
    actions.executeCode(code);
  }

  function handleCreateTab() {
    const newBufferId = actions.createBuffer({
      name: 'Untitled',
      content: '',
      language: 'python',
    });
    const newTabId = actions.createTab(newBufferId);
    localTabIds = [...localTabIds, newTabId];
    activeLocalTabId = newTabId;
    actions.switchToTab(newTabId);
  }

  function handleSwitchTab(tabId: string) {
    activeLocalTabId = tabId;
    actions.switchToTab(tabId);
  }

  function handleCloseTab(tabId: string) {
    logger.debug('CodeEditorWrapper', 'handleCloseTab called', { tabId });

    const tab = $tabs.find(t => t.id === tabId);
    if (!tab) {
      logger.warn('CodeEditorWrapper', 'Tab not found, returning');
      return;
    }

    const buffer = $buffers.find(b => b.id === tab.bufferId);
    logger.debug('CodeEditorWrapper', 'Found buffer for closing tab', {
      bufferId: buffer?.id,
      isDirty: buffer?.isDirty
    });

    if (buffer?.isDirty) {
      logger.debug('CodeEditorWrapper', 'Buffer is dirty, showing confirmation modal');
      pendingCloseTabId = tabId;
      showConfirmClose = true;
    } else {
      logger.debug('CodeEditorWrapper', 'Buffer is clean, closing directly');
      closeTabDirectly(tabId);
    }
  }

  function closeTabDirectly(tabId: string) {
    actions.closeTab(tabId);
    localTabIds = localTabIds.filter((id) => id !== tabId);
    if (activeLocalTabId === tabId && localTabIds.length > 0) {
      activeLocalTabId = localTabIds[0];
      actions.switchToTab(localTabIds[0]);
    }
  }

  function handleConfirmClose() {
    if (pendingCloseTabId) {
      logger.debug('CodeEditorWrapper', 'Confirmed close', { tabId: pendingCloseTabId });
      closeTabDirectly(pendingCloseTabId);
    }
    showConfirmClose = false;
    pendingCloseTabId = null;
  }

  function handleCancelClose() {
    logger.debug('CodeEditorWrapper', 'Cancelled close');
    showConfirmClose = false;
    pendingCloseTabId = null;
  }

  let showSaveModal = $state(false)

  function handleKeyDown(event: KeyboardEvent) {
    if ((event.ctrlKey || event.metaKey) && event.key === 's') {
      event.preventDefault()
      handleSave()
    }
  }

  function handleSave() {
    if (!activeBuffer) return
    showSaveModal = true
  }

  async function handleFileSave(filePath: string) {
    if (!activeBuffer) return
    const result = await actions.saveBuffer(activeBuffer.id, filePath)
    if (!result.success) {
      alert(result.message)
    }
  }

  onMount(() => {
    document.addEventListener('keydown', handleKeyDown)
  })

  onDestroy(() => {
    document.removeEventListener('keydown', handleKeyDown)
  })
</script>

<div class="h-full flex flex-col overflow-hidden">
  {#if localTabs.length > 1}
    <!-- Tab bar -->
    <div
      class="flex items-center bg-surface-200 dark:bg-surface-800 border-b border-surface-300 dark:border-surface-700"
    >
      {#each localTabs as tab}
        <div class="flex items-center group">
          <button
            class="px-3 py-2 text-sm transition-colors {tab.id === activeLocalTabId
              ? 'bg-surface-100 dark:bg-surface-900 border-b-2 border-primary-500'
              : 'hover:bg-surface-300 dark:hover:bg-surface-700'}"
            onclick={() => handleSwitchTab(tab.id)}
          >
            <span class="text-surface-900 dark:text-surface-50">{tab.title}</span>
          </button>
          {#if !tab.isPinned}
            <button
              class="px-1 opacity-0 group-hover:opacity-100 transition-opacity text-surface-500 hover:text-surface-900 dark:hover:text-surface-50"
              onclick={() => handleCloseTab(tab.id)}
              title="Close tab"
            >
              ×
            </button>
          {/if}
        </div>
      {/each}
    </div>
  {/if}

  <!-- Editor content -->
  <div class="flex-1 overflow-hidden">
    {#if activeBuffer}
      <CodeEditor
        buffer={activeBuffer}
        onchange={handleChange}
        onexecute={handleExecute}
        oncreatetab={handleCreateTab}
      />
    {:else}
      <div class="h-full flex items-center justify-center text-surface-500">
        <p>Loading editor...</p>
      </div>
    {/if}
  </div>
</div>

<SaveFileModal
  isOpen={showSaveModal}
  initialPath={$currentProject?.root_path || null}
  onclose={() => showSaveModal = false}
  onsave={handleFileSave}
/>

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
