<script lang="ts">
  import CodeEditor from '../../editor/CodeEditor.component.svelte';
  import SaveFileModal from '../../shared/SaveFileModal.component.svelte';
  import { ElConfirmModal } from '../../primitives';
  import { useEditorStore } from '../../../store/editor';
  import { useProjectStore } from '../../../store/project';
  import { useI18nStore } from '../../../store/i18n/I18n.store';
  import type { LoadFileEvent } from '../../../events/editorEvents';
  import logger from '../../../services/logger.service';
  import { scheduleBackendSave } from '../../../services/frontend-state.service';
  import { onMount, onDestroy } from 'svelte';

  interface SavedTab {
    filePath: string;
    title: string;
    isActive: boolean;
  }

  let {
    componentId = 'code-editor',
    title = 'Code Editor',
  }: {
    componentId?: string;
    title?: string;
  } = $props();

  const { actions, getters } = useEditorStore();
  const { buffers } = getters;

  const { getters: projectGetters } = useProjectStore();
  const { currentProject } = projectGetters;

  const { getters: i18nGetters } = useI18nStore();
  const { translate } = i18nGetters;

  let editorId = $state<string>('');
  let showConfirmClose = $state(false);
  let pendingCloseTabId = $state<string | null>(null);
  let isTabsInitialized = $state(false);

  // Get editor-specific derived stores
  let localTabs = $derived(editorId ? getters.getEditorTabs(editorId) : null);
  let activeTab = $derived(editorId ? getters.getEditorActiveTab(editorId) : null);
  let activeBuffer = $derived(editorId ? getters.getEditorActiveBuffer(editorId) : null);

  // Register editor and restore or create initial tabs
  $effect(() => {
    if (!editorId) {
      editorId = actions.registerEditor(componentId);
      logger.debug('CodeEditorWrapper', 'Registered editor', { editorId, componentId });
      initEditorTabs(editorId);
    }
  });

  async function initEditorTabs(eid: string) {
    const savedTabs = getPersistedTabs();

    if (savedTabs.length === 0) {
      const bufferId = actions.createBuffer({ name: title || 'Code Editor', content: '', language: 'python' });
      actions.createTab(eid, bufferId);
      isTabsInitialized = true;
      return;
    }

    let restoredCount = 0;
    let activeTabId: string | null = null;

    for (const saved of savedTabs) {
      try {
        const response = await fetch(
          `http://localhost:8000/api/file-explorer/read?path=${encodeURIComponent(saved.filePath)}`
        );
        if (!response.ok) continue;
        const data = await response.json();
        const tabId = actions.loadContentInNewTab(eid, data.content || '', saved.title, saved.filePath);
        if (saved.isActive) activeTabId = tabId;
        restoredCount++;
      } catch {
        // Fichier inaccessible, on le saute
      }
    }

    if (restoredCount === 0) {
      // Tous les fichiers ont échoué, on crée un buffer vide
      const bufferId = actions.createBuffer({ name: title || 'Code Editor', content: '', language: 'python' });
      actions.createTab(eid, bufferId);
    } else if (activeTabId) {
      actions.switchToTab(eid, activeTabId);
    }

    isTabsInitialized = true;
  }

  function getPersistedTabs(): SavedTab[] {
    const raw = localStorage.getItem('editor-tabs');
    if (!raw) return [];
    try {
      return JSON.parse(raw)[componentId] || [];
    } catch {
      return [];
    }
  }

  // Sauvegarder les onglets file-backed quand ils changent (après init seulement)
  $effect(() => {
    if (!editorId || !isTabsInitialized) return;

    const openTabs: SavedTab[] = ($localTabs || [])
      .map(tab => {
        const buf = $buffers.find(b => b.id === tab.bufferId);
        if (!buf?.filePath) return null;
        return {
          filePath: buf.filePath,
          title: tab.title,
          isActive: tab.id === $activeTab?.id,
        };
      })
      .filter((t): t is SavedTab => t !== null);

    const saved = JSON.parse(localStorage.getItem('editor-tabs') || '{}');
    saved[componentId] = openTabs;
    localStorage.setItem('editor-tabs', JSON.stringify(saved));
    scheduleBackendSave();
  });

  // Listen for file load events
  $effect(() => {
    const handleLoadFile = (event: CustomEvent) => {
      if (!editorId) return
      const { content, title, filePath } = event.detail
      logger.debug('CodeEditorWrapper', 'Received loadFile event', { title, filePath })

      // Check if file already open
      const tabs = $localTabs || []
      const existingTab = tabs.find(t => {
        const buf = $buffers.find(b => b.id === t.bufferId)
        return buf?.filePath === filePath
      })

      if (existingTab) {
        logger.debug('CodeEditorWrapper', 'File already open, switching to tab', { tabId: existingTab.id })
        actions.switchToTab(editorId, existingTab.id)
      } else {
        logger.debug('CodeEditorWrapper', 'Loading file in new tab')
        actions.loadContentInNewTab(editorId, content, title, filePath)
      }
    }

    window.addEventListener('editor:loadFile', handleLoadFile as EventListener)

    return () => {
      window.removeEventListener('editor:loadFile', handleLoadFile as EventListener)
    }
  })

  function handleChange(value: string) {
    if ($activeBuffer) {
      actions.updateBufferContent($activeBuffer.id, value);
    }
  }

  function handleExecute(code: string) {
    if ($activeBuffer?.language === 'hydra') {
      actions.executeHydraCode(code);
    } else {
      actions.executeCode(code);
    }
  }

  function handleCreateTab(language: 'python' | 'hydra' = 'python') {
    if (!editorId) return;
    const newBufferId = actions.createBuffer({
      name: language === 'hydra' ? 'Hydra' : 'Untitled',
      content: language === 'hydra' ? 'osc().mult(solid(.1,.1,.1)).out()' : '',
      language,
    });
    actions.createTab(editorId, newBufferId);
  }

  function handleSwitchTab(tabId: string) {
    if (!editorId) return;
    actions.switchToTab(editorId, tabId);
  }

  function handleCloseTab(tabId: string) {
    if (!editorId) return;
    logger.debug('CodeEditorWrapper', 'handleCloseTab called', { tabId });

    const tab = $localTabs?.find(t => t.id === tabId);
    if (!tab) {
      logger.warn('CodeEditorWrapper', 'Tab not found');
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
    if (!editorId) return;
    actions.closeTab(editorId, tabId);
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
    if (!$activeBuffer) return
    if ($activeBuffer.filePath) {
      handleFileSave($activeBuffer.filePath)
    } else {
      showSaveModal = true
    }
  }

  async function handleFileSave(filePath: string) {
    if (!$activeBuffer) return
    const result = await actions.saveBuffer($activeBuffer.id, filePath)
    if (!result.success) {
      alert(result.message)
    }
  }

  onMount(() => {
    document.addEventListener('keydown', handleKeyDown)
  })

  onDestroy(() => {
    document.removeEventListener('keydown', handleKeyDown)
    if (editorId) {
      actions.unregisterEditor(editorId)
      logger.debug('CodeEditorWrapper', 'Unregistered editor', { editorId })
    }
  })
</script>

<div class="h-full flex flex-col overflow-hidden">
  {#if $localTabs && $localTabs.length > 1}
    <!-- Tab bar -->
    <div
      class="flex items-center bg-surface-200 dark:bg-surface-800 border-b border-surface-300 dark:border-surface-700"
    >
      {#each $localTabs as tab}
        {@const tabBuffer = $buffers?.find(b => b.id === tab.bufferId)}
        <div class="flex items-center group">
          <button
            class="px-3 py-2 text-sm transition-colors {tab.id === $activeTab?.id
              ? 'bg-surface-100 dark:bg-surface-900 border-b-2 border-primary-500'
              : 'hover:bg-surface-300 dark:hover:bg-surface-700'}"
            onclick={() => handleSwitchTab(tab.id)}
          >
            <span class="text-surface-900 dark:text-surface-50 {tabBuffer?.isDirty ? 'italic opacity-70' : ''}">{tab.title}</span>
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
    {#if $activeBuffer}
      <CodeEditor
        buffer={$activeBuffer}
        onchange={handleChange}
        onexecute={handleExecute}
        oncreatetab={(lang) => handleCreateTab(lang)}
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
