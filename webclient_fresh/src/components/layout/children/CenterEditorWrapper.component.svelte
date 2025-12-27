<script lang="ts">
  import { onMount, onDestroy } from 'svelte'
  import CodeEditor from '../../editor/CodeEditor.component.svelte'
  import SaveFileModal from '../../shared/SaveFileModal.component.svelte'
  import { ElConfirmModal } from '../../primitives'
  import { useEditorStore } from '../../../store/editor'
  import { useProjectStore } from '../../../store/project'
  import { useI18nStore } from '../../../store/i18n/I18n.store'
  import logger from '../../../services/logger.service'

  const { actions, getters } = useEditorStore()
  const { tabs, buffers } = getters

  const { getters: projectGetters } = useProjectStore()
  const { currentProject } = projectGetters

  const { getters: i18nGetters } = useI18nStore()
  const { translate } = i18nGetters

  // Track local tab IDs for this editor instance
  let localTabIds = $state<string[]>([])
  let activeLocalTabId = $state<string | null>(null)
  let showConfirmClose = $state(false)
  let pendingCloseTabId = $state<string | null>(null)

  // Get active buffer from active local tab
  let activeBuffer = $derived.by(() => {
    if (!activeLocalTabId) return null
    const tab = $tabs.find(t => t.id === activeLocalTabId)
    if (!tab) return null
    return $buffers.find(b => b.id === tab.bufferId) || null
  })

  // Get local tabs
  let localTabs = $derived($tabs.filter(t => localTabIds.includes(t.id)))

  // Create initial buffer for center editor
  $effect(() => {
    if (localTabIds.length === 0) {
      const newBufferId = actions.createBuffer({
        name: 'Untitled',
        content: '',
        language: 'python',
      })
      const newTabId = actions.createTab(newBufferId)
      localTabIds = [newTabId]
      activeLocalTabId = newTabId
    }
  })

  // Sync new tabs created globally to local tab list
  $effect(() => {
    const allTabIds = $tabs.map(t => t.id)
    const newTabs = allTabIds.filter(id => !localTabIds.includes(id))

    if (newTabs.length > 0) {
      localTabIds = [...localTabIds, ...newTabs]
      // Switch to the newest tab
      const newestTab = $tabs.find(t => t.isActive)
      if (newestTab) {
        activeLocalTabId = newestTab.id
      }
    }
  })

  // Handle Ctrl+S to save
  function handleKeyDown(event: KeyboardEvent) {
    if ((event.ctrlKey || event.metaKey) && event.key === 's') {
      event.preventDefault()
      handleSave()
    }
  }

  onMount(() => {
    document.addEventListener('keydown', handleKeyDown)
  })

  onDestroy(() => {
    document.removeEventListener('keydown', handleKeyDown)
  })

  let showSaveModal = $state(false)

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

  function handleChange(value: string) {
    if (activeBuffer) {
      actions.updateBufferContent(activeBuffer.id, value)
    }
  }

  function handleExecute(code: string) {
    actions.executeCode(code)
  }

  function handleCreateTab() {
    const newBufferId = actions.createBuffer({
      name: 'Untitled',
      content: '',
      language: 'python',
    })
    const newTabId = actions.createTab(newBufferId)
    localTabIds = [...localTabIds, newTabId]
    activeLocalTabId = newTabId
    actions.switchToTab(newTabId)
  }

  function handleSwitchTab(tabId: string) {
    activeLocalTabId = tabId
    actions.switchToTab(tabId)
  }

  function handleCloseTab(tabId: string) {
    logger.debug('CenterEditorWrapper', 'handleCloseTab called', { tabId })

    // Find the tab and its buffer
    const tab = $tabs.find(t => t.id === tabId)
    if (!tab) {
      logger.warn('CenterEditorWrapper', 'Tab not found, returning')
      return
    }

    const buffer = $buffers.find(b => b.id === tab.bufferId)
    logger.debug('CenterEditorWrapper', 'Found buffer for closing tab', { bufferId: buffer?.id, isDirty: buffer?.isDirty })

    if (buffer?.isDirty) {
      logger.debug('CenterEditorWrapper', 'Buffer is dirty, showing confirmation modal')
      pendingCloseTabId = tabId
      showConfirmClose = true
    } else {
      logger.debug('CenterEditorWrapper', 'Buffer is clean, closing directly')
      closeTabDirectly(tabId)
    }
  }

  function closeTabDirectly(tabId: string) {
    actions.closeTab(tabId)
    localTabIds = localTabIds.filter(id => id !== tabId)
    if (activeLocalTabId === tabId && localTabIds.length > 0) {
      activeLocalTabId = localTabIds[0]
      actions.switchToTab(localTabIds[0])
    }
  }

  function handleConfirmClose() {
    if (pendingCloseTabId) {
      logger.debug('CenterEditorWrapper', 'Confirmed close', { tabId: pendingCloseTabId })
      closeTabDirectly(pendingCloseTabId)
    }
    showConfirmClose = false
    pendingCloseTabId = null
  }

  function handleCancelClose() {
    logger.debug('CenterEditorWrapper', 'Cancelled close')
    showConfirmClose = false
    pendingCloseTabId = null
  }
</script>

<div class="h-full flex flex-col">
  {#if localTabs.length > 1}
    <!-- Tab bar -->
    <div class="flex items-center bg-surface-200 dark:bg-surface-800 border-b border-surface-300 dark:border-surface-700">
      {#each localTabs as tab}
        <div class="flex items-center group">
          <button
            class="px-3 py-2 text-sm transition-colors {tab.id === activeLocalTabId ? 'bg-surface-100 dark:bg-surface-900 border-b-2 border-primary-500' : 'hover:bg-surface-300 dark:hover:bg-surface-700'}"
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
      <CodeEditor buffer={activeBuffer} onchange={handleChange} onexecute={handleExecute} oncreatetab={handleCreateTab} />
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
