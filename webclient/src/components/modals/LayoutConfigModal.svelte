<script>
  // Props
  export let showModal = false;
  export let paneVisibility = {};
  export let paneComponents = {};
  export let hideAppNavbar = false;
  export let layoutManager = null;

  // Available component types
  const availableComponents = [
    { type: 'ColorPicker', title: 'Color Picker', icon: '🎨', description: 'Interactive color picker with HSL controls' },
    { type: 'TextArea', title: 'Text Area', icon: '📝', description: 'Rich text editor with markdown support' },
    { type: 'placeholder', title: 'Empty', icon: '📦', description: 'Empty pane placeholder' }
  ];

  // Get all pane positions (except center)
  function getAllPanePositions() {
    return ['left-top', 'left-middle', 'left-bottom', 'right-top', 'right-middle', 'right-bottom', 'bottom-left', 'bottom-right'];
  }

  // Update component assignment for a pane
  function updatePaneComponent(position, componentType) {
    const componentInfo = availableComponents.find(c => c.type === componentType) || availableComponents[0];
    const newId = `${componentType}-${position}-${Date.now()}`;
    
    paneComponents[position] = {
      type: componentType,
      title: componentInfo.title,
      id: newId
    };
    
    // Trigger reactivity
    paneComponents = { ...paneComponents };
  }

  // Preset configurations
  function applyPresetConfiguration(preset) {
    const presets = {
      'all-color': {
        'left-top': { type: 'ColorPicker', title: 'Color Picker', id: 'color-preset-1' },
        'left-middle': { type: 'ColorPicker', title: 'Color Picker', id: 'color-preset-2' },
        'left-bottom': { type: 'ColorPicker', title: 'Color Picker', id: 'color-preset-3' },
        'right-top': { type: 'ColorPicker', title: 'Color Picker', id: 'color-preset-4' },
        'right-middle': { type: 'ColorPicker', title: 'Color Picker', id: 'color-preset-5' },
        'right-bottom': { type: 'ColorPicker', title: 'Color Picker', id: 'color-preset-6' },
        'bottom-left': { type: 'ColorPicker', title: 'Color Picker', id: 'color-preset-7' },
        'bottom-right': { type: 'ColorPicker', title: 'Color Picker', id: 'color-preset-8' }
      },
      'all-text': {
        'left-top': { type: 'TextArea', title: 'Text Area', id: 'text-preset-1' },
        'left-middle': { type: 'TextArea', title: 'Text Area', id: 'text-preset-2' },
        'left-bottom': { type: 'TextArea', title: 'Text Area', id: 'text-preset-3' },
        'right-top': { type: 'TextArea', title: 'Text Area', id: 'text-preset-4' },
        'right-middle': { type: 'TextArea', title: 'Text Area', id: 'text-preset-5' },
        'right-bottom': { type: 'TextArea', title: 'Text Area', id: 'text-preset-6' },
        'bottom-left': { type: 'TextArea', title: 'Text Area', id: 'text-preset-7' },
        'bottom-right': { type: 'TextArea', title: 'Text Area', id: 'text-preset-8' }
      },
      'mixed': {
        'left-top': { type: 'ColorPicker', title: 'Color Picker', id: 'mixed-color-1' },
        'left-middle': { type: 'TextArea', title: 'Notes', id: 'mixed-text-1' },
        'left-bottom': { type: 'ColorPicker', title: 'Color Picker', id: 'mixed-color-2' },
        'right-top': { type: 'TextArea', title: 'Text Area', id: 'mixed-text-2' },
        'right-middle': { type: 'ColorPicker', title: 'Shared Colors', id: 'mixed-color-3' },
        'right-bottom': { type: 'TextArea', title: 'Shared Notes', id: 'mixed-text-3' },
        'bottom-left': { type: 'TextArea', title: 'Draft', id: 'mixed-text-4' },
        'bottom-right': { type: 'ColorPicker', title: 'Palette', id: 'mixed-color-4' }
      },
      'empty': {
        'left-top': { type: 'placeholder', title: 'Empty', id: null },
        'left-middle': { type: 'placeholder', title: 'Empty', id: null },
        'left-bottom': { type: 'placeholder', title: 'Empty', id: null },
        'right-top': { type: 'placeholder', title: 'Empty', id: null },
        'right-middle': { type: 'placeholder', title: 'Empty', id: null },
        'right-bottom': { type: 'placeholder', title: 'Empty', id: null },
        'bottom-left': { type: 'placeholder', title: 'Empty', id: null },
        'bottom-right': { type: 'placeholder', title: 'Empty', id: null }
      }
    };

    if (presets[preset]) {
      paneComponents = { ...presets[preset] };
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
    <div class="modal-box max-w-5xl h-[90vh] flex flex-col">
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

        <!-- Quick Presets Section -->
        <div class="divider">Quick Presets</div>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-2 mb-4">
          <button 
            class="btn btn-sm btn-outline"
            on:click={() => applyPresetConfiguration('all-color')}
          >
            🎨 All Colors
          </button>
          <button 
            class="btn btn-sm btn-outline"
            on:click={() => applyPresetConfiguration('all-text')}
          >
            📝 All Text
          </button>
          <button 
            class="btn btn-sm btn-outline"
            on:click={() => applyPresetConfiguration('mixed')}
          >
            🔄 Mixed (Default)
          </button>
          <button 
            class="btn btn-sm btn-outline"
            on:click={() => applyPresetConfiguration('empty')}
          >
            📦 All Empty
          </button>
        </div>

        <!-- Component Selection Section -->
        <div class="divider">Component Assignment</div>
        <div class="space-y-4">
          <div class="alert alert-success">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            <span><strong>Tip:</strong> Components of the same type share synchronized state across all panes!</span>
          </div>

          <!-- Component assignment for each pane -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            {#each getAllPanePositions() as position}
              <div class="card card-compact bg-base-200 shadow-sm">
                <div class="card-body">
                  <div class="flex items-center gap-2 mb-2">
                    <div class="w-4 h-4 rounded {getPaneColor(position)}"></div>
                    <h4 class="card-title text-sm capitalize">
                      {position.replace('-', ' ')}
                    </h4>
                  </div>
                  
                  <div class="form-control">
                    <label class="label py-1">
                      <span class="label-text text-xs">Component Type</span>
                    </label>
                    <select 
                      class="select select-xs select-bordered w-full"
                      bind:value={paneComponents[position].type}
                      on:change={(e) => updatePaneComponent(position, e.target.value)}
                    >
                      {#each availableComponents as component}
                        <option value={component.type}>
                          {component.icon} {component.title}
                        </option>
                      {/each}
                    </select>
                    <label class="label py-1">
                      <span class="label-text-alt text-xs opacity-70">
                        {availableComponents.find(c => c.type === paneComponents[position].type)?.description || ''}
                      </span>
                    </label>
                  </div>
                  
                  <div class="flex items-center gap-1 text-xs opacity-70">
                    <span class="badge badge-xs">
                      {paneComponents[position].type === 'ColorPicker' ? '🎨' : 
                       paneComponents[position].type === 'TextArea' ? '📝' : '📦'} 
                      {paneComponents[position].type}
                    </span>
                    {#if paneComponents[position].type !== 'placeholder'}
                      <span class="text-xs opacity-50">ID: {paneComponents[position].id?.split('-').slice(-1)[0] || 'N/A'}</span>
                    {/if}
                  </div>
                </div>
              </div>
            {/each}
          </div>

          <!-- Component Info Section -->
          <div class="divider">Available Components</div>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-2">
            {#each availableComponents as component}
              <div class="card card-compact bg-base-100 border border-base-300">
                <div class="card-body items-center text-center">
                  <div class="text-2xl mb-1">{component.icon}</div>
                  <h4 class="card-title text-sm">{component.title}</h4>
                  <p class="text-xs opacity-70">{component.description}</p>
                  {#if component.type !== 'placeholder'}
                    <div class="badge badge-sm badge-primary">Synchronized</div>
                  {/if}
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