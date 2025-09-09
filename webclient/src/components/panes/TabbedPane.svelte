<script>
  import { onMount, onDestroy } from 'svelte';
  import { PaneTabManager } from '../../lib/newEditor/PaneTabManager';
  import { PaneComponent } from '../../lib/newEditor/PaneComponent';
  import ColorPicker from './ColorPicker.svelte';
  import TextArea from './TextArea.svelte';
  import CodeEditor from './CodeEditor.svelte';
  import { sendDebugLog } from '../../lib/websocket.js';

  // Props
  export let position = '';
  export let initialTabs = [];

  // Tab manager instance
  let tabManager = null;
  let tabs = [];
  let activeTabId = null;
  let activeComponent = null;

  // Component registry
  const componentRegistry = {
    'ColorPicker': ColorPicker,
    'TextArea': TextArea,
    'CodeEditor': CodeEditor
  };

  // Subscription cleanup
  let unsubscribeTabs = null;
  let unsubscribeActiveTab = null;

  onMount(() => {
    // Initialize tab manager
    tabManager = new PaneTabManager(initialTabs);

    // Subscribe to tabs changes
    unsubscribeTabs = tabManager.tabs.subscribe(newTabs => {
      tabs = newTabs;
    });

    // Subscribe to active tab changes
    unsubscribeActiveTab = tabManager.activeTabId.subscribe(newActiveTabId => {
      activeTabId = newActiveTabId;
      updateActiveComponent();
    });

    // Initialize active component
    updateActiveComponent();
  });

  onDestroy(() => {
    if (unsubscribeTabs) unsubscribeTabs();
    if (unsubscribeActiveTab) unsubscribeActiveTab();
    if (tabManager) tabManager.destroy();
  });

  // Update the active component based on active tab
  function updateActiveComponent() {
    if (!tabManager || !activeTabId) {
      activeComponent = null;
      sendDebugLog('DEBUG', 'TabbedPane: no tabManager or activeTabId', { tabManager: !!tabManager, activeTabId });
      return;
    }

    const activeTab = tabs.find(tab => tab.id === activeTabId);
    if (!activeTab) {
      activeComponent = null;
      sendDebugLog('DEBUG', 'TabbedPane: no activeTab found', { activeTabId, tabsLength: tabs.length });
      return;
    }

    // Get or create component for this tab
    let component = tabManager.getComponent(activeTabId);
    if (!component) {
      component = new PaneComponent({
        id: activeTab.componentId,
        type: activeTab.componentType,
        title: activeTab.title,
        initialData: {}
      });
      tabManager.registerComponent(activeTabId, component);
    }

    activeComponent = {
      component: componentRegistry[activeTab.componentType] || null,
      props: {
        componentId: activeTab.componentId,
        title: activeTab.title
      },
      config: activeTab
    };

    sendDebugLog('DEBUG', 'TabbedPane: activeComponent set', { 
      position,
      hasActiveComponent: !!activeComponent,
      hasComponent: !!activeComponent?.component,
      componentName: activeComponent?.component?.name || 'null',
      componentType: activeTab.componentType
    });
  }

  // Handle tab click
  function switchTab(tabId) {
    if (tabManager) {
      tabManager.switchToTab(tabId);
    }
  }

  // Handle tab close
  function closeTab(event, tabId) {
    event.stopPropagation();
    if (tabManager) {
      tabManager.removeTab(tabId);
    }
  }


  // Handle tab drag and drop (basic implementation)
  function handleTabDragStart(event, tabIndex) {
    event.dataTransfer.setData('text/plain', tabIndex.toString());
    event.dataTransfer.effectAllowed = 'move';
  }

  function handleTabDragOver(event) {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }

  function handleTabDrop(event, dropIndex) {
    event.preventDefault();
    const dragIndex = parseInt(event.dataTransfer.getData('text/plain'));
    
    if (dragIndex !== dropIndex && tabManager) {
      tabManager.reorderTabs(dragIndex, dropIndex);
    }
  }
</script>

<div class="tabbed-pane h-full flex flex-col">
  <!-- Tab Bar (only show when multiple tabs) -->
  {#if tabs.length > 1}
    <div class="tab-bar flex items-center bg-base-200 border-b border-base-300 min-h-10">
    <div class="flex flex-1 overflow-x-auto">
      {#each tabs as tab, index (tab.id)}
        <div 
          class="tab flex items-center px-3 py-2 cursor-pointer border-r border-base-300 min-w-0 max-w-48 {tab.active ? 'bg-base-100 text-base-content' : 'bg-base-200 text-base-content/70 hover:bg-base-300'}"
          on:click={() => switchTab(tab.id)}
          draggable="true"
          on:dragstart={(e) => handleTabDragStart(e, index)}
          on:dragover={handleTabDragOver}
          on:drop={(e) => handleTabDrop(e, index)}
          title={tab.title}
        >
          <!-- Component Icon -->
          <span class="text-xs mr-2 flex-shrink-0">
            {#if tab.componentType === 'ColorPicker'}🎨
            {:else if tab.componentType === 'TextArea'}📝
            {:else if tab.componentType === 'CodeEditor'}💻
            {:else}📦
            {/if}
          </span>
          
          <!-- Tab Title -->
          <span class="text-xs truncate flex-1 min-w-0">
            {tab.title}
          </span>
          
        </div>
      {/each}
    </div>
    </div>
  {/if}

  <!-- Tab Content -->
  <div class="tab-content" style="flex: 1; min-height: 0; overflow: hidden; display: block;">
    {#if activeComponent && activeComponent.component}
      <div class="h-full w-full">
        <svelte:component 
          this={activeComponent.component} 
          {...activeComponent.props}
        />
      </div>
    {:else if tabs.length === 0}
      <!-- Empty state -->
      <div class="h-full flex items-center justify-center text-base-content/50">
        <div class="text-center">
          <div class="text-4xl mb-2">📦</div>
          <div class="text-sm">No tabs open</div>
          <div class="text-xs opacity-70 mt-1">Configure tabs in Layout Settings</div>
        </div>
      </div>
    {:else}
      <!-- Fallback for unknown component types -->
      <div class="h-full flex items-center justify-center text-base-content/50">
        <div class="text-center">
          <div class="text-4xl mb-2">❓</div>
          <div class="text-sm">Unknown component type</div>
          <div class="text-xs opacity-70 mt-1">{activeComponent?.config?.componentType || 'N/A'}</div>
        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  .tab-bar {
    scrollbar-width: none; /* Firefox */
    -ms-overflow-style: none; /* IE and Edge */
  }
  
  .tab-bar::-webkit-scrollbar {
    display: none; /* Chrome, Safari and Opera */
  }
  
  .tab {
    transition: background-color 0.2s ease;
    user-select: none;
  }
  
  .tab:hover {
    background-color: oklch(var(--b3));
  }
  
  .tab-content {
    position: relative;
    height: 100%;
  }
  
  .tabbed-pane {
    height: 100%;
    display: flex;
    flex-direction: column;
  }
  
  /* Drag and drop visual feedback */
  .tab:drag {
    opacity: 0.5;
  }
  
  .dropdown:focus-within .dropdown-content {
    display: block;
  }
</style>