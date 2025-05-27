<script>
  import { onMount } from 'svelte';
  import FontSelector from './FontSelector.svelte';
  
  // Available themes - these are commonly used CodeMirror themes
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
  
  // Storage keys
  const EDITOR_THEME_KEY = 'editor-theme';
  const SHOW_LINE_NUMBERS_KEY = 'editor-show-line-numbers';
  const VIM_MODE_KEY = 'editor-vim-mode';
  
  // Default settings
  let currentTheme = "dracula";
  let showLineNumbers = true;
  let vimModeEnabled = false;
  
  // Reference to the CodeMirror editor instance
  export let editor = null;
  
  // Reference to the FontSelector component
  let fontSelector;
  
  onMount(() => {
    // Check for theme in localStorage
    const savedTheme = localStorage.getItem(EDITOR_THEME_KEY);
    if (savedTheme) {
      currentTheme = savedTheme;
      setThemeIfEditorReady(savedTheme);
    }
    
    // Check for line numbers setting in localStorage
    const showLineNumbersSetting = localStorage.getItem(SHOW_LINE_NUMBERS_KEY);
    if (showLineNumbersSetting !== null) {
      showLineNumbers = showLineNumbersSetting === 'true';
      toggleLineNumbersIfEditorReady(showLineNumbers);
    }
    
    // Check for Vim mode setting in localStorage
    const vimModeSetting = localStorage.getItem(VIM_MODE_KEY);
    if (vimModeSetting !== null) {
      vimModeEnabled = vimModeSetting === 'true';
      toggleVimModeIfEditorReady(vimModeEnabled);
    }
  });
  
  // This function checks if the editor is ready before setting the theme
  function setThemeIfEditorReady(theme) {
    if (editor) {
      editor.setOption("theme", theme);
    }
  }
  
  // This function checks if the editor is ready before toggling line numbers
  function toggleLineNumbersIfEditorReady(show) {
    if (editor) {
      editor.setOption("lineNumbers", show);
    }
  }
  
  // This function loads Vim mode and enables/disables it
  async function toggleVimModeIfEditorReady(enable) {
    if (!editor) return;
    
    if (enable) {
      // Load the Vim keymap if needed
      try {
        // First check if CodeMirror.Vim is already available
        if (typeof window.CodeMirror.Vim === 'undefined') {
          // Need to load the script
          await loadVimMode();
        }
        
        // Enable Vim mode
        window.CodeMirror.Vim.map('jk', '<Esc>', 'insert');  // Add a common Vim mapping for convenience
        editor.setOption('keyMap', 'vim');
      } catch (error) {
        console.error('Failed to load Vim mode:', error);
        vimModeEnabled = false;
        localStorage.setItem(VIM_MODE_KEY, 'false');
        return;
      }
    } else {
      // Disable Vim mode
      editor.setOption('keyMap', 'default');
    }
  }
  
  // Load Vim mode scripts
  function loadVimMode() {
    return new Promise((resolve, reject) => {
      // First load the key map script
      const vimScript = document.createElement('script');
      vimScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.11/keymap/vim.min.js';
      vimScript.onload = () => resolve();
      vimScript.onerror = () => reject(new Error('Failed to load Vim mode'));
      document.head.appendChild(vimScript);
    });
  }
  
  // This function should be called when the editor is initialized
  export function initEditor(editorInstance) {
    editor = editorInstance;
    setThemeIfEditorReady(currentTheme);
    toggleLineNumbersIfEditorReady(showLineNumbers);
    toggleVimModeIfEditorReady(vimModeEnabled);
    
    // Initialize the font selector with the editor
    if (fontSelector) {
      fontSelector.initEditor(editorInstance);
    }
  }
  
  // Create a custom event dispatcher
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();

  // Function to change theme
  function setTheme(theme) {
    if (!theme) return;
    
    // First load the CSS file for the theme if it's not already loaded
    loadThemeCSS(theme).then(() => {
      // Set the theme in the editor
      if (editor) {
        editor.setOption("theme", theme);
      }
      
      // Update the current theme
      currentTheme = theme;
      
      // Save to localStorage
      localStorage.setItem(EDITOR_THEME_KEY, theme);
      
      // Dispatch a theme change event for parent components
      dispatch('themeChange', { theme });
    });
  }
  
  // Function to toggle line numbers
  function toggleLineNumbers(show) {
    showLineNumbers = show;
    
    if (editor) {
      editor.setOption("lineNumbers", show);
    }
    
    // Save to localStorage
    localStorage.setItem(SHOW_LINE_NUMBERS_KEY, show.toString());
  }
  
  // Function to toggle Vim mode
  async function toggleVimMode(enable) {
    vimModeEnabled = enable;
    
    await toggleVimModeIfEditorReady(enable);
    
    // Save to localStorage
    localStorage.setItem(VIM_MODE_KEY, enable.toString());
  }
  
  // Function to load a theme's CSS file from our local theme directory
  function loadThemeCSS(theme) {
    return new Promise((resolve, reject) => {
      // Use our local theme files in the public directory
      const cssUrl = `/codemirror-themes/${theme}.css`;

      // Check if this CSS file is already loaded
      const existingLink = document.querySelector(`link[href="${cssUrl}"]`);
      if (existingLink) {
        resolve();
        return;
      }

      console.log(`Loading CodeMirror theme: ${theme} from ${cssUrl}`);

      // Load the CSS file
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = cssUrl;
      link.onload = () => resolve();
      link.onerror = () => {
        console.error(`Failed to load CodeMirror theme CSS: ${cssUrl}`);
        reject(new Error(`Failed to load theme: ${theme}`));
      };

      document.head.appendChild(link);
    });
  }
  
  // Handle theme dropdown change
  function handleThemeChange(event) {
    const selectedTheme = event.target.value;
    setTheme(selectedTheme);
  }
</script>

<div class="flex flex-wrap items-center gap-3 my-1">
  <div class="flex items-center">
    <span class="text-sm font-medium mr-2">Theme:</span>
    <select 
      class="select select-bordered select-sm w-40" 
      bind:value={currentTheme}
      on:change={handleThemeChange}
    >
      {#each themes as theme}
        <option value={theme.value}>{theme.name}</option>
      {/each}
    </select>
  </div>
  
  <FontSelector bind:this={fontSelector} />
  
  <label class="flex items-center cursor-pointer">
    <input 
      type="checkbox" 
      class="checkbox checkbox-sm mr-2" 
      bind:checked={showLineNumbers}
      on:change={() => toggleLineNumbers(showLineNumbers)}
    />
    <span class="text-sm font-medium">Line numbers</span>
  </label>
  
  <label class="flex items-center cursor-pointer">
    <input 
      type="checkbox" 
      class="checkbox checkbox-sm mr-2" 
      bind:checked={vimModeEnabled}
      on:change={() => toggleVimMode(vimModeEnabled)}
    />
    <span class="text-sm font-medium">Vim mode</span>
  </label>
</div>