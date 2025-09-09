<script>
  import { onMount, onDestroy } from 'svelte';
  import { LayoutManager, PaneComponent } from './lib/newEditor/index';
  import ColorPicker from './components/panes/ColorPicker.svelte';
  import TextArea from './components/panes/TextArea.svelte';
  import TabbedPane from './components/panes/TabbedPane.svelte';
  import LayoutConfigModal from './components/modals/LayoutConfigModal.svelte';
  
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

  // Track pane set visibility (independent from individual pane visibility)
  let paneSetVisibility = {
    'left': true,   // Controls entire left column (left-top, left-middle, left-bottom)
    'right': true,  // Controls entire right column (right-top, right-middle, right-bottom)
    'bottom': true  // Controls entire bottom area (bottom-left, bottom-right)
  };

  // Track hover states for showing/hiding buttons
  let hoverStates = {
    'left': false,
    'right': false,
    'bottom': false
  };


  // Pane tab configurations (each pane can have multiple tabs)
  let paneTabConfigs = {
    'top-menu': [
      { id: 'tab-top-menu-1', title: 'Menu', componentType: 'TextArea', componentId: 'menu-1', closable: false, active: true }
    ],
    'center': [
      { id: 'tab-center-1', title: 'Code Editor', componentType: 'CodeEditor', componentId: 'code-main', closable: false, active: true }
    ],
    'left-top': [
      { id: 'tab-left-top-1', title: 'Colors', componentType: 'ColorPicker', componentId: 'color-1', closable: false, active: true },
      { id: 'tab-left-top-2', title: 'Palette', componentType: 'ColorPicker', componentId: 'color-2', closable: true, active: false }
    ],
    'left-middle': [
      { id: 'tab-left-middle-1', title: 'Notes', componentType: 'TextArea', componentId: 'text-1', closable: false, active: true }
    ],
    'left-bottom': [
      { id: 'tab-left-bottom-1', title: 'Scratch', componentType: 'TextArea', componentId: 'text-scratch', closable: false, active: true },
      { id: 'tab-left-bottom-2', title: 'Colors', componentType: 'ColorPicker', componentId: 'color-scratch', closable: true, active: false }
    ],
    'right-top': [
      { id: 'tab-right-top-1', title: 'Workspace', componentType: 'TextArea', componentId: 'text-2', closable: false, active: true }
    ],
    'right-middle': [
      { id: 'tab-right-middle-1', title: 'Shared Colors', componentType: 'ColorPicker', componentId: 'color-3', closable: false, active: true },
      { id: 'tab-right-middle-2', title: 'Tools', componentType: 'TextArea', componentId: 'text-tools', closable: true, active: false }
    ],
    'right-bottom': [
      { id: 'tab-right-bottom-1', title: 'Shared Notes', componentType: 'TextArea', componentId: 'text-3', closable: false, active: true }
    ],
    'bottom-left': [
      { id: 'tab-bottom-left-1', title: 'Draft', componentType: 'TextArea', componentId: 'text-4', closable: false, active: true },
      { id: 'tab-bottom-left-2', title: 'Debug', componentType: 'TextArea', componentId: 'text-debug', closable: true, active: false }
    ],
    'bottom-right': [
      { id: 'tab-bottom-right-1', title: 'Palette', componentType: 'ColorPicker', componentId: 'color-4', closable: false, active: true },
      { id: 'tab-bottom-right-2', title: 'Export', componentType: 'TextArea', componentId: 'text-export', closable: true, active: false }
    ]
  };

  // All panes now use tabbed containers by default - no need for individual component assignments
  
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
  $: if (typeof window !== 'undefined' && layoutManager) {
    window.dispatchEvent(new CustomEvent('navbarVisibilityChange', {
      detail: { hideNavbar: hideAppNavbar }
    }));
  }

  // Reactive pane content rendering (depends on paneTabConfigs changes)
  $: leftTopContent = (paneTabConfigs, renderPaneContent('left-top'));
  $: leftMiddleContent = (paneTabConfigs, renderPaneContent('left-middle'));
  $: leftBottomContent = (paneTabConfigs, renderPaneContent('left-bottom'));
  $: rightTopContent = (paneTabConfigs, renderPaneContent('right-top'));
  $: rightMiddleContent = (paneTabConfigs, renderPaneContent('right-middle'));
  $: rightBottomContent = (paneTabConfigs, renderPaneContent('right-bottom'));
  $: bottomLeftContent = (paneTabConfigs, renderPaneContent('bottom-left'));
  $: bottomRightContent = (paneTabConfigs, renderPaneContent('bottom-right'));
  
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
      // Note: Don't sync visibility states as we manage them locally
    });

    // Subscribe to individual panes for reactive updates
    panes.forEach(pane => {
      const unsubscribe = pane.subscribe(() => {
        // Trigger reactivity
        panes = [...panes];
      });
      unsubscribePanes.push(unsubscribe);
    });

    // Add global mouse move listener for edge detection
    document.addEventListener('mousemove', handleGlobalMouseMove);
  });

  onDestroy(() => {
    unsubscribeLayout?.();
    unsubscribePanes.forEach(unsub => unsub());
    document.removeEventListener('mousemove', handleGlobalMouseMove);
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

  // Helper function to render pane content (all panes use tabbed containers)
  function renderPaneContent(position) {
    const props = {
      position: position,
      initialTabs: paneTabConfigs[position] || []
    };
    
    const rendered = { component: TabbedPane, props };
    return { rendered };
  }


  // Toggle pane set visibility
  function togglePaneSet(setName) {
    paneSetVisibility[setName] = !paneSetVisibility[setName];
    // Trigger reactivity
    paneSetVisibility = { ...paneSetVisibility };
  }

  // Check if any pane in a set is individually visible
  function hasPanesVisible(setName) {
    if (setName === 'left') {
      return paneVisibility['left-top'] || paneVisibility['left-middle'] || paneVisibility['left-bottom'];
    } else if (setName === 'right') {
      return paneVisibility['right-top'] || paneVisibility['right-middle'] || paneVisibility['right-bottom'];
    } else if (setName === 'bottom') {
      return paneVisibility['bottom-left'] || paneVisibility['bottom-right'];
    }
    return false;
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

  // Handle mouse enter/leave for pane sets
  function handlePaneSetHover(paneSet, isHovering) {
    hoverStates[paneSet] = isHovering;
    // Trigger reactivity
    hoverStates = { ...hoverStates };
  }

  // Handle global mouse movement for edge detection
  function handleGlobalMouseMove(event) {
    const threshold = 20; // 20px threshold from edge
    const { clientX, clientY } = event;
    const { innerWidth, innerHeight } = window;

    // Left edge detection
    const nearLeftEdge = clientX <= threshold;
    if (nearLeftEdge && hasPanesVisible('left') && !paneSetVisibility['left']) {
      handlePaneSetHover('left', true);
    }

    // Right edge detection  
    const nearRightEdge = clientX >= innerWidth - threshold;
    if (nearRightEdge && hasPanesVisible('right') && !paneSetVisibility['right']) {
      handlePaneSetHover('right', true);
    }

    // Bottom edge detection
    const nearBottomEdge = clientY >= innerHeight - threshold;
    if (nearBottomEdge && hasPanesVisible('bottom') && !paneSetVisibility['bottom']) {
      handlePaneSetHover('bottom', true);
    }

    // Clear hover states when not near edges and pane set is hidden
    if (!nearLeftEdge && !paneSetVisibility['left']) {
      // Only clear if we're not hovering the button area
      const buttonArea = clientX <= 60; // Left button area
      if (!buttonArea) {
        handlePaneSetHover('left', false);
      }
    }
    
    if (!nearRightEdge && !paneSetVisibility['right']) {
      // Only clear if we're not hovering the button area
      const buttonArea = clientX >= innerWidth - 60; // Right button area
      if (!buttonArea) {
        handlePaneSetHover('right', false);
      }
    }
    
    if (!nearBottomEdge && !paneSetVisibility['bottom']) {
      // Only clear if we're not hovering the button area
      const buttonArea = clientY >= innerHeight - 60; // Bottom button area
      if (!buttonArea) {
        handlePaneSetHover('bottom', false);
      }
    }
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
    {#if paneSetVisibility['left'] && (paneVisibility['left-top'] || paneVisibility['left-middle'] || paneVisibility['left-bottom'])}
      <div 
        class="flex flex-col h-full" 
        style="width: {containerSizes['left-column']}px; min-width: 200px;"
        on:mouseenter={() => handlePaneSetHover('left', true)}
        on:mouseleave={() => handlePaneSetHover('left', false)}
      >
        <!-- Left Top Pane -->
        {#if paneVisibility['left-top']}
          <div 
            class="{getPaneColor('left-top')} border-r border-base-300 overflow-hidden"
            style="height: {paneSizes['left-top']}px; min-height: 100px;"
          >
            {#if leftTopContent.rendered.component}
              <svelte:component this={leftTopContent.rendered.component} {...leftTopContent.rendered.props} />
            {:else}
              <div class="p-4 flex items-center justify-center text-sm">
                {leftTopContent.rendered.content}
              </div>
            {/if}
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
            class="{getPaneColor('left-middle')} border-r border-base-300 overflow-hidden"
            style="{paneVisibility['left-top'] || paneVisibility['left-bottom'] ? `height: ${paneSizes['left-middle']}px; min-height: 100px;` : 'flex: 1;'}"
          >
            {#if leftMiddleContent.rendered.component}
              <svelte:component this={leftMiddleContent.rendered.component} {...leftMiddleContent.rendered.props} />
            {:else}
              <div class="p-4 flex items-center justify-center text-sm">
                {leftMiddleContent.rendered.content}
              </div>
            {/if}
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
            class="{getPaneColor('left-bottom')} border-r border-base-300 overflow-hidden"
            style="{paneVisibility['left-top'] || paneVisibility['left-middle'] ? `flex: 1; min-height: 100px;` : 'flex: 1;'}"
          >
            {#if leftBottomContent.rendered.component}
              <svelte:component this={leftBottomContent.rendered.component} {...leftBottomContent.rendered.props} />
            {:else}
              <div class="p-4 flex items-center justify-center text-sm">
                {leftBottomContent.rendered.content}
              </div>
            {/if}
          </div>
        {/if}
      </div>
    {/if}

    <!-- Vertical Resize Handle (only show if left side has visible panes) -->
    {#if paneSetVisibility['left'] && (paneVisibility['left-top'] || paneVisibility['left-middle'] || paneVisibility['left-bottom'])}
      <div 
        class="w-1 bg-base-300 cursor-col-resize hover:bg-primary/30 transition-colors"
        on:mousedown={(e) => startResize(e, 'left-resize', 'horizontal')}
      ></div>
    {/if}

    <!-- Center Area -->
    <div class="flex flex-col flex-1 h-full">
      <!-- Center Pane (always visible) -->
      <div class="flex-1 {getPaneColor('center')} overflow-hidden">
        <TabbedPane 
          position="center"
          initialTabs={paneTabConfigs['center'] || []}
        />
      </div>
      
      <!-- Horizontal Resize Handle (only show if bottom panes are visible) -->
      {#if paneSetVisibility['bottom'] && (paneVisibility['bottom-left'] || paneVisibility['bottom-right'])}
        <div 
          class="h-1 bg-base-300 cursor-row-resize hover:bg-primary/30 transition-colors"
          on:mousedown={(e) => startResize(e, 'bottom-resize', 'vertical')}
        ></div>
      {/if}
      
      <!-- Bottom Area -->
      {#if paneSetVisibility['bottom'] && (paneVisibility['bottom-left'] || paneVisibility['bottom-right'])}
        <div 
          class="flex" 
          style="height: {containerSizes['bottom-area']}px; min-height: 150px;"
          on:mouseenter={() => handlePaneSetHover('bottom', true)}
          on:mouseleave={() => handlePaneSetHover('bottom', false)}
        >
          <!-- Bottom Left -->
          {#if paneVisibility['bottom-left']}
            <div 
              class="{getPaneColor('bottom-left')} border-r border-base-300 overflow-hidden"
              style="{paneVisibility['bottom-right'] ? `width: ${paneSizes['bottom-left']}px; min-width: 200px;` : 'flex: 1;'}"
            >
              {#if bottomLeftContent.rendered.component}
                <svelte:component this={bottomLeftContent.rendered.component} {...bottomLeftContent.rendered.props} />
              {:else}
                <div class="p-4 flex items-center justify-center text-sm">
                  {bottomLeftContent.rendered.content}
                </div>
              {/if}
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
              class="{getPaneColor('bottom-right')} overflow-hidden"
              style="flex: 1; min-width: 200px;"
            >
              {#if bottomRightContent.rendered.component}
                <svelte:component this={bottomRightContent.rendered.component} {...bottomRightContent.rendered.props} />
              {:else}
                <div class="p-4 flex items-center justify-center text-sm">
                  {bottomRightContent.rendered.content}
                </div>
              {/if}
            </div>
          {/if}
        </div>
      {/if}
    </div>

    <!-- Vertical Resize Handle (only show if right side has visible panes) -->
    {#if paneSetVisibility['right'] && (paneVisibility['right-top'] || paneVisibility['right-middle'] || paneVisibility['right-bottom'])}
      <div 
        class="w-1 bg-base-300 cursor-col-resize hover:bg-primary/30 transition-colors"
        on:mousedown={(e) => startResize(e, 'right-resize', 'horizontal')}
      ></div>
    {/if}

    <!-- Right Side -->
    {#if paneSetVisibility['right'] && (paneVisibility['right-top'] || paneVisibility['right-middle'] || paneVisibility['right-bottom'])}
      <div 
        class="flex flex-col h-full" 
        style="width: {containerSizes['right-column']}px; min-width: 200px;"
        on:mouseenter={() => handlePaneSetHover('right', true)}
        on:mouseleave={() => handlePaneSetHover('right', false)}
      >
        <!-- Right Top Pane -->
        {#if paneVisibility['right-top']}
          <div 
            class="{getPaneColor('right-top')} border-l border-base-300 overflow-hidden"
            style="height: {paneSizes['right-top']}px; min-height: 100px;"
          >
            {#if rightTopContent.rendered.component}
              <svelte:component this={rightTopContent.rendered.component} {...rightTopContent.rendered.props} />
            {:else}
              <div class="p-4 flex items-center justify-center text-sm">
                {rightTopContent.rendered.content}
              </div>
            {/if}
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
            class="{getPaneColor('right-middle')} border-l border-base-300 overflow-hidden"
            style="{paneVisibility['right-top'] || paneVisibility['right-bottom'] ? `height: ${paneSizes['right-middle']}px; min-height: 100px;` : 'flex: 1;'}"
          >
            {#if rightMiddleContent.rendered.component}
              <svelte:component this={rightMiddleContent.rendered.component} {...rightMiddleContent.rendered.props} />
            {:else}
              <div class="p-4 flex items-center justify-center text-sm">
                {rightMiddleContent.rendered.content}
              </div>
            {/if}
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
            class="{getPaneColor('right-bottom')} border-l border-base-300 overflow-hidden"
            style="{paneVisibility['right-top'] || paneVisibility['right-middle'] ? `flex: 1; min-height: 100px;` : 'flex: 1;'}"
          >
            {#if rightBottomContent.rendered.component}
              <svelte:component this={rightBottomContent.rendered.component} {...rightBottomContent.rendered.props} />
            {:else}
              <div class="p-4 flex items-center justify-center text-sm">
                {rightBottomContent.rendered.content}
              </div>
            {/if}
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
  <LayoutConfigModal 
    bind:showModal={showLayoutModal}
    bind:paneVisibility={paneVisibility}
    bind:paneTabConfigs={paneTabConfigs}
    bind:hideAppNavbar={hideAppNavbar}
    bind:layoutManager={layoutManager}
  />

  <!-- Floating Pane Set Toggle Buttons -->
  
  <!-- Left Pane Set Toggle -->
  {#if hasPanesVisible('left') && hoverStates['left']}
    <button 
      class="floating-toggle-btn left-right fixed left-4 top-1/2 w-8 h-8 rounded-full bg-transparent border-2 border-primary text-primary shadow-xl z-50 flex items-center justify-center outline-none"
      on:click={() => togglePaneSet('left')}
      on:mouseenter={() => handlePaneSetHover('left', true)}
      on:mouseleave={() => handlePaneSetHover('left', false)}
      title={paneSetVisibility['left'] ? 'Hide left panes' : 'Show left panes'}
    >
      {#if paneSetVisibility['left']}
        <!-- Left arrow (hide) -->
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
        </svg>
      {:else}
        <!-- Right arrow (show) -->
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
          <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
        </svg>
      {/if}
    </button>
  {/if}

  <!-- Right Pane Set Toggle -->
  {#if hasPanesVisible('right') && hoverStates['right']}
    <button 
      class="floating-toggle-btn left-right fixed right-4 top-1/2 w-8 h-8 rounded-full bg-transparent border-2 border-primary text-primary shadow-xl z-50 flex items-center justify-center outline-none"
      on:click={() => togglePaneSet('right')}
      on:mouseenter={() => handlePaneSetHover('right', true)}
      on:mouseleave={() => handlePaneSetHover('right', false)}
      title={paneSetVisibility['right'] ? 'Hide right panes' : 'Show right panes'}
    >
      {#if paneSetVisibility['right']}
        <!-- Right arrow (hide) -->
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
          <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
        </svg>
      {:else}
        <!-- Left arrow (show) -->
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
        </svg>
      {/if}
    </button>
  {/if}

  <!-- Bottom Pane Set Toggle -->
  {#if hasPanesVisible('bottom') && hoverStates['bottom']}
    <button 
      class="floating-toggle-btn bottom fixed bottom-2 left-1/2 w-8 h-8 rounded-full bg-transparent border-2 border-primary text-primary shadow-xl z-50 flex items-center justify-center outline-none"
      on:click={() => togglePaneSet('bottom')}
      on:mouseenter={() => handlePaneSetHover('bottom', true)}
      on:mouseleave={() => handlePaneSetHover('bottom', false)}
      title={paneSetVisibility['bottom'] ? 'Hide bottom panes' : 'Show bottom panes'}
    >
      {#if paneSetVisibility['bottom']}
        <!-- Down arrow (hide) -->
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
          <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
        </svg>
      {:else}
        <!-- Up arrow (show) -->
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 15.75l7.5-7.5 7.5 7.5" />
        </svg>
      {/if}
    </button>
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
  
  /* Floating toggle buttons - completely stable positioning */
  .floating-toggle-btn {
    user-select: none;
    -webkit-tap-highlight-color: transparent;
    transition: background-color 0.2s ease, border-color 0.2s ease, opacity 0.3s ease !important;
    backdrop-filter: blur(4px);
    -webkit-backdrop-filter: blur(4px);
    animation: fadeIn 0.3s ease-out;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(-50%) scale(0.8);
    }
    to {
      opacity: 1;
      transform: translateY(-50%) scale(1);
    }
  }

  @keyframes fadeInBottom {
    from {
      opacity: 0;
      transform: translateX(-50%) scale(0.8);
    }
    to {
      opacity: 1;
      transform: translateX(-50%) scale(1);
    }
  }
  
  /* Left/Right buttons - always maintain translateY(-50%) */
  .floating-toggle-btn.left-right {
    transform: translateY(-50%) !important;
  }
  
  .floating-toggle-btn.left-right:hover {
    background-color: rgba(255, 255, 255, 0.1) !important;
    border-color: oklch(var(--pf)) !important;
    transform: translateY(-50%) !important;
  }
  
  .floating-toggle-btn.left-right:active {
    background-color: rgba(255, 255, 255, 0.2) !important;
    transform: translateY(-50%) !important;
  }
  
  .floating-toggle-btn.left-right:focus {
    background-color: rgba(255, 255, 255, 0.05) !important;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3) !important;
    transform: translateY(-50%) !important;
    outline: none !important;
  }
  
  /* Bottom button - always maintain translateX(-50%) */
  .floating-toggle-btn.bottom {
    transform: translateX(-50%) !important;
    animation: fadeInBottom 0.3s ease-out;
  }
  
  .floating-toggle-btn.bottom:hover {
    background-color: rgba(255, 255, 255, 0.1) !important;
    border-color: oklch(var(--pf)) !important;
    transform: translateX(-50%) !important;
  }
  
  .floating-toggle-btn.bottom:active {
    background-color: rgba(255, 255, 255, 0.2) !important;
    transform: translateX(-50%) !important;
  }
  
  .floating-toggle-btn.bottom:focus {
    background-color: rgba(255, 255, 255, 0.05) !important;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3) !important;
    transform: translateX(-50%) !important;
    outline: none !important;
  }
  
  /* Remove any default button behavior */
  .floating-toggle-btn:focus:not(:focus-visible) {
    outline: none !important;
    box-shadow: none !important;
  }
</style>