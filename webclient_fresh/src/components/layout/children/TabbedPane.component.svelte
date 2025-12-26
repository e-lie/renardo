<script lang="ts">
  import type { PanePosition } from '../../../models/layout'
  import { useLayoutStore } from '../../../store/layout'
  import TextArea from './TextArea.component.svelte'
  import CodeEditorWrapper from './CodeEditorWrapper.component.svelte'
  import TopMenu from './TopMenu.component.svelte'
  import { TutorialTab } from '../../tutorial'
  import { ConsoleOutput } from '../../index'

  let { position }: { position: PanePosition } = $props()

  const { getters, actions } = useLayoutStore()
  const { paneTabConfigs } = getters
  const tabs = $derived($paneTabConfigs.get(position) || [])
  const activeTab = $derived(tabs.find(t => t.active))

  const componentMap: Record<string, any> = {
    'TextArea': TextArea,
    'CodeEditor': CodeEditorWrapper,
    'TopMenu': TopMenu,
    'CodeEditorWrapper': CodeEditorWrapper,
    'TutorialTab': TutorialTab,
    'ConsoleOutput': ConsoleOutput
  }

  function handleSwitchTab(tabId: string) {
    actions.switchToTab(position, tabId)
  }

  function handleCloseTab(tabId: string) {
    actions.removeTab(position, tabId)
  }
</script>

<div class="h-full flex flex-col">
  {#if tabs.length === 0}
    <!-- Empty placeholder -->
    <div class="h-full bg-surface-100 dark:bg-surface-900"></div>
  {:else}
    {#if tabs.length > 1}
      <!-- Tab bar -->
      <div class="flex items-center bg-surface-200 dark:bg-surface-800 border-b border-surface-300 dark:border-surface-700">
        {#each tabs as tab}
          <button
            class="px-3 py-2 text-sm transition-colors {tab.active ? 'bg-surface-100 dark:bg-surface-900 border-b-2 border-primary-500' : 'hover:bg-surface-300 dark:hover:bg-surface-700'}"
            onclick={() => handleSwitchTab(tab.id)}
          >
            <span class="text-surface-900 dark:text-surface-50">{tab.title}</span>
          </button>
        {/each}
      </div>
    {/if}

    <!-- Active tab content -->
    <div class="flex-1 overflow-hidden">
      {#if activeTab && componentMap[activeTab.componentType]}
        {@const Component = componentMap[activeTab.componentType]}
        <Component
          componentId={activeTab.componentId}
          title={activeTab.title}
        />
      {:else}
        <div class="h-full flex items-center justify-center text-surface-500">
          <p>No component available</p>
        </div>
      {/if}
    </div>
  {/if}
</div>
