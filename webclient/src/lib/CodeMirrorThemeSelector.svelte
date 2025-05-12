<script>
  import { onMount } from 'svelte';
  
  // Available themes - these are commonly used CodeMirror themes
  const themes = [
    { name: "Monokai", value: "monokai" },
    { name: "Dracula", value: "dracula" },
    { name: "Material", value: "material" },
    { name: "Nord", value: "nord" },
    { name: "Solarized Dark", value: "solarized dark" },
    { name: "Solarized Light", value: "solarized light" },
    { name: "Darcula", value: "darcula" },
    { name: "Eclipse", value: "eclipse" }
  ];
  
  // Storage key for the editor theme
  const EDITOR_THEME_KEY = 'editor-theme';
  
  // Default theme
  let currentTheme = "monokai";
  
  // Reference to the CodeMirror editor instance
  export let editor = null;
  
  onMount(() => {
    // Check for theme in localStorage
    const savedTheme = localStorage.getItem(EDITOR_THEME_KEY);
    if (savedTheme) {
      currentTheme = savedTheme;
      setThemeIfEditorReady(savedTheme);
    }
  });
  
  // This function checks if the editor is ready before setting the theme
  function setThemeIfEditorReady(theme) {
    if (editor) {
      editor.setOption("theme", theme);
    }
  }
  
  // This function should be called when the editor is initialized
  export function initEditor(editorInstance) {
    editor = editorInstance;
    setThemeIfEditorReady(currentTheme);
  }
  
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
    });
  }
  
  // Function to load a theme's CSS file
  function loadThemeCSS(theme) {
    return new Promise((resolve, reject) => {
      // Convert spaces to hyphens in the theme name for the CSS file
      const themeFile = theme.replace(/\s+/g, '-');
      const cssUrl = `https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.11/theme/${themeFile}.min.css`;
      
      // Check if this CSS file is already loaded
      const existingLink = document.querySelector(`link[href="${cssUrl}"]`);
      if (existingLink) {
        resolve();
        return;
      }
      
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
</script>

<div class="card bg-base-100 shadow-xl mb-4">
  <div class="card-body">
    <h2 class="card-title title-font">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 mr-2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M17.25 6.75L22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3l-4.5 16.5" />
      </svg>
      Editor Theme
    </h2>
    
    <div class="flex flex-wrap gap-2 mt-2">
      {#each themes as theme}
        <button 
          class="btn btn-sm {currentTheme === theme.value ? 'btn-primary' : 'btn-outline'}"
          on:click={() => setTheme(theme.value)}
        >
          {theme.name}
        </button>
      {/each}
    </div>
  </div>
</div>