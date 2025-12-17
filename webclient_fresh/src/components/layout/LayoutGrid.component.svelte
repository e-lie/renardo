<script lang="ts">
  import type { LayoutManager } from '../../lib/layout/LayoutManager';
  import type { Pane } from '../../lib/layout/Pane';
  import type { TabInterface, BufferInterface } from '../../models/editor';
  import TabbedPane from './TabbedPane.component.svelte';
  import EditorTabs from '../editor/EditorTabs.component.svelte';
  import CodeEditor from '../editor/CodeEditor.component.svelte';
  import { useEditorStore } from '../../store/editor';

  let {
    layoutManager,
    tabs,
    buffers,
    onswitch,
    onclose,
    oncreate,
    onsettings,
    activeBuffer,
  }: {
    layoutManager: LayoutManager;
    tabs: TabInterface[];
    buffers: BufferInterface[];
    onswitch?: (tabId: string) => void;
    onclose?: (tabId: string) => void;
    oncreate?: () => void;
    onsettings?: () => void;
    activeBuffer: BufferInterface | null;
  } = $props();

  // Import EditorStore for buffer management
  const { actions } = useEditorStore();

  let panes = $state<Pane[]>([]);

  $effect(() => {
    const unsub = layoutManager.panes.subscribe(p => {
      panes = p;
    });
    return unsub;
  });

  function getPaneByPosition(pos: string): Pane | null {
    return panes.find(p => p.getState().position === pos) || null;
  }

  function togglePaneVisibility(pos: string) {
    // Toggle all panes in a column/row
    const leftPanes = ['left-top', 'left-bottom'];
    const rightPanes = ['right-top', 'right-bottom'];
    const bottomPanes = ['bottom-left', 'bottom-right'];
    
    let panesToToggle: string[] = [];
    
    if (pos === 'left-top' || pos === 'left') {
      panesToToggle = leftPanes;
    } else if (pos === 'right-top' || pos === 'right') {
      panesToToggle = rightPanes;
    } else if (pos === 'bottom-left' || pos === 'bottom') {
      panesToToggle = bottomPanes;
    } else {
      panesToToggle = [pos];
    }
    
    const anyVisible = panesToToggle.some(p => getPaneByPosition(p)?.getState().isVisible);
    
    panesToToggle.forEach(panePos => {
      const pane = getPaneByPosition(panePos);
      if (pane) {
        pane.setVisible(!anyVisible);
      }
    });
  }

  function isAnyPaneVisible(positions: string[]): boolean {
    return positions.some(pos => getPaneByPosition(pos)?.getState().isVisible);
  }

  function getPaneWidth(positions: string[]): string {
    const visiblePane = positions
      .map(pos => getPaneByPosition(pos))
      .find(pane => pane?.getState().isVisible);
    
    if (visiblePane) {
      const dims = visiblePane.getState().dimensions;
      return `${dims.width || 300}px`;
    }
    return '0px';
  }

  function getPaneHeight(positions: string[]): string {
    const visiblePane = positions
      .map(pos => getPaneByPosition(pos))
      .find(pane => pane?.getState().isVisible);
    
    if (visiblePane) {
      const dims = visiblePane.getState().dimensions;
      return `${dims.height || 200}px`;
    }
    return '0px';
  }

  // Resize state
  let isResizing = $state(false);
  let resizeDirection = $state<'horizontal' | 'vertical' | null>(null);
  let startPos = $state({ x: 0, y: 0 });
  let startSizes = $state<Record<string, number>>({});

  function startResize(e: MouseEvent, direction: 'horizontal' | 'vertical') {
    e.preventDefault();
    isResizing = true;
    resizeDirection = direction;
    startPos = { x: e.clientX, y: e.clientY };
    
    // Store current sizes
    startSizes = {};
    panes.forEach(pane => {
      const state = pane.getState();
      startSizes[pane.getState().id] = state.dimensions.width || state.dimensions.height || 300;
    });

    document.addEventListener('mousemove', handleResize);
    document.addEventListener('mouseup', endResize);
  }

  function handleResize(e: MouseEvent) {
    if (!isResizing || !resizeDirection) return;

    const deltaX = e.clientX - startPos.x;
    const deltaY = e.clientY - startPos.y;

    // Update pane dimensions based on resize direction
    if (resizeDirection === 'horizontal') {
      // Resize left panes
      ['left-top', 'left-bottom'].forEach(paneId => {
        const pane = getPaneByPosition(paneId);
        if (pane) {
          const newWidth = Math.max(200, (startSizes[paneId] || 300) + deltaX);
          pane.setDimensions({ width: newWidth });
        }
      });
      // Resize right panes (inverted)
      ['right-top', 'right-bottom'].forEach(paneId => {
        const pane = getPaneByPosition(paneId);
        if (pane) {
          const newWidth = Math.max(200, (startSizes[paneId] || 300) - deltaX);
          pane.setDimensions({ width: newWidth });
        }
      });
    } else if (resizeDirection === 'vertical') {
      // Resize top panes
      ['left-top', 'right-top'].forEach(paneId => {
        const pane = getPaneByPosition(paneId);
        if (pane) {
          const newHeight = Math.max(150, (startSizes[paneId] || 300) + deltaY);
          pane.setDimensions({ height: newHeight });
        }
      });
      // Resize bottom panes (inverted)
      ['left-bottom', 'right-bottom', 'bottom-left', 'bottom-right'].forEach(paneId => {
        const pane = getPaneByPosition(paneId);
        if (pane) {
          const newHeight = Math.max(150, (startSizes[paneId] || 200) - deltaY);
          pane.setDimensions({ height: newHeight });
        }
      });
    }
  }

  function endResize() {
    isResizing = false;
    resizeDirection = null;
    document.removeEventListener('mousemove', handleResize);
    document.removeEventListener('mouseup', endResize);
  }
</script>

<div class="layout-grid h-full grid" style="
  grid-template-areas:
    'left-top center right-top'
    'left-bottom center right-bottom'
    'bottom-left bottom-left bottom-right';
  grid-template-columns: {getPaneWidth(['left-top', 'left-bottom'])} 1fr {getPaneWidth(['right-top', 'right-bottom'])};
  grid-template-rows: {getPaneHeight(['left-top', 'right-top'])} 1fr {getPaneHeight(['bottom-left', 'bottom-right'])};
  gap: 4px;
  padding: 4px;
">
  <!-- Left Top Pane -->
  {#each panes as pane (pane.getState().id)}
    {#if pane.getState().position === 'left-top' && pane.getState().isVisible}
      <div
        class="border border-base-300 overflow-hidden flex flex-col"
        style="grid-area: left-top;"
      >
        <TabbedPane {pane} />
      </div>
    {/if}
  {/each}

  <!-- Vertical Resize Handle between left and center -->
  {#if isAnyPaneVisible(['left-top', 'left-bottom'])}
    <div 
      role="separator"
      aria-orientation="vertical"
      tabindex="-1"
      class="w-1 bg-base-300 cursor-col-resize hover:bg-primary/30 transition-colors z-30"
      style="grid-column: 2; grid-row: 1 / 3;"
      onmousedown={(e) => startResize(e, 'horizontal')}
    ></div>
  {/if}

  <!-- Right Top Pane -->
  {#each panes as pane (pane.getState().id)}
    {#if pane.getState().position === 'right-top' && pane.getState().isVisible}
      <div
        class="border border-base-300 overflow-hidden flex flex-col"
        style="grid-area: right-top;"
      >
        <TabbedPane {pane} />
      </div>
    {/if}
  {/each}

  <!-- Vertical Resize Handle between center and right -->
  {#if isAnyPaneVisible(['right-top', 'right-bottom'])}
    <div 
      role="separator"
      aria-orientation="vertical"
      tabindex="-1"
      class="w-1 bg-base-300 cursor-col-resize hover:bg-primary/30 transition-colors z-30"
      style="grid-column: 4; grid-row: 1 / 3;"
      onmousedown={(e) => startResize(e, 'horizontal')}
    ></div>
  {/if}

  <!-- Left Bottom Pane -->
  {#each panes as pane (pane.getState().id)}
    {#if pane.getState().position === 'left-bottom' && pane.getState().isVisible}
      <div
        class="border border-base-300 overflow-hidden flex flex-col"
        style="grid-area: left-bottom;"
      >
        <TabbedPane {pane} />
      </div>
    {/if}
  {/each}

  <!-- Horizontal Resize Handle between top and bottom -->
  {#if isAnyPaneVisible(['left-top', 'right-top']) && isAnyPaneVisible(['left-bottom', 'right-bottom'])}
    <div 
      role="separator"
      aria-orientation="horizontal"
      tabindex="-1"
      class="h-1 bg-base-300 cursor-row-resize hover:bg-primary/30 transition-colors z-30"
      style="grid-column: 1 / 4; grid-row: 2;"
      onmousedown={(e) => startResize(e, 'vertical')}
    ></div>
  {/if}

  <!-- Right Bottom Pane -->
  {#each panes as pane (pane.getState().id)}
    {#if pane.getState().position === 'right-bottom' && pane.getState().isVisible}
      <div
        class="border border-base-300 overflow-hidden flex flex-col"
        style="grid-area: right-bottom;"
      >
        <TabbedPane {pane} />
      </div>
    {/if}
  {/each}

  <!-- Bottom Left Pane -->
  {#each panes as pane (pane.getState().id)}
    {#if pane.getState().position === 'bottom-left' && pane.getState().isVisible}
      <div
        class="border border-base-300 overflow-hidden flex flex-col"
        style="grid-area: bottom-left;"
      >
        <TabbedPane {pane} />
      </div>
    {/if}
  {/each}

  <!-- Bottom Right Pane -->
  {#each panes as pane (pane.getState().id)}
    {#if pane.getState().position === 'bottom-right' && pane.getState().isVisible}
      <div
        class="border border-base-300 overflow-hidden flex flex-col"
        style="grid-area: bottom-right;"
      >
        <TabbedPane {pane} />
      </div>
    {/if}
  {/each}

  <!-- Floating Toggle Buttons -->
    <!-- Floating Toggle Buttons -->
  {#if isAnyPaneVisible(['left-top', 'left-bottom'])}
    <button 
      class="fixed left-4 top-1/2 btn btn-circle btn-primary btn-sm shadow-lg z-40"
      style="transform: translateY(-50%);"
      onclick={() => togglePaneVisibility('left')}
      title="Toggle Left Panes"
    >
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
        <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
      </svg>
    </button>
  {:else}
    <button 
      class="fixed left-4 top-1/2 btn btn-circle btn-primary btn-sm shadow-lg z-40"
      style="transform: translateY(-50%);"
      onclick={() => togglePaneVisibility('left')}
      title="Show Left Panes"
    >
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
        <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
      </svg>
    </button>
  {/if}

  {#if isAnyPaneVisible(['right-top', 'right-bottom'])}
    <button 
      class="fixed right-4 top-1/2 btn btn-circle btn-primary btn-sm shadow-lg z-40"
      style="transform: translateY(-50%);"
      onclick={() => togglePaneVisibility('right')}
      title="Toggle Right Panes"
    >
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
        <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
      </svg>
    </button>
  {:else}
    <button 
      class="fixed right-4 top-1/2 btn btn-circle btn-primary btn-sm shadow-lg z-40"
      style="transform: translateY(-50%);"
      onclick={() => togglePaneVisibility('right')}
      title="Show Right Panes"
    >
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
        <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
      </svg>
    </button>
  {/if}

  {#if isAnyPaneVisible(['bottom-left', 'bottom-right'])}
    <button 
      class="fixed bottom-4 left-1/2 btn btn-circle btn-primary btn-sm shadow-lg z-40"
      style="transform: translateX(-50%);"
      onclick={() => togglePaneVisibility('bottom')}
      title="Toggle Bottom Panes"
    >
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
        <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
      </svg>
    </button>
  {:else}
    <button 
      class="fixed bottom-4 left-1/2 btn btn-circle btn-primary btn-sm shadow-lg z-40"
      style="transform: translateX(-50%);"
      onclick={() => togglePaneVisibility('bottom')}
      title="Show Bottom Panes"
    >
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
        <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 15.75l7.5-7.5 7.5 7.5" />
      </svg>
    </button>
  {/if}

  <!-- Center Pane (always visible) - Contains original editor -->
  {#each panes as pane (pane.getState().id)}
    {#if pane.getState().position === 'center' && pane.getState().isVisible}
      <div
        class="border border-base-300 overflow-hidden flex flex-col bg-base-200"
        style="grid-area: center;"
      >
        <!-- Original Editor Tabs -->
        <div class="bg-base-200 border-b border-base-300">
          <EditorTabs
            tabs={tabs}
            buffers={buffers}
            onswitch={onswitch}
            onclose={onclose}
            oncreate={oncreate}
            onsettings={onsettings}
          />
        </div>

        <!-- Original Code Editor -->
        <div class="flex-1 overflow-hidden">
          {#if activeBuffer}
            {#if activeBuffer}
              <CodeEditor 
                buffer={activeBuffer}
                onchange={(content) => {
                  console.log('Central editor content changed:', content);
                  if (activeBuffer) {
                    actions.updateBufferContent(activeBuffer.id, content);
                  }
                }}
                onexecute={(code) => {
                  console.log('Central editor execute:', code);
                  actions.executeCode(code);
                }}
              />
            {:else}
              <div class="flex items-center justify-center h-full">
                <p class="text-base-content/50">No active buffer in central editor</p>
              </div>
            {/if}
          {:else}
            <div class="p-4 text-center text-base-content/50">
              No active buffer
            </div>
          {/if}
        </div>
      </div>
    {/if}
  {/each}
</div>
