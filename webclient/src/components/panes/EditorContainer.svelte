<script>
  import { onMount, onDestroy, createEventDispatcher } from 'svelte';
  import { writable } from 'svelte/store';
  import CodeEditor from './CodeEditor.svelte';
  import { sendDebugLog } from '../../lib/websocket.js';

  const dispatch = createEventDispatcher();

  // Props
  export let containerId = null;
  export let containerData = null;
  export let depth = 0;

  // Container types
  const CONTAINER_TYPES = {
    LEAF: 'leaf',          // Contains CodeEditor tabs
    VERTICAL: 'vertical',   // Contains child containers split vertically
    HORIZONTAL: 'horizontal' // Contains child containers split horizontally
  };

  // Container state
  let containerType = CONTAINER_TYPES.LEAF;
  let children = [];
  let tabs = [];
  let activeTabId = null;
  let nextTabId = 1;
  let splitPosition = 50; // Percentage for splits

  // Resize state
  let isResizing = false;

  // Initialize container
  onMount(() => {
    if (containerData) {
      // Initialize from existing data
      initializeFromData(containerData);
    } else {
      // Create new leaf container with one tab containing a CodeEditor
      createInitialTab();
    }
    
    sendDebugLog('DEBUG', 'EditorContainer initialized', { 
      containerId, 
      containerType, 
      depth,
      tabCount: tabs.length,
      childrenCount: children.length
    });
  });

  // Initialize container from data
  function initializeFromData(data) {
    containerType = data.type || CONTAINER_TYPES.LEAF;
    splitPosition = data.splitPosition || 50;
    
    if (containerType === CONTAINER_TYPES.LEAF) {
      tabs = data.tabs || [];
      activeTabId = data.activeTabId || tabs[0]?.id || null;
      if (tabs.length === 0) {
        createInitialTab();
      }
    } else {
      children = data.children || [];
    }
  }

  // Create the initial tab for a new leaf container (automatically creates CodeEditor)
  function createInitialTab() {
    const tabId = generateTabId();
    const newTab = {
      id: tabId,
      title: `Untitled-${nextTabId}`,
      content: '',
      componentId: `${containerId}-${tabId}`,
      isDirty: false,
      lastModified: new Date().toISOString()
    };
    
    tabs = [newTab];
    activeTabId = tabId;
    
    sendDebugLog('DEBUG', 'Initial CodeEditor tab created', { containerId, tabId });
  }

  // Generate unique tab ID
  function generateTabId() {
    return `tab-${containerId}-${nextTabId++}`;
  }

  // Generate unique container ID
  function generateContainerId() {
    return `container-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  // Split vertically: create two child containers, each with a CodeEditor
  function splitVertical() {
    if (containerType !== CONTAINER_TYPES.LEAF) return;
    
    sendDebugLog('DEBUG', 'Splitting container vertically', { containerId });
    
    // Create first child container with current tabs
    const firstChildId = generateContainerId();
    const firstChild = {
      id: firstChildId,
      type: CONTAINER_TYPES.LEAF,
      tabs: [...tabs], // Move existing tabs to first child
      activeTabId: activeTabId
    };
    
    // Create second child container with new CodeEditor tab
    const secondChildId = generateContainerId();
    const newTabId = `tab-${secondChildId}-1`;
    const secondChild = {
      id: secondChildId,
      type: CONTAINER_TYPES.LEAF,
      tabs: [{
        id: newTabId,
        title: `Untitled-${nextTabId++}`,
        content: '',
        componentId: `${secondChildId}-${newTabId}`,
        isDirty: false,
        lastModified: new Date().toISOString()
      }],
      activeTabId: newTabId
    };

    // Transform this container into a vertical split
    containerType = CONTAINER_TYPES.VERTICAL;
    children = [firstChild, secondChild];
    tabs = [];
    activeTabId = null;
    splitPosition = 50;
    
    sendDebugLog('DEBUG', 'Vertical split created with CodeEditor instances', { 
      containerId, 
      firstChildId, 
      secondChildId 
    });
    
    notifyParentOfChange();
  }

  // Split horizontally: create two child containers, each with a CodeEditor
  function splitHorizontal() {
    if (containerType !== CONTAINER_TYPES.LEAF) return;
    
    sendDebugLog('DEBUG', 'Splitting container horizontally', { containerId });
    
    // Create first child container with current tabs
    const firstChildId = generateContainerId();
    const firstChild = {
      id: firstChildId,
      type: CONTAINER_TYPES.LEAF,
      tabs: [...tabs], // Move existing tabs to first child
      activeTabId: activeTabId
    };
    
    // Create second child container with new CodeEditor tab
    const secondChildId = generateContainerId();
    const newTabId = `tab-${secondChildId}-1`;
    const secondChild = {
      id: secondChildId,
      type: CONTAINER_TYPES.LEAF,
      tabs: [{
        id: newTabId,
        title: `Untitled-${nextTabId++}`,
        content: '',
        componentId: `${secondChildId}-${newTabId}`,
        isDirty: false,
        lastModified: new Date().toISOString()
      }],
      activeTabId: newTabId
    };

    // Transform this container into a horizontal split
    containerType = CONTAINER_TYPES.HORIZONTAL;
    children = [firstChild, secondChild];
    tabs = [];
    activeTabId = null;
    splitPosition = 50;
    
    sendDebugLog('DEBUG', 'Horizontal split created with CodeEditor instances', { 
      containerId, 
      firstChildId, 
      secondChildId 
    });
    
    notifyParentOfChange();
  }

  // Add new tab to leaf container (automatically creates new CodeEditor)
  function addTab() {
    if (containerType !== CONTAINER_TYPES.LEAF) return;
    
    const tabId = generateTabId();
    const newTab = {
      id: tabId,
      title: `Untitled-${nextTabId++}`,
      content: '',
      componentId: `${containerId}-${tabId}`,
      isDirty: false,
      lastModified: new Date().toISOString()
    };
    
    tabs = [...tabs, newTab];
    activeTabId = tabId;
    
    sendDebugLog('DEBUG', 'New CodeEditor tab added', { containerId, tabId });
    notifyParentOfChange();
  }

  // Remove tab from leaf container
  function removeTab(tabId) {
    if (containerType !== CONTAINER_TYPES.LEAF || tabs.length <= 1) return;
    
    const tabIndex = tabs.findIndex(tab => tab.id === tabId);
    if (tabIndex === -1) return;

    tabs = tabs.filter(tab => tab.id !== tabId);
    
    // If we removed the active tab, select a new one
    if (activeTabId === tabId) {
      const newIndex = Math.min(tabIndex, tabs.length - 1);
      activeTabId = tabs[newIndex]?.id || null;
    }
    
    sendDebugLog('DEBUG', 'CodeEditor tab removed', { containerId, tabId });
    notifyParentOfChange();
  }

  // Switch to a specific tab
  function switchToTab(tabId) {
    if (containerType !== CONTAINER_TYPES.LEAF) return;
    activeTabId = tabId;
    sendDebugLog('DEBUG', 'Switched to CodeEditor tab', { containerId, tabId });
    notifyParentOfChange();
  }

  // Update tab content
  function updateTabContent(tabId, content) {
    if (containerType !== CONTAINER_TYPES.LEAF) return;
    
    tabs = tabs.map(tab => {
      if (tab.id === tabId) {
        return {
          ...tab,
          content,
          isDirty: true,
          lastModified: new Date().toISOString()
        };
      }
      return tab;
    });
    
    notifyParentOfChange();
  }

  // Remove split and merge back into leaf container
  function removeSplit() {
    if (containerType === CONTAINER_TYPES.LEAF) return;
    
    // Find the child container with tabs and merge its content
    const childWithTabs = children.find(child => child.type === CONTAINER_TYPES.LEAF && child.tabs?.length > 0);
    
    if (childWithTabs) {
      containerType = CONTAINER_TYPES.LEAF;
      tabs = [...childWithTabs.tabs];
      activeTabId = childWithTabs.activeTabId;
      children = [];
      splitPosition = 50;
      
      sendDebugLog('DEBUG', 'Split removed, merged to leaf with CodeEditor', { containerId });
      notifyParentOfChange();
    }
  }

  // Start resizing splits
  function startResize(event) {
    if (containerType === CONTAINER_TYPES.LEAF) return;
    
    event.preventDefault();
    isResizing = true;

    const handleMouseMove = (e) => {
      if (!isResizing) return;
      
      const container = event.target.parentElement;
      const rect = container.getBoundingClientRect();
      
      if (containerType === CONTAINER_TYPES.VERTICAL) {
        const newPosition = ((e.clientX - rect.left) / rect.width) * 100;
        splitPosition = Math.max(10, Math.min(90, newPosition));
      } else {
        const newPosition = ((e.clientY - rect.top) / rect.height) * 100;
        splitPosition = Math.max(10, Math.min(90, newPosition));
      }
    };

    const handleMouseUp = () => {
      isResizing = false;
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      notifyParentOfChange();
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  }

  // Notify parent of changes
  function notifyParentOfChange() {
    const containerState = {
      id: containerId,
      type: containerType,
      splitPosition,
      tabs: containerType === CONTAINER_TYPES.LEAF ? tabs : [],
      activeTabId: containerType === CONTAINER_TYPES.LEAF ? activeTabId : null,
      children: containerType !== CONTAINER_TYPES.LEAF ? children : []
    };
    
    dispatch('containerChange', containerState);
  }

  // Handle child container changes
  function handleChildChange(event) {
    const updatedChild = event.detail;
    children = children.map(child => 
      child.id === updatedChild.id ? updatedChild : child
    );
    notifyParentOfChange();
  }

  // Get the active tab object
  $: activeTab = tabs.find(tab => tab.id === activeTabId);
</script>

<div class="editor-container h-full flex flex-col">
  <!-- Container Controls -->
  <div class="container-controls flex items-center justify-between bg-base-200 border-b border-base-300 px-2 py-1">
    <!-- Left: Split Controls -->
    <div class="flex items-center gap-1">
      {#if containerType === CONTAINER_TYPES.LEAF}
        <button 
          class="btn btn-xs btn-ghost" 
          on:click={splitVertical}
          title="Split Vertical"
        >
          ⫿
        </button>
        <button 
          class="btn btn-xs btn-ghost" 
          on:click={splitHorizontal}
          title="Split Horizontal"
        >
          ⬓
        </button>
      {:else}
        <button 
          class="btn btn-xs btn-ghost" 
          on:click={removeSplit}
          title="Remove Split"
        >
          ⊡
        </button>
      {/if}
    </div>

    <!-- Center: Container Info -->
    <div class="flex items-center gap-2 text-xs text-base-content/70">
      <span>
        {#if containerType === CONTAINER_TYPES.LEAF}
          CodeEditors: {tabs.length}
        {:else}
          Split: {containerType}
        {/if}
      </span>
      <span>Depth: {depth}</span>
    </div>

    <!-- Right: Tab Controls (only for leaf containers) -->
    <div class="flex items-center gap-1">
      {#if containerType === CONTAINER_TYPES.LEAF}
        <button 
          class="btn btn-xs btn-ghost" 
          on:click={addTab}
          title="New CodeEditor Tab"
        >
          ＋
        </button>
      {/if}
    </div>
  </div>

  <!-- Container Content -->
  <div class="container-content flex-1">
    {#if containerType === CONTAINER_TYPES.LEAF}
      <!-- Leaf Container: Tabs + CodeEditor -->
      <div class="leaf-container h-full flex flex-col">
        <!-- Tab Bar (show only if multiple tabs) -->
        {#if tabs.length > 1}
          <div class="tab-bar flex items-center bg-base-200 border-b border-base-300">
            <div class="tabs flex-1 flex overflow-x-auto">
              {#each tabs as tab (tab.id)}
                <div 
                  class="tab flex items-center px-3 py-2 cursor-pointer border-r border-base-300 min-w-0 max-w-48 {tab.id === activeTabId ? 'bg-base-100 text-base-content' : 'bg-base-200 text-base-content/70 hover:bg-base-300'}"
                  on:click={() => switchToTab(tab.id)}
                  role="tab"
                  tabindex="0"
                  on:keydown={(e) => e.key === 'Enter' && switchToTab(tab.id)}
                >
                  <span class="text-xs mr-1 flex-shrink-0">💻</span>
                  <span class="text-xs truncate flex-1 min-w-0">
                    {tab.title}{tab.isDirty ? '*' : ''}
                  </span>
                  {#if tabs.length > 1}
                    <button 
                      class="ml-1 text-xs opacity-50 hover:opacity-100"
                      on:click|stopPropagation={() => removeTab(tab.id)}
                    >
                      ×
                    </button>
                  {/if}
                </div>
              {/each}
            </div>
          </div>
        {/if}

        <!-- Active Tab Content (CodeEditor) -->
        <div class="tab-content flex-1">
          {#if activeTab}
            <CodeEditor
              componentId={activeTab.componentId}
              title={activeTab.title}
              bind:content={activeTab.content}
              on:contentChange={(e) => updateTabContent(activeTab.id, e.detail)}
            />
          {/if}
        </div>
      </div>

    {:else if containerType === CONTAINER_TYPES.VERTICAL}
      <!-- Vertical Split Container -->
      <div class="split-container h-full flex">
        {#each children as child, index (child.id)}
          <div 
            class="child-container"
            style="width: {index === 0 ? splitPosition : 100 - splitPosition}%; min-width: 200px;"
          >
            <svelte:self
              containerId={child.id}
              containerData={child}
              depth={depth + 1}
              on:containerChange={handleChildChange}
            />
          </div>

          <!-- Vertical Resize Handle -->
          {#if index === 0 && children.length > 1}
            <div 
              class="w-1 bg-base-300 cursor-col-resize hover:bg-primary/30 transition-colors flex-shrink-0"
              on:mousedown={startResize}
              role="separator"
            ></div>
          {/if}
        {/each}
      </div>

    {:else if containerType === CONTAINER_TYPES.HORIZONTAL}
      <!-- Horizontal Split Container -->
      <div class="split-container h-full flex flex-col">
        {#each children as child, index (child.id)}
          <div 
            class="child-container"
            style="height: {index === 0 ? splitPosition : 100 - splitPosition}%; min-height: 150px;"
          >
            <svelte:self
              containerId={child.id}
              containerData={child}
              depth={depth + 1}
              on:containerChange={handleChildChange}
            />
          </div>

          <!-- Horizontal Resize Handle -->
          {#if index === 0 && children.length > 1}
            <div 
              class="h-1 bg-base-300 cursor-row-resize hover:bg-primary/30 transition-colors flex-shrink-0"
              on:mousedown={startResize}
              role="separator"
            ></div>
          {/if}
        {/each}
      </div>
    {/if}
  </div>
</div>

<style>
  .editor-container {
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  .container-content {
    flex: 1;
    min-height: 0;
    overflow: hidden;
  }

  .leaf-container {
    display: flex;
    flex-direction: column;
    min-height: 0;
  }

  .tab-content {
    flex: 1;
    min-height: 0;
    overflow: hidden;
  }

  .split-container {
    min-height: 0;
  }

  .child-container {
    min-height: 0;
    overflow: hidden;
  }

  .tabs {
    scrollbar-width: none; /* Firefox */
    -ms-overflow-style: none; /* IE and Edge */
  }
  
  .tabs::-webkit-scrollbar {
    display: none; /* Chrome, Safari and Opera */
  }

  .tab {
    transition: background-color 0.2s ease;
    user-select: none;
  }

  .tab:hover {
    background-color: oklch(var(--b3));
  }
</style>