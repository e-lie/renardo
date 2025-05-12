<script>
  import { onMount } from 'svelte';

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

  // Default settings
  let currentTheme = "monokai";
  let showLineNumbers = true;

  // Reference to the CodeMirror editor instance
  export let editor = null;

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

  // This function should be called when the editor is initialized
  export function initEditor(editorInstance) {
    editor = editorInstance;
    setThemeIfEditorReady(currentTheme);
    toggleLineNumbersIfEditorReady(showLineNumbers);
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

  // Function to toggle line numbers
  function toggleLineNumbers(show) {
    showLineNumbers = show;

    if (editor) {
      editor.setOption("lineNumbers", show);
    }

    // Save to localStorage
    localStorage.setItem(SHOW_LINE_NUMBERS_KEY, show.toString());
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

<div class="flex items-center gap-3 my-1">
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

  <label class="flex items-center cursor-pointer">
    <input
      type="checkbox"
      class="checkbox checkbox-sm mr-2"
      bind:checked={showLineNumbers}
      on:change={() => toggleLineNumbers(showLineNumbers)}
    />
    <span class="text-sm font-medium">Show line numbers</span>
  </label>
</div>