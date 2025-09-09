<script>
  import { onMount, onDestroy } from 'svelte';
  import { PaneComponent } from '../../lib/newEditor/PaneComponent';

  // Props
  export let componentId = null;
  export let title = 'Color Picker';

  // Component instance
  let component = null;
  let unsubscribe = null;

  // Local state synchronized with global state
  let selectedColor = '#3b82f6';
  let colorHistory = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6'];
  let showAdvanced = false;
  let hue = 217;
  let saturation = 76;
  let lightness = 61;

  // Predefined colors
  const presetColors = [
    '#ef4444', '#f97316', '#f59e0b', '#eab308', '#84cc16',
    '#22c55e', '#10b981', '#14b8a6', '#06b6d4', '#0ea5e9',
    '#3b82f6', '#6366f1', '#8b5cf6', '#a855f7', '#d946ef',
    '#ec4899', '#f43f5e', '#64748b', '#6b7280', '#374151',
    '#1f2937', '#111827', '#ffffff', '#f8fafc', '#e2e8f0'
  ];

  onMount(() => {
    // Create component instance
    component = new PaneComponent({
      id: componentId,
      type: 'ColorPicker',
      title: title,
      initialData: {
        selectedColor,
        colorHistory,
        showAdvanced,
        hue,
        saturation,
        lightness
      }
    });

    // Subscribe to global state changes
    unsubscribe = component.getGlobalState().subscribe((data) => {
      selectedColor = data.selectedColor || selectedColor;
      colorHistory = data.colorHistory || colorHistory;
      showAdvanced = data.showAdvanced || showAdvanced;
      hue = data.hue || hue;
      saturation = data.saturation || saturation;
      lightness = data.lightness || lightness;
    });

    component.setActive(true);
  });

  onDestroy(() => {
    if (unsubscribe) {
      unsubscribe();
    }
    if (component) {
      component.setActive(false);
    }
  });

  function updateColor(newColor) {
    selectedColor = newColor;
    
    // Add to history if not already present
    if (!colorHistory.includes(newColor)) {
      colorHistory = [newColor, ...colorHistory.slice(0, 9)];
    }

    // Update HSL values from hex
    const { h, s, l } = hexToHsl(newColor);
    hue = h;
    saturation = s;
    lightness = l;

    // Sync with global state
    if (component) {
      component.updateData({
        selectedColor,
        colorHistory,
        hue,
        saturation,
        lightness
      });
    }
  }

  function updateFromHsl() {
    const newColor = hslToHex(hue, saturation, lightness);
    updateColor(newColor);
  }

  function toggleAdvanced() {
    showAdvanced = !showAdvanced;
    if (component) {
      component.setDataProperty('showAdvanced', showAdvanced);
    }
  }

  function clearHistory() {
    colorHistory = [];
    if (component) {
      component.setDataProperty('colorHistory', colorHistory);
    }
  }

  // Color conversion utilities
  function hexToHsl(hex) {
    const r = parseInt(hex.substr(1, 2), 16) / 255;
    const g = parseInt(hex.substr(3, 2), 16) / 255;
    const b = parseInt(hex.substr(5, 2), 16) / 255;

    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    let h, s, l = (max + min) / 2;

    if (max === min) {
      h = s = 0;
    } else {
      const d = max - min;
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
      switch (max) {
        case r: h = (g - b) / d + (g < b ? 6 : 0); break;
        case g: h = (b - r) / d + 2; break;
        case b: h = (r - g) / d + 4; break;
      }
      h /= 6;
    }

    return {
      h: Math.round(h * 360),
      s: Math.round(s * 100),
      l: Math.round(l * 100)
    };
  }

  function hslToHex(h, s, l) {
    l /= 100;
    const a = s * Math.min(l, 1 - l) / 100;
    const f = n => {
      const k = (n + h / 30) % 12;
      const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
      return Math.round(255 * color).toString(16).padStart(2, '0');
    };
    return `#${f(0)}${f(8)}${f(4)}`;
  }
</script>

<div class="color-picker p-4 h-full overflow-y-auto">
  <div class="flex items-center justify-between mb-4">
    <h3 class="text-lg font-semibold">Color Picker</h3>
    <button 
      class="btn btn-xs btn-ghost"
      on:click={toggleAdvanced}
      title="Toggle Advanced Controls"
    >
      {showAdvanced ? '🔽' : '🔼'}
    </button>
  </div>

  <!-- Current Color Display -->
  <div class="mb-4">
    <div class="flex items-center gap-3 mb-2">
      <div 
        class="w-12 h-12 rounded-lg border-2 border-base-300 shadow-sm"
        style="background-color: {selectedColor}"
      ></div>
      <div class="flex-1">
        <input 
          type="color" 
          bind:value={selectedColor}
          on:input={(e) => updateColor(e.target.value)}
          class="w-full h-8 rounded cursor-pointer"
        />
      </div>
    </div>
    
    <input 
      type="text" 
      bind:value={selectedColor}
      on:input={(e) => updateColor(e.target.value)}
      class="input input-sm input-bordered w-full font-mono"
      placeholder="#3b82f6"
    />
  </div>

  <!-- Advanced HSL Controls -->
  {#if showAdvanced}
    <div class="mb-4 p-3 bg-base-200 rounded-lg">
      <h4 class="text-sm font-semibold mb-3">HSL Controls</h4>
      
      <!-- Hue -->
      <div class="mb-3">
        <div class="flex justify-between text-xs mb-1">
          <span>Hue</span>
          <span>{hue}°</span>
        </div>
        <input 
          type="range" 
          min="0" 
          max="360" 
          bind:value={hue}
          on:input={updateFromHsl}
          class="range range-xs range-primary"
        />
      </div>

      <!-- Saturation -->
      <div class="mb-3">
        <div class="flex justify-between text-xs mb-1">
          <span>Saturation</span>
          <span>{saturation}%</span>
        </div>
        <input 
          type="range" 
          min="0" 
          max="100" 
          bind:value={saturation}
          on:input={updateFromHsl}
          class="range range-xs range-secondary"
        />
      </div>

      <!-- Lightness -->
      <div class="mb-3">
        <div class="flex justify-between text-xs mb-1">
          <span>Lightness</span>
          <span>{lightness}%</span>
        </div>
        <input 
          type="range" 
          min="0" 
          max="100" 
          bind:value={lightness}
          on:input={updateFromHsl}
          class="range range-xs range-accent"
        />
      </div>
    </div>
  {/if}

  <!-- Preset Colors -->
  <div class="mb-4">
    <h4 class="text-sm font-semibold mb-2">Preset Colors</h4>
    <div class="grid grid-cols-5 gap-2">
      {#each presetColors as color}
        <button 
          class="w-8 h-8 rounded border-2 hover:scale-110 transition-transform {selectedColor === color ? 'border-primary border-4' : 'border-base-300'}"
          style="background-color: {color}"
          on:click={() => updateColor(color)}
          title={color}
        ></button>
      {/each}
    </div>
  </div>

  <!-- Color History -->
  {#if colorHistory.length > 0}
    <div class="mb-4">
      <div class="flex justify-between items-center mb-2">
        <h4 class="text-sm font-semibold">Recent Colors</h4>
        <button 
          class="btn btn-xs btn-ghost"
          on:click={clearHistory}
          title="Clear History"
        >
          🗑️
        </button>
      </div>
      <div class="flex flex-wrap gap-2">
        {#each colorHistory as color}
          <button 
            class="w-6 h-6 rounded border border-base-300 hover:scale-110 transition-transform"
            style="background-color: {color}"
            on:click={() => updateColor(color)}
            title={color}
          ></button>
        {/each}
      </div>
    </div>
  {/if}

  <!-- Color Info -->
  <div class="text-xs text-base-content/70">
    <div>Current: <span class="font-mono">{selectedColor}</span></div>
    <div>HSL: {hue}°, {saturation}%, {lightness}%</div>
  </div>
</div>

<style>
  .color-picker {
    min-height: 300px;
  }

  input[type="color"] {
    border: none;
    background: none;
  }

  input[type="color"]::-webkit-color-swatch-wrapper {
    padding: 0;
    border: none;
    border-radius: 6px;
  }

  input[type="color"]::-webkit-color-swatch {
    border: 2px solid oklch(var(--bc) / 0.2);
    border-radius: 6px;
  }
</style>