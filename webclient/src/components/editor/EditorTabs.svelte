<script>
  import { createEventDispatcher, onMount, afterUpdate } from 'svelte';
  
  export let tabs = [];
  export let activeTabId = 1;
  export let nextTabId = 2;
  export let rightPanelOpen = true;
  
  const dispatch = createEventDispatcher();
  
  // Get the active tab's content
  $: activeBuffer = tabs.find(t => t.id === activeTabId);
  
  // Check if there's a startup file tab
  $: startupFileTab = tabs.find(tab => tab.isStartupFile);
  
  // Scrolling state
  let tabsContainer;
  let canScrollLeft = false;
  let canScrollRight = false;
  let scrollAmount = 200; // Pixels to scroll on arrow click
  
  function switchTab(tabId) {
    dispatch('switchTab', { tabId });
    // Ensure the active tab is visible after switching
    setTimeout(() => ensureActiveTabVisible(), 100);
  }
  
  function startEditingBufferName(bufferId) {
    dispatch('startEditingName', { bufferId });
  }
  
  function finishEditingBufferName(bufferId, buffer) {
    dispatch('finishEditingName', { bufferId, newName: buffer.editingName });
  }
  
  function cancelEditingBufferName(bufferId) {
    dispatch('cancelEditingName', { bufferId });
  }
  
  function confirmCloseBuffer(bufferId) {
    dispatch('closeBuffer', { bufferId });
  }
  
  function openNewBufferModal() {
    dispatch('newBuffer');
  }
  
  function saveStartupFile(buffer) {
    dispatch('saveStartupFile', { buffer });
  }
  
  function toggleRightPanel() {
    dispatch('toggleRightPanel');
  }
  
  function scrollTabs(direction) {
    if (!tabsContainer) return;
    
    const currentScroll = tabsContainer.scrollLeft;
    const newScroll = direction === 'left' 
      ? Math.max(0, currentScroll - scrollAmount)
      : currentScroll + scrollAmount;
    
    tabsContainer.scrollTo({
      left: newScroll,
      behavior: 'smooth'
    });
  }
  
  function checkScrollButtons() {
    if (!tabsContainer) return;
    
    const { scrollLeft, scrollWidth, clientWidth } = tabsContainer;
    canScrollLeft = scrollLeft > 0;
    canScrollRight = scrollLeft + clientWidth < scrollWidth - 1;
  }
  
  function ensureActiveTabVisible() {
    if (!tabsContainer) return;
    
    const activeTab = tabsContainer.querySelector('.tab-active');
    if (!activeTab) return;
    
    const containerRect = tabsContainer.getBoundingClientRect();
    const tabRect = activeTab.getBoundingClientRect();
    
    if (tabRect.left < containerRect.left) {
      // Tab is to the left of visible area
      tabsContainer.scrollLeft -= containerRect.left - tabRect.left + 20;
    } else if (tabRect.right > containerRect.right) {
      // Tab is to the right of visible area
      tabsContainer.scrollLeft += tabRect.right - containerRect.right + 20;
    }
  }
  
  onMount(() => {
    checkScrollButtons();
    ensureActiveTabVisible();
  });
  
  afterUpdate(() => {
    checkScrollButtons();
  });
</script>

<!-- Buffer tabs -->
<div class="bg-base-200 px-2 py-0.5">
  <div class="flex items-center gap-1 h-8">
    <!-- Left scroll arrow -->
    {#if canScrollLeft}
      <button
        class="btn btn-xs btn-ghost scroll-arrow-left"
        on:click={() => scrollTabs('left')}
        title="Scroll tabs left"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
        </svg>
      </button>
    {/if}
    
    <!-- Scrollable tabs container -->
    <div class="flex-1 overflow-hidden">
      <div 
        class="flex items-center gap-1 overflow-x-auto scrollbar-hide"
        bind:this={tabsContainer}
        on:scroll={checkScrollButtons}
      >
        {#each tabs as buffer}
          <button
            class="tab tab-lifted flex-shrink-0 {activeTabId === buffer.id ? 'tab-active' : ''} {buffer.isStartupFile ? 'startup-file' : ''}"
            on:click={() => switchTab(buffer.id)}
            on:dblclick={() => startEditingBufferName(buffer.id)}
            title={buffer.isStartupFile ? 'Startup File - Will run when Renardo starts' : buffer.name}
          >
            {#if buffer.editing}
              <input
                id="buffer-name-input-{buffer.id}"
                type="text"
                class="bg-transparent outline-none w-24"
                bind:value={buffer.editingName}
                on:keydown={(e) => {
                  if (e.key === 'Enter') {
                    finishEditingBufferName(buffer.id, buffer);
                  } else if (e.key === 'Escape') {
                    cancelEditingBufferName(buffer.id);
                  }
                }}
                on:blur={() => finishEditingBufferName(buffer.id, buffer)}
                on:click|stopPropagation
              />
            {:else}
              {#if buffer.isStartupFile}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1 inline-block" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clip-rule="evenodd" />
                </svg>
              {/if}
              {buffer.name}
            {/if}
            {#if !buffer.isStartupFile && tabs.length > 1}
              <button
                class="ml-2 w-4 h-4 rounded-full hover:bg-base-300 flex items-center justify-center text-xs"
                on:click|stopPropagation={() => confirmCloseBuffer(buffer.id)}
              >
                ×
              </button>
            {/if}
          </button>
        {/each}
      </div>
    </div>
    
    <!-- Right scroll arrow -->
    {#if canScrollRight}
      <button
        class="btn btn-xs btn-ghost scroll-arrow-right"
        on:click={() => scrollTabs('right')}
        title="Scroll tabs right"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
        </svg>
      </button>
    {/if}
    
    <!-- New Buffer button - Always visible -->
    <button
      class="tab tab-lifted"
      on:click={openNewBufferModal}
      title="New Buffer"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clip-rule="evenodd" />
      </svg>
    </button>
    
    <!-- Right Panel Toggle -->
    <button
      class="btn btn-sm btn-outline ml-2"
      on:click={toggleRightPanel}
      title="{rightPanelOpen ? 'Close' : 'Open'} side panel"
    >
      {#if rightPanelOpen}
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L12.586 11H5a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg>
      {:else}
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M9.707 14.707a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 1.414L7.414 9H15a1 1 0 110 2H7.414l2.293 2.293a1 1 0 010 1.414z" clip-rule="evenodd" />
        </svg>
      {/if}
      {rightPanelOpen ? 'Hide' : 'Show'} Panel
    </button>
  </div>
</div>

<style>
  /* Style for buffer tabs */
  .tab-lifted {
    padding: 0.125rem 0.75rem;
    margin-right: 0.25rem;
    font-size: 0.8rem;
    height: 2rem;
    display: flex;
    align-items: center;
    white-space: nowrap;
  }
  
  .tab-active {
    background-color: oklch(var(--b1));
  }
  
  /* Startup file tab styling */
  .startup-file {
    background-color: oklch(var(--p) / 0.2); /* Primary color with some transparency */
    border-bottom: 2px solid oklch(var(--p)); /* Primary color border bottom */
    font-weight: bold;
  }
  
  .startup-file.tab-active {
    background-color: oklch(var(--p) / 0.3); /* Slightly darker when active */
  }
  
  /* Hide scrollbar but keep functionality */
  .scrollbar-hide {
    -ms-overflow-style: none;  /* IE and Edge */
    scrollbar-width: none;  /* Firefox */
  }
  
  .scrollbar-hide::-webkit-scrollbar {
    display: none;  /* Chrome, Safari and Opera */
  }
  
  /* Scroll arrow buttons */
  .scroll-arrow-left,
  .scroll-arrow-right {
    flex-shrink: 0;
    padding: 0.25rem;
    min-height: 1.75rem;
    height: 1.75rem;
  }
  
  /* Smooth scroll behavior */
  .overflow-x-auto {
    scroll-behavior: smooth;
  }
</style>