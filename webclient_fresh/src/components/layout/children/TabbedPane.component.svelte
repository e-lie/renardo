<script lang="ts">
  import type { PanePosition } from '../../../models/layout'
  import { useLayoutStore } from '../../../store/layout'
  import ColorPicker from './ColorPicker.component.svelte'
  import TextArea from './TextArea.component.svelte'
  import CodeEditorWrapper from './CodeEditorWrapper.component.svelte'
  import TopMenu from './TopMenu.component.svelte'

  let { position }: { position: PanePosition } = $props()

  const { getters, actions } = useLayoutStore()
  const tabs = $derived(getters.getPaneTabConfigs(position))
  const activeTab = $derived(tabs.find(t => t.active))

  const componentMap = {
    'ColorPicker': ColorPicker,
    'TextArea': TextArea,
    'CodeEditor': CodeEditorWrapper,
    'TopMenu': TopMenu
  }

  function handleSwitchTab(tabId: string) {
    actions.switchToTab(position, tabId)
  }

  function handleCloseTab(tabId: string) {
    actions.removeTab(position, tabId)
  }
</script>

<div class="h-full flex flex-col">
  {#if tabs.length > 1}
    <!-- Tab bar -->
    <div class="flex items-center bg-surface-200 dark:bg-surface-800 border-b border-surface-300 dark:border-surface-700">
      {#each tabs as tab}
        <button
          class="px-3 py-2 text-sm transition-colors {tab.active ? 'bg-surface-100 dark:bg-surface-900 border-b-2 border-primary-500' : 'hover:bg-surface-300 dark:hover:bg-surface-700'}"
          onclick={() => handleSwitchTab(tab.id)}
        >
          <span class="text-surface-900 dark:text-surface-50">{tab.title}</span>
          {#if tab.closable}
            <span
              class="ml-2 text-surface-600 dark:text-surface-400 hover:text-error-500 cursor-pointer"
              onclick={(e) => { e.stopPropagation(); handleCloseTab(tab.id) }}
            >×</span>
          {/if}
        </button>
      {/each}
    </div>
  {/if}

  <!-- Active tab content -->
  <div class="flex-1 overflow-hidden">
    {#if activeTab && componentMap[activeTab.componentType]}
      <svelte:component
        this={componentMap[activeTab.componentType]}
        componentId={activeTab.componentId}
        title={activeTab.title}
      />
    {:else}
      <div class="h-full flex items-center justify-center text-surface-500">
        <p>No component available</p>
      </div>
    {/if}
  </div>
</div>
