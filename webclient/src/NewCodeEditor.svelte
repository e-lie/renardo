<script>
  import { onMount, onDestroy } from 'svelte';
  import { LayoutManager } from './lib/newEditor/index';
  
  // Create layout manager instance
  let layoutManager = null;
  
  // Layout state
  let panes = [];
  let isResizing = false;
  let showLayoutModal = false;
  
  // Track pane visibility states
  let paneVisibility = {
    'top-menu': true,
    'left-top': true,
    'left-bottom': true,
    'right-top': true,
    'right-bottom': true,
    'bottom-left': true,
    'bottom-right': true
  };
  
  // Resize state
  let resizeData = null;

  // Subscribe to layout changes
  let unsubscribeLayout = null;
  let unsubscribePanes = [];

  onMount(() => {
    // Initialize layout manager
    layoutManager = new LayoutManager();
    
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
    let targetElement;
    
    // Get the appropriate element to resize based on type
    switch(resizeType) {
      case 'left-resize':
        targetElement = document.querySelector('.flex.flex-col[style*="width: 300px"]');
        break;
      case 'right-resize':
        targetElement = document.querySelectorAll('.flex.flex-col[style*="width: 300px"]')[1];
        break;
      case 'left-vertical':
        targetElement = document.querySelector('.flex.flex-col .flex-1:first-child');
        break;
      case 'right-vertical':
        targetElement = document.querySelector('.flex.flex-col:last-child .flex-1:first-child');
        break;
      case 'bottom-resize':
        targetElement = document.querySelector('.flex[style*="height: 200px"]');
        break;
      case 'bottom-horizontal':
        targetElement = document.querySelector('.flex[style*="height: 200px"] .flex-1:first-child');
        break;
    }
    
    if (!targetElement) return;
    
    resizeData = {
      resizeType,
      direction,
      startPos,
      startSize: direction === 'horizontal' ? 
        targetElement.offsetWidth : 
        targetElement.offsetHeight,
      element: targetElement
    };

    document.addEventListener('mousemove', handleResize);
    document.addEventListener('mouseup', endResize);
  }

  function handleResize(event) {
    if (!resizeData || !layoutManager) return;

    const { resizeType, direction, startPos, startSize, element } = resizeData;
    const currentPos = direction === 'horizontal' ? event.clientX : event.clientY;
    let delta = currentPos - startPos;
    
    // Invert delta for right-side and bottom panels
    if (resizeType === 'right-resize' || resizeType === 'bottom-resize') {
      delta = -delta;
    }
    
    const newSize = Math.max(100, startSize + delta); // Minimum size of 100px

    // Apply the resize to the DOM element directly for flex layout
    if (direction === 'horizontal') {
      element.style.width = `${newSize}px`;
    } else {
      element.style.height = `${newSize}px`;
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
      'left-bottom': 'bg-secondary/10',
      'right-top': 'bg-accent/10',
      'right-bottom': 'bg-info/10',
      'bottom-left': 'bg-success/10',
      'bottom-right': 'bg-warning/10',
      'center': 'bg-base-200'
    };
    return colors[position] || 'bg-base-100';
  }
</script>

<div class="new-code-editor h-screen bg-base-100 overflow-hidden flex flex-col">
  <!-- Top Menu Bar -->
  {#if paneVisibility['top-menu']}
    <div class="top-menu {getPaneColor('top-menu')} p-3 flex items-center justify-center text-sm font-semibold border-b border-base-300" style="height: 60px; flex-shrink: 0;">
      🍔 Top Menu Bar
    </div>
  {/if}

  <!-- Main Content Area -->
  <div class="flex flex-grow overflow-hidden">
    <!-- Left Side -->
    {#if paneVisibility['left-top'] || paneVisibility['left-bottom']}
      <div class="flex flex-col h-full" style="width: 300px; min-width: 200px;">
        <!-- Left Top Pane -->
        {#if paneVisibility['left-top']}
          <div class="flex-1 {getPaneColor('left-top')} p-4 flex items-center justify-center text-sm border-r border-base-300">
            🔵 Left Top Pane
          </div>
        {/if}
        
        <!-- Horizontal Resize Handle (only show if both panes are visible) -->
        {#if paneVisibility['left-top'] && paneVisibility['left-bottom']}
          <div 
            class="h-1 bg-base-300 cursor-row-resize hover:bg-primary/30 transition-colors"
            on:mousedown={(e) => startResize(e, 'left-vertical', 'vertical')}
          ></div>
        {/if}
        
        <!-- Left Bottom Pane -->
        {#if paneVisibility['left-bottom']}
          <div class="flex-1 {getPaneColor('left-bottom')} p-4 flex items-center justify-center text-sm border-r border-base-300">
            🟢 Left Bottom Pane
          </div>
        {/if}
      </div>
    {/if}

    <!-- Vertical Resize Handle (only show if left side has visible panes) -->
    {#if paneVisibility['left-top'] || paneVisibility['left-bottom']}
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
        <div class="flex" style="height: 200px; min-height: 150px;">
          <!-- Bottom Left -->
          {#if paneVisibility['bottom-left']}
            <div class="flex-1 {getPaneColor('bottom-left')} p-4 flex items-center justify-center text-sm border-r border-base-300">
              🟡 Bottom Left
            </div>
          {/if}
          
          <!-- Vertical Resize Handle (only show if both bottom panes are visible) -->
          {#if paneVisibility['bottom-left'] && paneVisibility['bottom-right']}
            <div 
              class="w-1 bg-base-300 cursor-col-resize hover:bg-primary/30 transition-colors"
              on:mousedown={(e) => startResize(e, 'bottom-horizontal', 'horizontal')}
            ></div>
          {/if}
          
          <!-- Bottom Right -->
          {#if paneVisibility['bottom-right']}
            <div class="flex-1 {getPaneColor('bottom-right')} p-4 flex items-center justify-center text-sm">
              🟠 Bottom Right
            </div>
          {/if}
        </div>
      {/if}
    </div>

    <!-- Vertical Resize Handle (only show if right side has visible panes) -->
    {#if paneVisibility['right-top'] || paneVisibility['right-bottom']}
      <div 
        class="w-1 bg-base-300 cursor-col-resize hover:bg-primary/30 transition-colors"
        on:mousedown={(e) => startResize(e, 'right-resize', 'horizontal')}
      ></div>
    {/if}

    <!-- Right Side -->
    {#if paneVisibility['right-top'] || paneVisibility['right-bottom']}
      <div class="flex flex-col h-full" style="width: 300px; min-width: 200px;">
        <!-- Right Top Pane -->
        {#if paneVisibility['right-top']}
          <div class="flex-1 {getPaneColor('right-top')} p-4 flex items-center justify-center text-sm border-l border-base-300">
            🔴 Right Top Pane
          </div>
        {/if}
        
        <!-- Horizontal Resize Handle (only show if both panes are visible) -->
        {#if paneVisibility['right-top'] && paneVisibility['right-bottom']}
          <div 
            class="h-1 bg-base-300 cursor-row-resize hover:bg-primary/30 transition-colors"
            on:mousedown={(e) => startResize(e, 'right-vertical', 'vertical')}
          ></div>
        {/if}
        
        <!-- Right Bottom Pane -->
        {#if paneVisibility['right-bottom']}
          <div class="flex-1 {getPaneColor('right-bottom')} p-4 flex items-center justify-center text-sm border-l border-base-300">
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
            <div class="divider">Pane Visibility</div>
            
            <!-- Top Menu -->
            <div class="form-control">
              <label class="label cursor-pointer">
                <span class="label-text font-semibold">Top Menu</span>
                <input 
                  type="checkbox" 
                  class="toggle toggle-primary"
                  checked={paneVisibility['top-menu']}
                  on:change={(e) => {
                    const pane = layoutManager?.getPaneByPosition('top-menu');
                    if (pane) {
                      pane.setVisible(e.target.checked);
                      paneVisibility['top-menu'] = e.target.checked;
                    }
                  }}
                />
              </label>
            </div>
            
            <!-- Left Top -->
            <div class="form-control">
              <label class="label cursor-pointer">
                <span class="label-text font-semibold">Left Top</span>
                <input 
                  type="checkbox" 
                  class="toggle toggle-primary"
                  checked={paneVisibility['left-top']}
                  on:change={(e) => {
                    const pane = layoutManager?.getPaneByPosition('left-top');
                    if (pane) {
                      pane.setVisible(e.target.checked);
                      paneVisibility['left-top'] = e.target.checked;
                    }
                  }}
                />
              </label>
            </div>
            
            <!-- Left Bottom -->
            <div class="form-control">
              <label class="label cursor-pointer">
                <span class="label-text font-semibold">Left Bottom</span>
                <input 
                  type="checkbox" 
                  class="toggle toggle-primary"
                  checked={paneVisibility['left-bottom']}
                  on:change={(e) => {
                    const pane = layoutManager?.getPaneByPosition('left-bottom');
                    if (pane) {
                      pane.setVisible(e.target.checked);
                      paneVisibility['left-bottom'] = e.target.checked;
                    }
                  }}
                />
              </label>
            </div>
            
            <!-- Right Top -->
            <div class="form-control">
              <label class="label cursor-pointer">
                <span class="label-text font-semibold">Right Top</span>
                <input 
                  type="checkbox" 
                  class="toggle toggle-primary"
                  checked={paneVisibility['right-top']}
                  on:change={(e) => {
                    const pane = layoutManager?.getPaneByPosition('right-top');
                    if (pane) {
                      pane.setVisible(e.target.checked);
                      paneVisibility['right-top'] = e.target.checked;
                    }
                  }}
                />
              </label>
            </div>
            
            <!-- Right Bottom -->
            <div class="form-control">
              <label class="label cursor-pointer">
                <span class="label-text font-semibold">Right Bottom</span>
                <input 
                  type="checkbox" 
                  class="toggle toggle-primary"
                  checked={paneVisibility['right-bottom']}
                  on:change={(e) => {
                    const pane = layoutManager?.getPaneByPosition('right-bottom');
                    if (pane) {
                      pane.setVisible(e.target.checked);
                      paneVisibility['right-bottom'] = e.target.checked;
                    }
                  }}
                />
              </label>
            </div>
            
            <!-- Bottom Left -->
            <div class="form-control">
              <label class="label cursor-pointer">
                <span class="label-text font-semibold">Bottom Left</span>
                <input 
                  type="checkbox" 
                  class="toggle toggle-primary"
                  checked={paneVisibility['bottom-left']}
                  on:change={(e) => {
                    const pane = layoutManager?.getPaneByPosition('bottom-left');
                    if (pane) {
                      pane.setVisible(e.target.checked);
                      paneVisibility['bottom-left'] = e.target.checked;
                    }
                  }}
                />
              </label>
            </div>
            
            <!-- Bottom Right -->
            <div class="form-control">
              <label class="label cursor-pointer">
                <span class="label-text font-semibold">Bottom Right</span>
                <input 
                  type="checkbox" 
                  class="toggle toggle-primary"
                  checked={paneVisibility['bottom-right']}
                  on:change={(e) => {
                    const pane = layoutManager?.getPaneByPosition('bottom-right');
                    if (pane) {
                      pane.setVisible(e.target.checked);
                      paneVisibility['bottom-right'] = e.target.checked;
                    }
                  }}
                />
              </label>
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