<script lang="ts">
  import { useEditorStore } from '../../store/editor/Editor.store'
  import EditorTabs from '../editor/EditorTabs.component.svelte'
  import CodeEditor from '../editor/CodeEditor.component.svelte'
  import ElPane from '../primitives/panes/ElPane.svelte'
  import ElPaneTab from '../primitives/tabs/ElPaneTab.svelte'
  import ElButton from '../primitives/buttons/ElButton.svelte'
  import type { TabInterface, BufferInterface } from '../../models/editor'

  // Editor store
  const { actions: editorActions, getters: editorGetters } = useEditorStore()
  const { tabs, buffers, activeBuffer } = editorGetters

  // Simple layout state
  let visiblePanes = $state({
    'left-top': {
      id: 'left-top',
      position: 'left-top',
      title: 'Left Top',
      isVisible: false,
      isResizable: true,
      dimensions: { width: 300, minWidth: 200, height: 300, minHeight: 200 },
      tabs: [{
        id: 'left-top-tab-1',
        paneId: 'left-top',
        title: 'Notes',
        componentType: 'TextArea',
        isActive: true,
        isCloseable: true
      }],
      activeTabId: 'left-top-tab-1'
    },
    'right-top': {
      id: 'right-top',
      position: 'right-top',
      title: 'Right Top',
      isVisible: false,
      isResizable: true,
      dimensions: { width: 300, minWidth: 200, height: 300, minHeight: 200 },
      tabs: [{
        id: 'right-top-tab-1',
        paneId: 'right-top',
        title: 'Workspace',
        componentType: 'TextArea',
        isActive: true,
        isCloseable: true
      }],
      activeTabId: 'right-top-tab-1'
    },
    'center': {
      id: 'center',
      position: 'center',
      title: 'Code Editor',
      isVisible: true,
      isResizable: true,
      dimensions: { width: 400, minWidth: 300, height: 400, minHeight: 300 },
      tabs: [],
      activeTabId: null
    }
  })

  // Tab management
  function handleSwitchTab(tabId: string) {
    editorActions.switchToTab(tabId)
  }

  function handleCloseTab(tabId: string) {
    editorActions.closeTab(tabId)
  }

  function handleCreateTab() {
    const bufferId = editorActions.createBuffer({
      name: 'Untitled',
      content: '',
      language: 'python',
    })
    editorActions.createTab(bufferId)
  }

  // Layout management
  function togglePaneVisibility(position: string) {
    visiblePanes = {
      ...visiblePanes,
      [position]: {
        ...visiblePanes[position],
        isVisible: !visiblePanes[position].isVisible
      }
    }
  }

  // Initialize with at least one tab
  $effect(() => {
    const currentTabs = $tabs
    if (currentTabs.length === 0) {
      const bufferId = editorActions.createBuffer({
        name: 'Untitled',
        content: '',
        language: 'python',
      })
      editorActions.createTab(bufferId)
    }
  })

  // Handle code changes
  function handleCodeChange(content: string) {
    if ($activeBuffer) {
      editorActions.updateBufferContent($activeBuffer.id, content)
    }
  }

  function handleCodeExecute(code: string) {
    editorActions.executeCode(code)
  }
</script>

<!-- Left Toggle Button -->
{#if visiblePanes['left-top'].isVisible}
  <ElButton
    variant="primary"
    addCss="fixed left-4 top-1/2 btn-circle btn-sm shadow-lg z-40"
    style="transform: translateY(-50%)"
    onclick={() => togglePaneVisibility('left-top')}
    testid="toggle-left-panes"
  >
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
      <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
    </svg>
  </ElButton>
{:else}
  <ElButton
    variant="primary"
    addCss="fixed left-4 top-1/2 btn-circle btn-sm shadow-lg z-40"
    style="transform: translateY(-50%)"
    onclick={() => togglePaneVisibility('left-top')}
    testid="show-left-panes"
  >
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
      <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
    </svg>
  </ElButton>
{/if}

<!-- Right Toggle Button -->
{#if visiblePanes['right-top'].isVisible}
  <ElButton
    variant="primary"
    addCss="fixed right-4 top-1/2 btn-circle btn-sm shadow-lg z-40"
    style="transform: translateY(-50%)"
    onclick={() => togglePaneVisibility('right-top')}
    testid="toggle-right-panes"
  >
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
      <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
    </svg>
  </ElButton>
{:else}
  <ElButton
    variant="primary"
    addCss="fixed right-4 top-1/2 btn-circle btn-sm shadow-lg z-40"
    style="transform: translateY(-50%)"
    onclick={() => togglePaneVisibility('right-top')}
    testid="show-right-panes"
  >
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
      <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
    </svg>
  </ElButton>
{/if}

<!-- Grid Layout -->
<div class="layout-grid h-full grid" style="
  grid-template-areas:
    'left-top center right-top'
    'center center right-top'
    'center center center';
  grid-template-columns: {visiblePanes['left-top'].isVisible ? (visiblePanes['left-top'].dimensions.width || 300) + 'px' : '0px'} 1fr {visiblePanes['right-top'].isVisible ? (visiblePanes['right-top'].dimensions.width || 300) + 'px' : '0px'};
  grid-template-rows: {visiblePanes['left-top'].isVisible ? (visiblePanes['left-top'].dimensions.height || 300) + 'px' : '0px'} 1fr 0px;
  gap: 4px;
  padding: 4px;
">
  <!-- Left Top Pane -->
  {#if visiblePanes['left-top'].isVisible}
    <ElPane pane={visiblePanes['left-top']} style="grid-area: left-top;">
      <div class="flex gap-1 bg-base-200 px-2 py-1">
        {#each visiblePanes['left-top'].tabs as tab (tab.id)}
          <ElPaneTab {tab} />
        {/each}
      </div>
      <div class="flex-1 p-2 bg-base-100">
        <textarea
          class="textarea textarea-bordered flex-1 font-mono"
          placeholder="Notes..."
        ></textarea>
      </div>
    </ElPane>
  {/if}

  <!-- Center Pane (Editor) -->
  <ElPane pane={visiblePanes['center']} style="grid-area: center;">
    <!-- Original Editor Tabs -->
    <div class="bg-base-200 border-b border-base-300">
      <EditorTabs
        tabs={$tabs}
        buffers={$buffers}
        onswitch={handleSwitchTab}
        onclose={handleCloseTab}
        oncreate={handleCreateTab}
      />
    </div>

    <!-- Original Code Editor -->
    <div class="flex-1 overflow-hidden">
      {#if $activeBuffer}
        <CodeEditor 
          buffer={$activeBuffer}
          onchange={handleCodeChange}
          onexecute={handleCodeExecute}
        />
      {:else}
        <div class="flex items-center justify-center h-full">
          <p class="text-base-content/50">No active buffer</p>
        </div>
      {/if}
    </div>
  </ElPane>
</div>