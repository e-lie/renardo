<script>
  import { onMount, createEventDispatcher } from 'svelte';
  
  const dispatch = createEventDispatcher();
  
  // Available themes and fonts
  const themes = [
    { name: "Monokai", value: "monokai" },
    { name: "Dracula", value: "dracula" },
    { name: "Material", value: "material" },
    { name: "Nord", value: "nord" },
    { name: "Solarized Dark", value: "solarized-dark" },
    { name: "Solarized Light", value: "solarized-light" },
    { name: "Darcula", value: "darcula" },
    { name: "Eclipse", value: "eclipse" }
  ];
  
  const fonts = [
    { name: "Fira Code", value: "fira-code" },
    { name: "Source Code Pro", value: "source-code-pro" },
    { name: "JetBrains Mono", value: "jetbrains-mono" },
    { name: "JGS", value: "jgs" },
    { name: "JGS5", value: "jgs5" },
    { name: "JGS7", value: "jgs7" },
    { name: "JGS9", value: "jgs9" },
    { name: "Monaco", value: "monaco" },
    { name: "Consolas", value: "consolas" },
    { name: "Menlo", value: "menlo" },
    { name: "SF Mono", value: "sf-mono" }
  ];
  
  // Settings state
  let editorTheme = 'dracula';
  let editorFont = 'fira-code';
  let showLineNumbers = true;
  let vimModeEnabled = false;
  
  // Loading state
  let isApplyingSettings = false;
  
  // Load settings from localStorage
  function loadSettings() {
    const savedTheme = localStorage.getItem('editor-theme');
    if (savedTheme) {
      editorTheme = savedTheme;
    }
    
    const savedFont = localStorage.getItem('editor-font-family');
    if (savedFont) {
      editorFont = savedFont;
    }
    
    const savedLineNumbers = localStorage.getItem('editor-show-line-numbers');
    if (savedLineNumbers !== null) {
      showLineNumbers = savedLineNumbers !== 'false';
    }
    
    const savedVimMode = localStorage.getItem('editor-vim-mode');
    if (savedVimMode !== null) {
      vimModeEnabled = savedVimMode === 'true';
    }
  }
  
  // Apply settings and save to localStorage
  async function applySettings() {
    isApplyingSettings = true;
    
    try {
      // Save to localStorage
      localStorage.setItem('editor-theme', editorTheme);
      localStorage.setItem('editor-font-family', editorFont);
      localStorage.setItem('editor-show-line-numbers', showLineNumbers.toString());
      localStorage.setItem('editor-vim-mode', vimModeEnabled.toString());
      
      // Dispatch event to notify parent components
      dispatch('settingsChanged', {
        theme: editorTheme,
        font: editorFont,
        lineNumbers: showLineNumbers,
        vimMode: vimModeEnabled
      });
      
      // Show success feedback briefly
      await new Promise(resolve => setTimeout(resolve, 500));
    } finally {
      isApplyingSettings = false;
    }
  }
  
  // Handle individual setting changes and auto-apply
  function handleThemeChange() {
    applySettings();
  }
  
  function handleFontChange() {
    applySettings();
  }
  
  function handleLineNumbersChange() {
    applySettings();
  }
  
  function handleVimModeChange() {
    applySettings();
  }
  
  onMount(() => {
    loadSettings();
  });
</script>

<div class="space-y-4">
  <div class="text-center mb-4">
    <h3 class="text-lg font-semibold">Editor Settings</h3>
    <p class="text-sm text-base-content/70">Customize your code editor appearance and behavior</p>
  </div>
  
  <!-- Theme selector -->
  <div class="form-control">
    <div class="label">
      <span class="label-text font-medium">Theme</span>
    </div>
    <select 
      class="select select-bordered select-sm w-full"
      bind:value={editorTheme}
      on:change={handleThemeChange}
    >
      {#each themes as theme}
        <option value={theme.value}>{theme.name}</option>
      {/each}
    </select>
  </div>
  
  <!-- Font selector -->
  <div class="form-control">
    <div class="label">
      <span class="label-text font-medium">Font</span>
    </div>
    <select 
      class="select select-bordered select-sm w-full"
      bind:value={editorFont}
      on:change={handleFontChange}
    >
      {#each fonts as font}
        <option value={font.value}>{font.name}</option>
      {/each}
    </select>
  </div>
  
  <!-- Line numbers toggle -->
  <div class="form-control">
    <label class="label cursor-pointer justify-start gap-3">
      <input 
        type="checkbox" 
        class="checkbox checkbox-primary checkbox-sm" 
        bind:checked={showLineNumbers}
        on:change={handleLineNumbersChange}
      />
      <span class="label-text font-medium">Show line numbers</span>
    </label>
  </div>
  
  <!-- Vim mode toggle -->
  <div class="form-control">
    <label class="label cursor-pointer justify-start gap-3">
      <input 
        type="checkbox" 
        class="checkbox checkbox-primary checkbox-sm" 
        bind:checked={vimModeEnabled}
        on:change={handleVimModeChange}
      />
      <span class="label-text font-medium">Enable Vim mode</span>
    </label>
  </div>
  
  <!-- Status indicator -->
  {#if isApplyingSettings}
    <div class="alert alert-info py-2">
      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-4 w-4" fill="none" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <span class="text-sm">Applying settings...</span>
    </div>
  {/if}
  
</div>