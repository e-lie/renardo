<script>
  import { onMount, onDestroy } from 'svelte';
  import { LayoutManager } from './lib/newEditor/index';
  
  // Create layout manager instance
  let layoutManager = null;
  
  // Layout state
  let panes = [];
  let isResizing = false;
  let showLayoutModal = false;
  let hideAppNavbar = false;
  
  // Track pane visibility states
  let paneVisibility = {
    'top-menu': true,
    'left-top': true,
    'left-middle': true,
    'left-bottom': true,
    'right-top': true,
    'right-middle': true,
    'right-bottom': true,
    'bottom-left': true,
    'bottom-right': true
  };
  
  // Track pane sizes for resizing
  let paneSizes = {
    'left-top': 200,
    'left-middle': 200,
    'left-bottom': 200,
    'right-top': 200,
    'right-middle': 200,
    'right-bottom': 200,
    'bottom-left': 400,
    'bottom-right': 400
  };
  
  // Track container sizes
  let containerSizes = {
    'left-column': 300,
    'right-column': 300,
    'bottom-area': 200
  };
  
  // React to navbar visibility changes
  $: if (typeof window !== 'undefined') {
    window.dispatchEvent(new CustomEvent('navbarVisibilityChange', {
      detail: { hideNavbar: hideAppNavbar }
    }));
  }
  
  // Resize state
  let resizeData = null;

  // Subscribe to layout changes
  let unsubscribeLayout = null;
  let unsubscribePanes = [];

  onMount(() => {
    // Initialize layout manager
    layoutManager = new LayoutManager();
    
    // Dispatch initial navbar state
    window.dispatchEvent(new CustomEvent('navbarVisibilityChange', {
      detail: { hideNavbar: hideAppNavbar }
    }));
    
    // Subscribe to layout manager
    unsubscribeLayout = layoutManager.subscribe((state) => {
      panes = Array.from(state.panes.values());
      isResizing = state.isResizing;
      
      // Update visibility states
      for (const [position, pane] of state.panes) {
        if (paneVisibility.hasOwnProperty(pane.getState().position)) {
          paneVisibility[pane.getState().position] = pane.getState().isVisible;
        }
      }
    });

    // Subscribe to individual panes for reactive updates
    panes.forEach(pane => {
      const unsubscribe = pane.subscribe(() => {
        // Trigger reactivity
        panes = [...panes];
      });
      unsubscribePanes.push(unsubscribe);
    });
  });

  onDestroy(() => {
    unsubscribeLayout?.();
    unsubscribePanes.forEach(unsub => unsub());
  });

  // Resize handlers for flex layout
  function startResize(event, resizeType, direction) {
    event.preventDefault();
    if (!layoutManager) return;

    layoutManager.startResize();
    
    const startPos = direction === 'horizontal' ? event.clientX : event.clientY;
    let paneKey = null;
    let containerKey = null;
    let startSize = 0;
    
    // Map resize type to pane or container key
    switch(resizeType) {
      case 'left-top-resize':
        paneKey = 'left-top';
        startSize = paneSizes[paneKey];
        break;
      case 'left-middle-resize':
        paneKey = 'left-middle';
        startSize = paneSizes[paneKey];
        break;
      case 'right-top-resize':
        paneKey = 'right-top';
        startSize = paneSizes[paneKey];
        break;
      case 'right-middle-resize':
        paneKey = 'right-middle';
        startSize = paneSizes[paneKey];
        break;
      case 'bottom-horizontal-resize':
        paneKey = 'bottom-left';
        startSize = paneSizes[paneKey];
        break;
      case 'left-resize':
        containerKey = 'left-column';
        startSize = containerSizes[containerKey];
        break;
      case 'right-resize':
        containerKey = 'right-column';
        startSize = containerSizes[containerKey];
        break;
      case 'bottom-resize':
        containerKey = 'bottom-area';
        startSize = containerSizes[containerKey];
        break;
    }
    
    resizeData = {
      resizeType,
      direction,
      startPos,
      startSize,
      paneKey,
      containerKey
    };

    document.addEventListener('mousemove', handleResize);
    document.addEventListener('mouseup', endResize);
  }

  function handleResize(event) {
    if (!resizeData || !layoutManager) return;

    const { resizeType, direction, startPos, startSize, paneKey, containerKey } = resizeData;
    const currentPos = direction === 'horizontal' ? event.clientX : event.clientY;
    let delta = currentPos - startPos;
    
    // Invert delta for right-side and bottom panels
    if (resizeType === 'right-resize' || resizeType === 'bottom-resize') {
      delta = -delta;
    }
    
    const newSize = Math.max(100, startSize + delta); // Minimum size of 100px

    // Update the appropriate size in our state
    if (paneKey) {
      paneSizes[paneKey] = newSize;
      // Trigger reactivity
      paneSizes = { ...paneSizes };
    } else if (containerKey) {
      containerSizes[containerKey] = newSize;
      // Trigger reactivity
      containerSizes = { ...containerSizes };
    }
  }

  function endResize() {
    if (!resizeData) return;
    
    if (layoutManager) {
      layoutManager.endResize();
    }
    resizeData = null;

    document.removeEventListener('mousemove', handleResize);
    document.removeEventListener('mouseup', endResize);
  }

  // Tab handlers
  function switchToTab(paneId, tabId) {
    if (layoutManager) {
      layoutManager.switchToTab(paneId, tabId);
    }
  }

  function closeTab(paneId, tabId) {
    if (layoutManager) {
      layoutManager.removeTabFromPane(paneId, tabId);
    }
  }

  // Get pane style based on position and dimensions
  function getPaneStyle(pane) {
    const state = pane.getState();
    const dims = state.dimensions;
    let style = '';

    if (dims.width) style += `width: ${dims.width}px; `;
    if (dims.height) style += `height: ${dims.height}px; `;
    if (dims.minWidth) style += `min-width: ${dims.minWidth}px; `;
    if (dims.minHeight) style += `min-height: ${dims.minHeight}px; `;
    if (dims.maxWidth) style += `max-width: ${dims.maxWidth}px; `;
    if (dims.maxHeight) style += `max-height: ${dims.maxHeight}px; `;

    return style;
  }

  // Component rendering helpers
  function renderComponent(componentType, props) {
    switch (componentType) {
      case 'TopMenu':
        return { component: null, content: '🍔 Menu Bar' };
      case 'EditorPlaceholder':
        return { component: null, content: '📝 Code Editor (Coming Soon)' };
      default:
        return { component: null, content: `📦 ${componentType}` };
    }
  }

  // Get pane background color based on position
  function getPaneColor(position) {
    const colors = {
      'top-menu': 'bg-base-300',
      'left-top': 'bg-primary/10',
      'left-middle': 'bg-primary/20',
      'left-bottom': 'bg-secondary/10',
      'right-top': 'bg-accent/10',
      'right-middle': 'bg-accent/20',
      'right-bottom': 'bg-info/10',
      'bottom-left': 'bg-success/10',
      'bottom-right': 'bg-warning/10',
      'center': 'bg-base-200'
    };
    return colors[position] || 'bg-base-100';
  }
</script>

<div class="new-code-editor {hideAppNavbar ? 'h-screen' : 'h-full'} bg-base-100 overflow-hidden flex flex-col">
  <!-- Top Menu Bar -->
  {#if paneVisibility['top-menu']}
    <div class="top-menu {getPaneColor('top-menu')} p-3 flex items-center justify-center text-sm font-semibold border-b border-base-300" style="height: 60px; flex-shrink: 0;">
      🍔 Top Menu Bar
    </div>
  {/if}

  <!-- Main Content Area -->
  <div class="flex flex-grow overflow-hidden">
    <!-- Left Side -->
    {#if paneVisibility['left-top'] || paneVisibility['left-middle'] || paneVisibility['left-bottom']}
      <div class="flex flex-col h-full" style="width: {containerSizes['left-column']}px; min-width: 200px;">
        <!-- Left Top Pane -->
        {#if paneVisibility['left-top']}
          <div 
            class="{getPaneColor('left-top')} p-4 flex items-center justify-center text-sm border-r border-base-300"
            style="height: {paneSizes['left-top']}px; min-height: 100px;"
          >
            🔵 Left Top Pane
          </div>
        {/if}
        
        <!-- Resize Handle between Top and Middle -->
        {#if paneVisibility['left-top'] && (paneVisibility['left-middle'] || paneVisibility['left-bottom'])}
          <div 
            class="h-1 bg-base-300 cursor-row-resize hover:bg-primary/30 transition-colors"
            on:mousedown={(e) => startResize(e, 'left-top-resize', 'vertical')}
          ></div>
        {/if}
        
        <!-- Left Middle Pane -->
        {#if paneVisibility['left-middle']}
          <div 
            class="{getPaneColor('left-middle')} p-4 flex items-center justify-center text-sm border-r border-base-300"
            style="{paneVisibility['left-top'] || paneVisibility['left-bottom'] ? `height: ${paneSizes['left-middle']}px; min-height: 100px;` : 'flex: 1;'}"
          >
            🟦 Left Middle Pane
          </div>
        {/if}
        
        <!-- Resize Handle between Middle and Bottom -->
        {#if paneVisibility['left-middle'] && paneVisibility['left-bottom']}
          <div 
            class="h-1 bg-base-300 cursor-row-resize hover:bg-primary/30 transition-colors"
            on:mousedown={(e) => startResize(e, 'left-middle-resize', 'vertical')}
          ></div>
        {/if}
        
        <!-- Left Bottom Pane -->
        {#if paneVisibility['left-bottom']}
          <div 
            class="{getPaneColor('left-bottom')} p-4 flex items-center justify-center text-sm border-r border-base-300"
            style="{paneVisibility['left-top'] || paneVisibility['left-middle'] ? `flex: 1; min-height: 100px;` : 'flex: 1;'}"
          >
            🟢 Left Bottom Pane
          </div>
        {/if}
      </div>
    {/if}

    <!-- Vertical Resize Handle (only show if left side has visible panes) -->
    {#if paneVisibility['left-top'] || paneVisibility['left-middle'] || paneVisibility['left-bottom']}
      <div 
        class="w-1 bg-base-300 cursor-col-resize hover:bg-primary/30 transition-colors"
        on:mousedown={(e) => startResize(e, 'left-resize', 'horizontal')}
      ></div>
    {/if}

    <!-- Center Area -->
    <div class="flex flex-col flex-1 h-full">
      <!-- Center Pane (always visible) -->
      <div class="flex-1 {getPaneColor('center')} p-8 flex items-center justify-center text-lg font-semibold">
        📝 Code Editor Area
      </div>
      
      <!-- Horizontal Resize Handle (only show if bottom panes are visible) -->
      {#if paneVisibility['bottom-left'] || paneVisibility['bottom-right']}
        <div 
          class="h-1 bg-base-300 cursor-row-resize hover:bg-primary/30 transition-colors"
          on:mousedown={(e) => startResize(e, 'bottom-resize', 'vertical')}
        ></div>
      {/if}
      
      <!-- Bottom Area -->
      {#if paneVisibility['bottom-left'] || paneVisibility['bottom-right']}
        <div class="flex" style="height: {containerSizes['bottom-area']}px; min-height: 150px;">
          <!-- Bottom Left -->
          {#if paneVisibility['bottom-left']}
            <div 
              class="{getPaneColor('bottom-left')} p-4 flex items-center justify-center text-sm border-r border-base-300"
              style="{paneVisibility['bottom-right'] ? `width: ${paneSizes['bottom-left']}px; min-width: 200px;` : 'flex: 1;'}"
            >
              🟡 Bottom Left
            </div>
          {/if}
          
          <!-- Vertical Resize Handle (only show if both bottom panes are visible) -->
          {#if paneVisibility['bottom-left'] && paneVisibility['bottom-right']}
            <div 
              class="w-1 bg-base-300 cursor-col-resize hover:bg-primary/30 transition-colors"
              on:mousedown={(e) => startResize(e, 'bottom-horizontal-resize', 'horizontal')}
            ></div>
          {/if}
          
          <!-- Bottom Right -->
          {#if paneVisibility['bottom-right']}
            <div 
              class="{getPaneColor('bottom-right')} p-4 flex items-center justify-center text-sm"
              style="flex: 1; min-width: 200px;"
            >
              🟠 Bottom Right
            </div>
          {/if}
        </div>
      {/if}
    </div>

    <!-- Vertical Resize Handle (only show if right side has visible panes) -->
    {#if paneVisibility['right-top'] || paneVisibility['right-middle'] || paneVisibility['right-bottom']}
      <div 
        class="w-1 bg-base-300 cursor-col-resize hover:bg-primary/30 transition-colors"
        on:mousedown={(e) => startResize(e, 'right-resize', 'horizontal')}
      ></div>
    {/if}

    <!-- Right Side -->
    {#if paneVisibility['right-top'] || paneVisibility['right-middle'] || paneVisibility['right-bottom']}
      <div class="flex flex-col h-full" style="width: {containerSizes['right-column']}px; min-width: 200px;">
        <!-- Right Top Pane -->
        {#if paneVisibility['right-top']}
          <div 
            class="{getPaneColor('right-top')} p-4 flex items-center justify-center text-sm border-l border-base-300"
            style="height: {paneSizes['right-top']}px; min-height: 100px;"
          >
            🔴 Right Top Pane
          </div>
        {/if}
        
        <!-- Resize Handle between Top and Middle -->
        {#if paneVisibility['right-top'] && (paneVisibility['right-middle'] || paneVisibility['right-bottom'])}
          <div 
            class="h-1 bg-base-300 cursor-row-resize hover:bg-primary/30 transition-colors"
            on:mousedown={(e) => startResize(e, 'right-top-resize', 'vertical')}
          ></div>
        {/if}
        
        <!-- Right Middle Pane -->
        {#if paneVisibility['right-middle']}
          <div 
            class="{getPaneColor('right-middle')} p-4 flex items-center justify-center text-sm border-l border-base-300"
            style="{paneVisibility['right-top'] || paneVisibility['right-bottom'] ? `height: ${paneSizes['right-middle']}px; min-height: 100px;` : 'flex: 1;'}"
          >
            🟥 Right Middle Pane
          </div>
        {/if}
        
        <!-- Resize Handle between Middle and Bottom -->
        {#if paneVisibility['right-middle'] && paneVisibility['right-bottom']}
          <div 
            class="h-1 bg-base-300 cursor-row-resize hover:bg-primary/30 transition-colors"
            on:mousedown={(e) => startResize(e, 'right-middle-resize', 'vertical')}
          ></div>
        {/if}
        
        <!-- Right Bottom Pane -->
        {#if paneVisibility['right-bottom']}
          <div 
            class="{getPaneColor('right-bottom')} p-4 flex items-center justify-center text-sm border-l border-base-300"
            style="{paneVisibility['right-top'] || paneVisibility['right-middle'] ? `flex: 1; min-height: 100px;` : 'flex: 1;'}"
          >
            🟣 Right Bottom Pane
          </div>
        {/if}
      </div>
    {/if}
  </div>
  
  <!-- Floating Layout Configuration Button -->
  <button 
    class="fixed top-4 right-4 btn btn-circle btn-primary shadow-lg z-50"
    on:click={() => showLayoutModal = true}
    title="Configure Layout"
  >
    <!-- Window Icon SVG -->
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
      <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z" />
    </svg>
  </button>

  <!-- Layout Configuration Modal -->
  {#if showLayoutModal}
    <div class="modal modal-open">
      <div class="modal-box max-w-4xl h-[80vh] flex flex-col">
        <!-- Modal Header -->
        <div class="flex justify-between items-center mb-4">
          <h3 class="font-bold text-lg">Layout Configuration</h3>
          <button 
            class="btn btn-sm btn-circle btn-ghost"
            on:click={() => showLayoutModal = false}
          >
            ✕
          </button>
        </div>
        
        <!-- Modal Content -->
        <div class="flex-1 overflow-y-auto">
          <!-- Pane Visibility Controls -->
          <div class="space-y-4">
            <!-- App Navigation Bar -->
            <div class="divider">App Navigation</div>
            <div class="form-control">
              <label class="label cursor-pointer">
                <span class="label-text font-semibold">Hide App Navigation Bar</span>
                <input 
                  type="checkbox" 
                  class="toggle toggle-primary"
                  bind:checked={hideAppNavbar}
                />
              </label>
              <span class="label-text-alt pl-12 text-xs opacity-70">Hides the top navigation bar from the main app</span>
            </div>
            
            <div class="divider">Pane Layout</div>
            
            <!-- Layout Grid matching the actual pane positions -->
            <div class="grid grid-cols-3 gap-2 p-4 bg-base-200 rounded-lg">
              <!-- Top Row -->
              <div class="col-span-3 flex justify-center">
                <div class="form-control">
                  <label class="label cursor-pointer flex-col gap-1">
                    <span class="label-text text-xs font-semibold">Top Menu</span>
                    <input 
                      type="checkbox" 
                      class="toggle toggle-primary toggle-xs"
                      checked={paneVisibility['top-menu']}
                      on:change={(e) => {
                        paneVisibility['top-menu'] = e.target.checked;
                        paneVisibility = { ...paneVisibility };
                      }}
                    />
                  </label>
                </div>
              </div>
              
              <!-- Middle Row -->
              <div class="flex flex-col gap-1">
                <!-- Left Column -->
                <div class="form-control">
                  <label class="label cursor-pointer flex-col gap-1">
                    <span class="label-text text-xs font-semibold">Left Top</span>
                    <input 
                      type="checkbox" 
                      class="toggle toggle-primary toggle-xs"
                      checked={paneVisibility['left-top']}
                      on:change={(e) => {
                        paneVisibility['left-top'] = e.target.checked;
                        paneVisibility = { ...paneVisibility };
                      }}
                    />
                  </label>
                </div>
                <div class="form-control">
                  <label class="label cursor-pointer flex-col gap-1">
                    <span class="label-text text-xs font-semibold">Left Mid</span>
                    <input 
                      type="checkbox" 
                      class="toggle toggle-primary toggle-xs"
                      checked={paneVisibility['left-middle']}
                      on:change={(e) => {
                        paneVisibility['left-middle'] = e.target.checked;
                        paneVisibility = { ...paneVisibility };
                      }}
                    />
                  </label>
                </div>
                <div class="form-control">
                  <label class="label cursor-pointer flex-col gap-1">
                    <span class="label-text text-xs font-semibold">Left Bot</span>
                    <input 
                      type="checkbox" 
                      class="toggle toggle-primary toggle-xs"
                      checked={paneVisibility['left-bottom']}
                      on:change={(e) => {
                        paneVisibility['left-bottom'] = e.target.checked;
                        paneVisibility = { ...paneVisibility };
                      }}
                    />
                  </label>
                </div>
              </div>
              
              <div class="flex items-center justify-center">
                <!-- Center Area (always visible) -->
                <div class="form-control">
                  <label class="label cursor-pointer flex-col gap-1">
                    <span class="label-text text-xs font-semibold text-center">Center<br/>Editor</span>
                    <div class="w-8 h-4 bg-primary/30 rounded flex items-center justify-center">
                      <span class="text-xs">📝</span>
                    </div>
                  </label>
                </div>
              </div>
              
              <div class="flex flex-col gap-1">
                <!-- Right Column -->
                <div class="form-control">
                  <label class="label cursor-pointer flex-col gap-1">
                    <span class="label-text text-xs font-semibold">Right Top</span>
                    <input 
                      type="checkbox" 
                      class="toggle toggle-primary toggle-xs"
                      checked={paneVisibility['right-top']}
                      on:change={(e) => {
                        paneVisibility['right-top'] = e.target.checked;
                        paneVisibility = { ...paneVisibility };
                      }}
                    />
                  </label>
                </div>
                <div class="form-control">
                  <label class="label cursor-pointer flex-col gap-1">
                    <span class="label-text text-xs font-semibold">Right Mid</span>
                    <input 
                      type="checkbox" 
                      class="toggle toggle-primary toggle-xs"
                      checked={paneVisibility['right-middle']}
                      on:change={(e) => {
                        paneVisibility['right-middle'] = e.target.checked;
                        paneVisibility = { ...paneVisibility };
                      }}
                    />
                  </label>
                </div>
                <div class="form-control">
                  <label class="label cursor-pointer flex-col gap-1">
                    <span class="label-text text-xs font-semibold">Right Bot</span>
                    <input 
                      type="checkbox" 
                      class="toggle toggle-primary toggle-xs"
                      checked={paneVisibility['right-bottom']}
                      on:change={(e) => {
                        paneVisibility['right-bottom'] = e.target.checked;
                        paneVisibility = { ...paneVisibility };
                      }}
                    />
                  </label>
                </div>
              </div>
              
              <!-- Bottom Row -->
              <div class="col-span-3 grid grid-cols-2 gap-2 mt-2">
                <div class="form-control">
                  <label class="label cursor-pointer flex-col gap-1">
                    <span class="label-text text-xs font-semibold">Bottom Left</span>
                    <input 
                      type="checkbox" 
                      class="toggle toggle-primary toggle-xs"
                      checked={paneVisibility['bottom-left']}
                      on:change={(e) => {
                        paneVisibility['bottom-left'] = e.target.checked;
                        paneVisibility = { ...paneVisibility };
                      }}
                    />
                  </label>
                </div>
                <div class="form-control">
                  <label class="label cursor-pointer flex-col gap-1">
                    <span class="label-text text-xs font-semibold">Bottom Right</span>
                    <input 
                      type="checkbox" 
                      class="toggle toggle-primary toggle-xs"
                      checked={paneVisibility['bottom-right']}
                      on:change={(e) => {
                        paneVisibility['bottom-right'] = e.target.checked;
                        paneVisibility = { ...paneVisibility };
                      }}
                    />
                  </label>
                </div>
              </div>
            </div>
            
            <!-- Note about center pane -->
            <div class="alert alert-info">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
              <span>The center code editor pane cannot be hidden.</span>
            </div>
          </div>
        </div>
        
        <!-- Modal Actions -->
        <div class="modal-action">
          <button 
            class="btn btn-primary"
            on:click={() => layoutManager && layoutManager.resetToDefault()}
          >
            Reset to Default
          </button>
          <button 
            class="btn"
            on:click={() => showLayoutModal = false}
          >
            Close
          </button>
        </div>
      </div>
      
      <!-- Modal backdrop -->
      <div class="modal-backdrop" on:click={() => showLayoutModal = false}></div>
    </div>
  {/if}
</div>

<style>
  .pane {
    position: relative;
  }
  
  .resize-handle {
    z-index: 10;
  }
  
  .resize-handle:hover {
    background-color: oklch(var(--p) / 0.2);
  }
  
  /* Custom grid areas for better positioning */
  .editor-layout {
    height: 100vh;
    background: oklch(var(--b1));
  }
  
  /* Smooth transitions for non-resizing states */
  .pane:not(.resizing) {
    transition: width 0.2s ease, height 0.2s ease;
  }
  
  /* Tab styling improvements */
  .tab {
    transition: all 0.2s ease;
  }
  
  .tab:hover {
    background-color: oklch(var(--b3));
  }
  
  .tab-active {
    background-color: oklch(var(--p));
    color: oklch(var(--pc));
  }
</style>