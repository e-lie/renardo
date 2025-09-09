<script>
  // Props
  export let showModal = false;
  export let paneVisibility = {};
  export let paneTabConfigs = {};
  export let hideAppNavbar = false;
  export let layoutManager = null;

  // Available component types (for individual tabs within panes)
  const availableComponents = [
    { type: 'ColorPicker', title: 'Color Picker', icon: '🎨', description: 'Interactive color picker with HSL controls' },
    { type: 'TextArea', title: 'Text Area', icon: '📝', description: 'Rich text editor with markdown support' }
  ];

  // Get all pane positions (except center)
  function getAllPanePositions() {
    return ['left-top', 'left-middle', 'left-bottom', 'right-top', 'right-middle', 'right-bottom', 'bottom-left', 'bottom-right'];
  }

  // Add a new tab to a pane
  function addTabToPane(position, componentType) {
    const componentInfo = availableComponents.find(c => c.type === componentType) || availableComponents[0];
    const newId = `${componentType.toLowerCase()}-${position}-${Date.now()}`;
    
    if (!paneTabConfigs[position]) {
      paneTabConfigs[position] = [];
    }
    
    // Deactivate other tabs
    paneTabConfigs[position].forEach(tab => tab.active = false);
    
    // Add new tab as active
    paneTabConfigs[position].push({
      title: componentInfo.title,
      componentType: componentType,
      componentId: newId,
      closable: paneTabConfigs[position].length > 0, // First tab is not closable
      active: true
    });
    
    // Trigger reactivity
    paneTabConfigs = { ...paneTabConfigs };
  }

  // Remove tab from pane
  function removeTabFromPane(position, tabIndex) {
    if (!paneTabConfigs[position] || paneTabConfigs[position].length <= 1) {
      return; // Cannot remove if only one tab or no tabs
    }
    
    const wasActive = paneTabConfigs[position][tabIndex]?.active;
    paneTabConfigs[position].splice(tabIndex, 1);
    
    // If removed tab was active, activate another tab
    if (wasActive && paneTabConfigs[position].length > 0) {
      const newActiveIndex = Math.min(tabIndex, paneTabConfigs[position].length - 1);
      paneTabConfigs[position][newActiveIndex].active = true;
    }
    
    // Update closable status (first tab should not be closable)
    if (paneTabConfigs[position].length > 0) {
      paneTabConfigs[position][0].closable = paneTabConfigs[position].length > 1;
    }
    
    // Trigger reactivity
    paneTabConfigs = { ...paneTabConfigs };
  }

  // Update tab title
  function updateTabTitle(position, tabIndex, newTitle) {
    if (paneTabConfigs[position] && paneTabConfigs[position][tabIndex]) {
      paneTabConfigs[position][tabIndex].title = newTitle;
      paneTabConfigs = { ...paneTabConfigs };
    }
  }

  // Preset configurations for tab layouts
  function applyPresetConfiguration(preset) {
    const presets = {
      'single': {
        'left-top': [{ title: 'Colors', componentType: 'ColorPicker', componentId: 'color-1', closable: false, active: true }],
        'left-middle': [{ title: 'Notes', componentType: 'TextArea', componentId: 'text-1', closable: false, active: true }],
        'left-bottom': [{ title: 'Colors', componentType: 'ColorPicker', componentId: 'color-2', closable: false, active: true }],
        'right-top': [{ title: 'Text', componentType: 'TextArea', componentId: 'text-2', closable: false, active: true }],
        'right-middle': [{ title: 'Colors', componentType: 'ColorPicker', componentId: 'color-3', closable: false, active: true }],
        'right-bottom': [{ title: 'Notes', componentType: 'TextArea', componentId: 'text-3', closable: false, active: true }],
        'bottom-left': [{ title: 'Draft', componentType: 'TextArea', componentId: 'text-4', closable: false, active: true }],
        'bottom-right': [{ title: 'Palette', componentType: 'ColorPicker', componentId: 'color-4', closable: false, active: true }]
      },
      'multi': {
        'left-top': [
          { title: 'Colors', componentType: 'ColorPicker', componentId: 'color-1', closable: false, active: true },
          { title: 'Palette', componentType: 'ColorPicker', componentId: 'color-1b', closable: true, active: false }
        ],
        'left-middle': [
          { title: 'Notes', componentType: 'TextArea', componentId: 'text-1', closable: false, active: true }
        ],
        'left-bottom': [
          { title: 'Scratch', componentType: 'TextArea', componentId: 'text-scratch', closable: false, active: true },
          { title: 'Colors', componentType: 'ColorPicker', componentId: 'color-scratch', closable: true, active: false }
        ],
        'right-top': [
          { title: 'Workspace', componentType: 'TextArea', componentId: 'text-2', closable: false, active: true }
        ],
        'right-middle': [
          { title: 'Shared Colors', componentType: 'ColorPicker', componentId: 'color-3', closable: false, active: true },
          { title: 'Tools', componentType: 'TextArea', componentId: 'text-tools', closable: true, active: false }
        ],
        'right-bottom': [
          { title: 'Shared Notes', componentType: 'TextArea', componentId: 'text-3', closable: false, active: true }
        ],
        'bottom-left': [
          { title: 'Draft', componentType: 'TextArea', componentId: 'text-4', closable: false, active: true },
          { title: 'Debug', componentType: 'TextArea', componentId: 'text-debug', closable: true, active: false }
        ],
        'bottom-right': [
          { title: 'Palette', componentType: 'ColorPicker', componentId: 'color-4', closable: false, active: true },
          { title: 'Export', componentType: 'TextArea', componentId: 'text-export', closable: true, active: false }
        ]
      },
      'empty': {
        'left-top': [],
        'left-middle': [],
        'left-bottom': [],
        'right-top': [],
        'right-middle': [],
        'right-bottom': [],
        'bottom-left': [],
        'bottom-right': []
      }
    };

    if (presets[preset]) {
      paneTabConfigs = { ...presets[preset] };
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

  // Close modal
  function closeModal() {
    showModal = false;
  }
</script>

<!-- Layout Configuration Modal -->
{#if showModal}
  <div class="modal modal-open">
    <div class="modal-box max-w-[80vw] w-[80vw] h-[80vh] flex flex-col">
      <!-- Modal Header -->
      <div class="flex justify-between items-center mb-4">
        <h3 class="font-bold text-lg">Layout Configuration</h3>
        <button 
          class="btn btn-sm btn-circle btn-ghost"
          on:click={closeModal}
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
          <div class="flex flex-col gap-2 p-4 bg-base-200 rounded-lg h-[400px]">
            <!-- Top Row - Top Menu -->
            <div class="flex h-[15%]">
              <div class="flex-1 flex items-center justify-center border-2 border-base-300 rounded-lg {getPaneColor('top-menu')}">
                <div class="form-control">
                  <label class="label cursor-pointer flex-col gap-1">
                    <span class="label-text text-xs font-semibold">Top Menu</span>
                    <input 
                      type="checkbox" 
                      class="toggle toggle-primary toggle-sm"
                      checked={paneVisibility['top-menu']}
                      on:change={(e) => {
                        paneVisibility['top-menu'] = e.target.checked;
                        paneVisibility = { ...paneVisibility };
                      }}
                    />
                  </label>
                </div>
              </div>
            </div>
            
            <!-- Middle Row -->
            <div class="flex flex-1 gap-2">
              <!-- Left Column -->
              <div class="flex flex-col gap-2 w-[25%]">
                <!-- Left Top -->
                <div class="flex-1 flex items-center justify-center border-2 border-base-300 rounded-lg {getPaneColor('left-top')}">
                  <div class="form-control">
                    <label class="label cursor-pointer flex-col gap-1">
                      <span class="label-text text-xs font-semibold">Left Top</span>
                      <input 
                        type="checkbox" 
                        class="toggle toggle-primary toggle-sm"
                        checked={paneVisibility['left-top']}
                        on:change={(e) => {
                          paneVisibility['left-top'] = e.target.checked;
                          paneVisibility = { ...paneVisibility };
                        }}
                      />
                    </label>
                  </div>
                </div>
                <!-- Left Middle -->
                <div class="flex-1 flex items-center justify-center border-2 border-base-300 rounded-lg {getPaneColor('left-middle')}">
                  <div class="form-control">
                    <label class="label cursor-pointer flex-col gap-1">
                      <span class="label-text text-xs font-semibold">Left Mid</span>
                      <input 
                        type="checkbox" 
                        class="toggle toggle-primary toggle-sm"
                        checked={paneVisibility['left-middle']}
                        on:change={(e) => {
                          paneVisibility['left-middle'] = e.target.checked;
                          paneVisibility = { ...paneVisibility };
                        }}
                      />
                    </label>
                  </div>
                </div>
                <!-- Left Bottom -->
                <div class="flex-1 flex items-center justify-center border-2 border-base-300 rounded-lg {getPaneColor('left-bottom')}">
                  <div class="form-control">
                    <label class="label cursor-pointer flex-col gap-1">
                      <span class="label-text text-xs font-semibold">Left Bot</span>
                      <input 
                        type="checkbox" 
                        class="toggle toggle-primary toggle-sm"
                        checked={paneVisibility['left-bottom']}
                        on:change={(e) => {
                          paneVisibility['left-bottom'] = e.target.checked;
                          paneVisibility = { ...paneVisibility };
                        }}
                      />
                    </label>
                  </div>
                </div>
              </div>
              
              <!-- Center -->
              <div class="flex-1 flex items-center justify-center border-2 border-primary rounded-lg {getPaneColor('center')}">
                <div class="form-control">
                  <label class="label cursor-pointer flex-col gap-1">
                    <span class="text-2xl mb-2">📝</span>
                    <span class="label-text text-sm font-bold">Center Editor</span>
                    <span class="badge badge-xs badge-primary">Always Visible</span>
                  </label>
                </div>
              </div>
              
              <!-- Right Column -->
              <div class="flex flex-col gap-2 w-[25%]">
                <!-- Right Top -->
                <div class="flex-1 flex items-center justify-center border-2 border-base-300 rounded-lg {getPaneColor('right-top')}">
                  <div class="form-control">
                    <label class="label cursor-pointer flex-col gap-1">
                      <span class="label-text text-xs font-semibold">Right Top</span>
                      <input 
                        type="checkbox" 
                        class="toggle toggle-primary toggle-sm"
                        checked={paneVisibility['right-top']}
                        on:change={(e) => {
                          paneVisibility['right-top'] = e.target.checked;
                          paneVisibility = { ...paneVisibility };
                        }}
                      />
                    </label>
                  </div>
                </div>
                <!-- Right Middle -->
                <div class="flex-1 flex items-center justify-center border-2 border-base-300 rounded-lg {getPaneColor('right-middle')}">
                  <div class="form-control">
                    <label class="label cursor-pointer flex-col gap-1">
                      <span class="label-text text-xs font-semibold">Right Mid</span>
                      <input 
                        type="checkbox" 
                        class="toggle toggle-primary toggle-sm"
                        checked={paneVisibility['right-middle']}
                        on:change={(e) => {
                          paneVisibility['right-middle'] = e.target.checked;
                          paneVisibility = { ...paneVisibility };
                        }}
                      />
                    </label>
                  </div>
                </div>
                <!-- Right Bottom -->
                <div class="flex-1 flex items-center justify-center border-2 border-base-300 rounded-lg {getPaneColor('right-bottom')}">
                  <div class="form-control">
                    <label class="label cursor-pointer flex-col gap-1">
                      <span class="label-text text-xs font-semibold">Right Bot</span>
                      <input 
                        type="checkbox" 
                        class="toggle toggle-primary toggle-sm"
                        checked={paneVisibility['right-bottom']}
                        on:change={(e) => {
                          paneVisibility['right-bottom'] = e.target.checked;
                          paneVisibility = { ...paneVisibility };
                        }}
                      />
                    </label>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Bottom Row -->
            <div class="flex h-[25%] gap-2">
              <!-- Bottom Left -->
              <div class="flex-1 flex items-center justify-center border-2 border-base-300 rounded-lg {getPaneColor('bottom-left')}">
                <div class="form-control">
                  <label class="label cursor-pointer flex-col gap-1">
                    <span class="label-text text-xs font-semibold">Bottom Left</span>
                    <input 
                      type="checkbox" 
                      class="toggle toggle-primary toggle-sm"
                      checked={paneVisibility['bottom-left']}
                      on:change={(e) => {
                        paneVisibility['bottom-left'] = e.target.checked;
                        paneVisibility = { ...paneVisibility };
                      }}
                    />
                  </label>
                </div>
              </div>
              <!-- Bottom Right -->
              <div class="flex-1 flex items-center justify-center border-2 border-base-300 rounded-lg {getPaneColor('bottom-right')}">
                <div class="form-control">
                  <label class="label cursor-pointer flex-col gap-1">
                    <span class="label-text text-xs font-semibold">Bottom Right</span>
                    <input 
                      type="checkbox" 
                      class="toggle toggle-primary toggle-sm"
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
          </div>
          
          <!-- Note about center pane -->
          <div class="alert alert-info">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            <span>The center code editor pane cannot be hidden.</span>
          </div>
        </div>

        <!-- Quick Presets Section -->
        <div class="divider">Quick Presets</div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-2 mb-4">
          <button 
            class="btn btn-sm btn-outline"
            on:click={() => applyPresetConfiguration('single')}
          >
            📄 Single Components
          </button>
          <button 
            class="btn btn-sm btn-outline"
            on:click={() => applyPresetConfiguration('multi')}
          >
            🗂️ Multi-Tab Layout
          </button>
          <button 
            class="btn btn-sm btn-outline"
            on:click={() => applyPresetConfiguration('empty')}
          >
            📦 All Empty
          </button>
        </div>

        <!-- Tab Management Section -->
        <div class="divider">Pane Tab Management</div>
        <div class="space-y-4">
          <div class="alert alert-info">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            <span><strong>Tip:</strong> Each pane can contain multiple components in tabs. Components of the same type share synchronized state!</span>
          </div>

          <!-- Tab management visual layout matching pane positions -->
          <div class="flex flex-col gap-2 p-4 bg-base-200 rounded-lg" style="min-height: 600px;">
            <!-- Top Row - Top Menu -->
            <div class="flex" style="height: 120px;">
              <div class="flex-1 flex flex-col border-2 border-base-300 rounded-lg {getPaneColor('top-menu')} p-3">
                {#if paneVisibility['top-menu']}
                  <div class="flex items-center justify-between mb-2">
                    <span class="text-xs font-semibold">Top Menu</span>
                    <span class="badge badge-xs badge-primary">{paneTabConfigs['top-menu']?.length || 0} tabs</span>
                  </div>
                  <div class="flex-1 overflow-y-auto">
                    <div class="flex flex-wrap gap-1">
                      {#each (paneTabConfigs['top-menu'] || []) as tab, tabIndex}
                        <div class="badge badge-sm {tab.active ? 'badge-primary' : 'badge-ghost'}" title={tab.title}>
                          {tab.componentType === 'ColorPicker' ? '🎨' : '📝'}
                          <span class="ml-1 truncate max-w-[60px]">{tab.title}</span>
                        </div>
                      {/each}
                    </div>
                  </div>
                  <div class="flex gap-1 mt-2">
                    <button class="btn btn-xs btn-ghost" on:click={() => addTabToPane('top-menu', 'ColorPicker')}>+🎨</button>
                    <button class="btn btn-xs btn-ghost" on:click={() => addTabToPane('top-menu', 'TextArea')}>+📝</button>
                  </div>
                {:else}
                  <div class="flex-1 flex items-center justify-center text-base-content/30">
                    <span class="text-xs">Pane Hidden</span>
                  </div>
                {/if}
              </div>
            </div>
            
            <!-- Middle Row -->
            <div class="flex flex-1 gap-2">
              <!-- Left Column -->
              <div class="flex flex-col gap-2 w-[25%]">
                <!-- Left Top -->
                <div class="flex-1 flex flex-col border-2 border-base-300 rounded-lg {getPaneColor('left-top')} p-3 min-h-0">
                  {#if paneVisibility['left-top']}
                    <div class="flex items-center justify-between mb-2">
                      <span class="text-xs font-semibold">Left Top</span>
                      <span class="badge badge-xs badge-primary">{paneTabConfigs['left-top']?.length || 0}</span>
                    </div>
                    <div class="flex-1 overflow-y-auto min-h-0">
                      {#each (paneTabConfigs['left-top'] || []) as tab, tabIndex}
                        <div class="flex items-center gap-1 p-1 mb-1 rounded text-xs {tab.active ? 'bg-primary/20' : 'bg-base-100/50'}">
                          <span>{tab.componentType === 'ColorPicker' ? '🎨' : '📝'}</span>
                          <span class="flex-1 truncate">{tab.title}</span>
                          {#if tab.closable}
                            <button class="text-error hover:bg-error/20 rounded px-1" on:click={() => removeTabFromPane('left-top', tabIndex)}>×</button>
                          {/if}
                        </div>
                      {/each}
                    </div>
                    <div class="flex gap-1 mt-2">
                      <button class="btn btn-xs btn-ghost flex-1" on:click={() => addTabToPane('left-top', 'ColorPicker')}>+🎨</button>
                      <button class="btn btn-xs btn-ghost flex-1" on:click={() => addTabToPane('left-top', 'TextArea')}>+📝</button>
                    </div>
                  {:else}
                    <div class="flex-1 flex items-center justify-center text-base-content/30">
                      <span class="text-xs">Hidden</span>
                    </div>
                  {/if}
                </div>
                <!-- Left Middle -->
                <div class="flex-1 flex flex-col border-2 border-base-300 rounded-lg {getPaneColor('left-middle')} p-3 min-h-0">
                  {#if paneVisibility['left-middle']}
                    <div class="flex items-center justify-between mb-2">
                      <span class="text-xs font-semibold">Left Mid</span>
                      <span class="badge badge-xs badge-primary">{paneTabConfigs['left-middle']?.length || 0}</span>
                    </div>
                    <div class="flex-1 overflow-y-auto min-h-0">
                      {#each (paneTabConfigs['left-middle'] || []) as tab, tabIndex}
                        <div class="flex items-center gap-1 p-1 mb-1 rounded text-xs {tab.active ? 'bg-primary/20' : 'bg-base-100/50'}">
                          <span>{tab.componentType === 'ColorPicker' ? '🎨' : '📝'}</span>
                          <span class="flex-1 truncate">{tab.title}</span>
                          {#if tab.closable}
                            <button class="text-error hover:bg-error/20 rounded px-1" on:click={() => removeTabFromPane('left-middle', tabIndex)}>×</button>
                          {/if}
                        </div>
                      {/each}
                    </div>
                    <div class="flex gap-1 mt-2">
                      <button class="btn btn-xs btn-ghost flex-1" on:click={() => addTabToPane('left-middle', 'ColorPicker')}>+🎨</button>
                      <button class="btn btn-xs btn-ghost flex-1" on:click={() => addTabToPane('left-middle', 'TextArea')}>+📝</button>
                    </div>
                  {:else}
                    <div class="flex-1 flex items-center justify-center text-base-content/30">
                      <span class="text-xs">Hidden</span>
                    </div>
                  {/if}
                </div>
                <!-- Left Bottom -->
                <div class="flex-1 flex flex-col border-2 border-base-300 rounded-lg {getPaneColor('left-bottom')} p-3 min-h-0">
                  {#if paneVisibility['left-bottom']}
                    <div class="flex items-center justify-between mb-2">
                      <span class="text-xs font-semibold">Left Bot</span>
                      <span class="badge badge-xs badge-primary">{paneTabConfigs['left-bottom']?.length || 0}</span>
                    </div>
                    <div class="flex-1 overflow-y-auto min-h-0">
                      {#each (paneTabConfigs['left-bottom'] || []) as tab, tabIndex}
                        <div class="flex items-center gap-1 p-1 mb-1 rounded text-xs {tab.active ? 'bg-primary/20' : 'bg-base-100/50'}">
                          <span>{tab.componentType === 'ColorPicker' ? '🎨' : '📝'}</span>
                          <span class="flex-1 truncate">{tab.title}</span>
                          {#if tab.closable}
                            <button class="text-error hover:bg-error/20 rounded px-1" on:click={() => removeTabFromPane('left-bottom', tabIndex)}>×</button>
                          {/if}
                        </div>
                      {/each}
                    </div>
                    <div class="flex gap-1 mt-2">
                      <button class="btn btn-xs btn-ghost flex-1" on:click={() => addTabToPane('left-bottom', 'ColorPicker')}>+🎨</button>
                      <button class="btn btn-xs btn-ghost flex-1" on:click={() => addTabToPane('left-bottom', 'TextArea')}>+📝</button>
                    </div>
                  {:else}
                    <div class="flex-1 flex items-center justify-center text-base-content/30">
                      <span class="text-xs">Hidden</span>
                    </div>
                  {/if}
                </div>
              </div>
              
              <!-- Center -->
              <div class="flex-1 flex items-center justify-center border-2 border-primary rounded-lg {getPaneColor('center')}">
                <div class="text-center">
                  <span class="text-2xl mb-2">📝</span>
                  <div class="text-sm font-bold">Center Editor</div>
                  <div class="badge badge-xs badge-primary mt-1">Always Visible</div>
                </div>
              </div>
              
              <!-- Right Column -->
              <div class="flex flex-col gap-2 w-[25%]">
                <!-- Right Top -->
                <div class="flex-1 flex flex-col border-2 border-base-300 rounded-lg {getPaneColor('right-top')} p-3 min-h-0">
                  {#if paneVisibility['right-top']}
                    <div class="flex items-center justify-between mb-2">
                      <span class="text-xs font-semibold">Right Top</span>
                      <span class="badge badge-xs badge-primary">{paneTabConfigs['right-top']?.length || 0}</span>
                    </div>
                    <div class="flex-1 overflow-y-auto min-h-0">
                      {#each (paneTabConfigs['right-top'] || []) as tab, tabIndex}
                        <div class="flex items-center gap-1 p-1 mb-1 rounded text-xs {tab.active ? 'bg-primary/20' : 'bg-base-100/50'}">
                          <span>{tab.componentType === 'ColorPicker' ? '🎨' : '📝'}</span>
                          <span class="flex-1 truncate">{tab.title}</span>
                          {#if tab.closable}
                            <button class="text-error hover:bg-error/20 rounded px-1" on:click={() => removeTabFromPane('right-top', tabIndex)}>×</button>
                          {/if}
                        </div>
                      {/each}
                    </div>
                    <div class="flex gap-1 mt-2">
                      <button class="btn btn-xs btn-ghost flex-1" on:click={() => addTabToPane('right-top', 'ColorPicker')}>+🎨</button>
                      <button class="btn btn-xs btn-ghost flex-1" on:click={() => addTabToPane('right-top', 'TextArea')}>+📝</button>
                    </div>
                  {:else}
                    <div class="flex-1 flex items-center justify-center text-base-content/30">
                      <span class="text-xs">Hidden</span>
                    </div>
                  {/if}
                </div>
                <!-- Right Middle -->
                <div class="flex-1 flex flex-col border-2 border-base-300 rounded-lg {getPaneColor('right-middle')} p-3 min-h-0">
                  {#if paneVisibility['right-middle']}
                    <div class="flex items-center justify-between mb-2">
                      <span class="text-xs font-semibold">Right Mid</span>
                      <span class="badge badge-xs badge-primary">{paneTabConfigs['right-middle']?.length || 0}</span>
                    </div>
                    <div class="flex-1 overflow-y-auto min-h-0">
                      {#each (paneTabConfigs['right-middle'] || []) as tab, tabIndex}
                        <div class="flex items-center gap-1 p-1 mb-1 rounded text-xs {tab.active ? 'bg-primary/20' : 'bg-base-100/50'}">
                          <span>{tab.componentType === 'ColorPicker' ? '🎨' : '📝'}</span>
                          <span class="flex-1 truncate">{tab.title}</span>
                          {#if tab.closable}
                            <button class="text-error hover:bg-error/20 rounded px-1" on:click={() => removeTabFromPane('right-middle', tabIndex)}>×</button>
                          {/if}
                        </div>
                      {/each}
                    </div>
                    <div class="flex gap-1 mt-2">
                      <button class="btn btn-xs btn-ghost flex-1" on:click={() => addTabToPane('right-middle', 'ColorPicker')}>+🎨</button>
                      <button class="btn btn-xs btn-ghost flex-1" on:click={() => addTabToPane('right-middle', 'TextArea')}>+📝</button>
                    </div>
                  {:else}
                    <div class="flex-1 flex items-center justify-center text-base-content/30">
                      <span class="text-xs">Hidden</span>
                    </div>
                  {/if}
                </div>
                <!-- Right Bottom -->
                <div class="flex-1 flex flex-col border-2 border-base-300 rounded-lg {getPaneColor('right-bottom')} p-3 min-h-0">
                  {#if paneVisibility['right-bottom']}
                    <div class="flex items-center justify-between mb-2">
                      <span class="text-xs font-semibold">Right Bot</span>
                      <span class="badge badge-xs badge-primary">{paneTabConfigs['right-bottom']?.length || 0}</span>
                    </div>
                    <div class="flex-1 overflow-y-auto min-h-0">
                      {#each (paneTabConfigs['right-bottom'] || []) as tab, tabIndex}
                        <div class="flex items-center gap-1 p-1 mb-1 rounded text-xs {tab.active ? 'bg-primary/20' : 'bg-base-100/50'}">
                          <span>{tab.componentType === 'ColorPicker' ? '🎨' : '📝'}</span>
                          <span class="flex-1 truncate">{tab.title}</span>
                          {#if tab.closable}
                            <button class="text-error hover:bg-error/20 rounded px-1" on:click={() => removeTabFromPane('right-bottom', tabIndex)}>×</button>
                          {/if}
                        </div>
                      {/each}
                    </div>
                    <div class="flex gap-1 mt-2">
                      <button class="btn btn-xs btn-ghost flex-1" on:click={() => addTabToPane('right-bottom', 'ColorPicker')}>+🎨</button>
                      <button class="btn btn-xs btn-ghost flex-1" on:click={() => addTabToPane('right-bottom', 'TextArea')}>+📝</button>
                    </div>
                  {:else}
                    <div class="flex-1 flex items-center justify-center text-base-content/30">
                      <span class="text-xs">Hidden</span>
                    </div>
                  {/if}
                </div>
              </div>
            </div>
            
            <!-- Bottom Row -->
            <div class="flex gap-2" style="height: 150px;">
              <!-- Bottom Left -->
              <div class="flex-1 flex flex-col border-2 border-base-300 rounded-lg {getPaneColor('bottom-left')} p-3">
                {#if paneVisibility['bottom-left']}
                  <div class="flex items-center justify-between mb-2">
                    <span class="text-xs font-semibold">Bottom Left</span>
                    <span class="badge badge-xs badge-primary">{paneTabConfigs['bottom-left']?.length || 0}</span>
                  </div>
                  <div class="flex-1 overflow-y-auto">
                    {#each (paneTabConfigs['bottom-left'] || []) as tab, tabIndex}
                      <div class="flex items-center gap-1 p-1 mb-1 rounded text-xs {tab.active ? 'bg-primary/20' : 'bg-base-100/50'}">
                        <span>{tab.componentType === 'ColorPicker' ? '🎨' : '📝'}</span>
                        <span class="flex-1 truncate">{tab.title}</span>
                        {#if tab.closable}
                          <button class="text-error hover:bg-error/20 rounded px-1" on:click={() => removeTabFromPane('bottom-left', tabIndex)}>×</button>
                        {/if}
                      </div>
                    {/each}
                  </div>
                  <div class="flex gap-1 mt-2">
                    <button class="btn btn-xs btn-ghost flex-1" on:click={() => addTabToPane('bottom-left', 'ColorPicker')}>+🎨</button>
                    <button class="btn btn-xs btn-ghost flex-1" on:click={() => addTabToPane('bottom-left', 'TextArea')}>+📝</button>
                  </div>
                {:else}
                  <div class="flex-1 flex items-center justify-center text-base-content/30">
                    <span class="text-xs">Hidden</span>
                  </div>
                {/if}
              </div>
              <!-- Bottom Right -->
              <div class="flex-1 flex flex-col border-2 border-base-300 rounded-lg {getPaneColor('bottom-right')} p-3">
                {#if paneVisibility['bottom-right']}
                  <div class="flex items-center justify-between mb-2">
                    <span class="text-xs font-semibold">Bottom Right</span>
                    <span class="badge badge-xs badge-primary">{paneTabConfigs['bottom-right']?.length || 0}</span>
                  </div>
                  <div class="flex-1 overflow-y-auto">
                    {#each (paneTabConfigs['bottom-right'] || []) as tab, tabIndex}
                      <div class="flex items-center gap-1 p-1 mb-1 rounded text-xs {tab.active ? 'bg-primary/20' : 'bg-base-100/50'}">
                        <span>{tab.componentType === 'ColorPicker' ? '🎨' : '📝'}</span>
                        <span class="flex-1 truncate">{tab.title}</span>
                        {#if tab.closable}
                          <button class="text-error hover:bg-error/20 rounded px-1" on:click={() => removeTabFromPane('bottom-right', tabIndex)}>×</button>
                        {/if}
                      </div>
                    {/each}
                  </div>
                  <div class="flex gap-1 mt-2">
                    <button class="btn btn-xs btn-ghost flex-1" on:click={() => addTabToPane('bottom-right', 'ColorPicker')}>+🎨</button>
                    <button class="btn btn-xs btn-ghost flex-1" on:click={() => addTabToPane('bottom-right', 'TextArea')}>+📝</button>
                  </div>
                {:else}
                  <div class="flex-1 flex items-center justify-center text-base-content/30">
                    <span class="text-xs">Hidden</span>
                  </div>
                {/if}
              </div>
            </div>
          </div>

          <!-- Available Components Info -->
          <div class="divider">Available Components</div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
            {#each availableComponents as component}
              <div class="card card-compact bg-base-100 border border-base-300">
                <div class="card-body items-center text-center">
                  <div class="text-2xl mb-1">{component.icon}</div>
                  <h4 class="card-title text-sm">{component.title}</h4>
                  <p class="text-xs opacity-70">{component.description}</p>
                  <div class="badge badge-sm badge-primary">Synchronized</div>
                </div>
              </div>
            {/each}
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
          on:click={closeModal}
        >
          Close
        </button>
      </div>
    </div>
    
    <!-- Modal backdrop -->
    <div class="modal-backdrop" on:click={closeModal}></div>
  </div>
{/if}