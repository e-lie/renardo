<script>
  import { onMount, onDestroy } from 'svelte';
  import { LayoutManager } from './lib/newEditor/index';
  
  // Create layout manager instance
  let layoutManager = null;
  
  // Layout state
  let panes = [];
  let isResizing = false;
  
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
    const delta = currentPos - startPos;
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

<div class="new-code-editor h-screen bg-base-100 overflow-hidden">
  <!-- Top Menu Bar -->
  {#if layoutManager}
    {@const topMenuPane = layoutManager.getPaneByPosition('top-menu')}
    {#if topMenuPane && topMenuPane.getState().isVisible}
      <div class="top-menu {getPaneColor('top-menu')} p-3 flex items-center justify-center text-sm font-semibold border-b border-base-300">
        🍔 Top Menu Bar
      </div>
    {/if}
  {/if}

  <!-- Main Content Area -->
  <div class="flex flex-1 overflow-hidden">
    <!-- Left Side -->
    <div class="flex flex-col" style="width: 300px; min-width: 200px;">
      <!-- Left Top Pane -->
      {#if layoutManager}
        {@const leftTopPane = layoutManager.getPaneByPosition('left-top')}
        {#if leftTopPane && leftTopPane.getState().isVisible}
          <div class="flex-1 {getPaneColor('left-top')} p-4 flex items-center justify-center text-sm border-r border-b border-base-300">
            🔵 Left Top Pane
          </div>
        {/if}
      {/if}
      
      <!-- Horizontal Resize Handle -->
      <div 
        class="h-1 bg-base-300 cursor-row-resize hover:bg-primary/30 transition-colors"
        on:mousedown={(e) => startResize(e, 'left-vertical', 'vertical')}
      ></div>
      
      <!-- Left Bottom Pane -->
      {#if layoutManager}
        {@const leftBottomPane = layoutManager.getPaneByPosition('left-bottom')}
        {#if leftBottomPane && leftBottomPane.getState().isVisible}
          <div class="flex-1 {getPaneColor('left-bottom')} p-4 flex items-center justify-center text-sm border-r border-base-300">
            🟢 Left Bottom Pane
          </div>
        {/if}
      {/if}
    </div>

    <!-- Vertical Resize Handle -->
    <div 
      class="w-1 bg-base-300 cursor-col-resize hover:bg-primary/30 transition-colors"
      on:mousedown={(e) => startResize(e, 'left-resize', 'horizontal')}
    ></div>

    <!-- Center Area -->
    <div class="flex flex-col flex-1" style="min-height: 500px;">
      <!-- Center Pane -->
      {#if layoutManager}
        {@const centerPane = layoutManager.getPaneByPosition('center')}
        {#if centerPane && centerPane.getState().isVisible}
          <div class="flex-1 {getPaneColor('center')} p-8 flex items-center justify-center text-lg font-semibold">
            📝 Code Editor Area
          </div>
        {/if}
      {/if}
      
      <!-- Horizontal Resize Handle -->
      <div 
        class="h-1 bg-base-300 cursor-row-resize hover:bg-primary/30 transition-colors"
        on:mousedown={(e) => startResize(e, 'bottom-resize', 'vertical')}
      ></div>
      
      <!-- Bottom Area -->
      <div class="flex" style="height: 200px; min-height: 150px;">
        <!-- Bottom Left -->
        {#if layoutManager}
          {@const bottomLeftPane = layoutManager.getPaneByPosition('bottom-left')}
          {#if bottomLeftPane && bottomLeftPane.getState().isVisible}
            <div class="flex-1 {getPaneColor('bottom-left')} p-4 flex items-center justify-center text-sm border-r border-base-300">
              🟡 Bottom Left
            </div>
          {/if}
        {/if}
        
        <!-- Vertical Resize Handle -->
        <div 
          class="w-1 bg-base-300 cursor-col-resize hover:bg-primary/30 transition-colors"
          on:mousedown={(e) => startResize(e, 'bottom-horizontal', 'horizontal')}
        ></div>
        
        <!-- Bottom Right -->
        {#if layoutManager}
          {@const bottomRightPane = layoutManager.getPaneByPosition('bottom-right')}
          {#if bottomRightPane && bottomRightPane.getState().isVisible}
            <div class="flex-1 {getPaneColor('bottom-right')} p-4 flex items-center justify-center text-sm">
              🟠 Bottom Right
            </div>
          {/if}
        {/if}
      </div>
    </div>

    <!-- Vertical Resize Handle -->
    <div 
      class="w-1 bg-base-300 cursor-col-resize hover:bg-primary/30 transition-colors"
      on:mousedown={(e) => startResize(e, 'right-resize', 'horizontal')}
    ></div>

    <!-- Right Side -->
    <div class="flex flex-col" style="width: 300px; min-width: 200px;">
      <!-- Right Top Pane -->
      {#if layoutManager}
        {@const rightTopPane = layoutManager.getPaneByPosition('right-top')}
        {#if rightTopPane && rightTopPane.getState().isVisible}
          <div class="flex-1 {getPaneColor('right-top')} p-4 flex items-center justify-center text-sm border-l border-b border-base-300">
            🔴 Right Top Pane
          </div>
        {/if}
      {/if}
      
      <!-- Horizontal Resize Handle -->
      <div 
        class="h-1 bg-base-300 cursor-row-resize hover:bg-primary/30 transition-colors"
        on:mousedown={(e) => startResize(e, 'right-vertical', 'vertical')}
      ></div>
      
      <!-- Right Bottom Pane -->
      {#if layoutManager}
        {@const rightBottomPane = layoutManager.getPaneByPosition('right-bottom')}
        {#if rightBottomPane && rightBottomPane.getState().isVisible}
          <div class="flex-1 {getPaneColor('right-bottom')} p-4 flex items-center justify-center text-sm border-l border-base-300">
            🟣 Right Bottom Pane
          </div>
        {/if}
      {/if}
    </div>
  </div>
  
  <!-- Debug Panel (temporary) -->
  <div class="fixed bottom-4 right-4 bg-base-300 p-4 rounded-lg shadow-lg max-w-sm">
    <h3 class="font-bold text-sm mb-2">Layout Debug</h3>
    <div class="text-xs space-y-1">
      <div>Panes: {panes.length}</div>
      <div>Resizing: {isResizing ? 'Yes' : 'No'}</div>
      <div class="mt-2">
        <button 
          class="btn btn-xs btn-primary"
          on:click={() => layoutManager && layoutManager.resetToDefault()}
        >
          Reset Layout
        </button>
      </div>
    </div>
  </div>
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