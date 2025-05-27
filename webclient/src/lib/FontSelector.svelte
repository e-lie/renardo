<script>
  import { onMount } from 'svelte';
  import { createEventDispatcher } from 'svelte';
  
  const dispatch = createEventDispatcher();
  
  // Available fonts for code editor
  const fonts = [
    { name: "Fira Code", value: "fira-code", local: true, css: "'Fira Code', 'Courier New', monospace" },
    { name: "Source Code Pro", value: "source-code-pro", local: true, css: "'Source Code Pro', 'Courier New', monospace" },
    { name: "JetBrains Mono", value: "jetbrains-mono", local: true, css: "'JetBrains Mono', 'Courier New', monospace" },
    { name: "JGS", value: "jgs", local: true, css: "'JGS', 'Courier New', monospace" },
    { name: "JGS5", value: "jgs5", local: true, css: "'JGS5', 'Courier New', monospace" },
    { name: "JGS7", value: "jgs7", local: true, css: "'JGS7', 'Courier New', monospace" },
    { name: "JGS9", value: "jgs9", local: true, css: "'JGS9', 'Courier New', monospace" },
    { name: "Monaco", value: "monaco", css: "monaco, 'Lucida Console', monospace" },
    { name: "Consolas", value: "consolas", css: "consolas, 'Courier New', monospace" },
    { name: "Menlo", value: "menlo", css: "menlo, 'Monaco', 'Courier New', monospace" },
    { name: "SF Mono", value: "sf-mono", css: "'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', 'Source Code Pro', monospace" }
  ];
  
  // Storage key
  const EDITOR_FONT_KEY = 'editor-font-family';
  
  // Default font
  let currentFont = "fira-code";
  
  // Reference to the CodeMirror editor instance
  export let editor = null;
  
  onMount(() => {
    // Load local fonts CSS first
    loadLocalFontsCSS();
    
    // Check for font in localStorage
    const savedFont = localStorage.getItem(EDITOR_FONT_KEY);
    if (savedFont) {
      currentFont = savedFont;
      setFontIfEditorReady(savedFont);
    } else {
      // Load default font
      setFontIfEditorReady(currentFont);
    }
  });
  
  // This function checks if the editor is ready before setting the font
  function setFontIfEditorReady(fontValue) {
    const font = fonts.find(f => f.value === fontValue);
    if (!font) return;
    
    // Apply the font to the editor using CSS injection
    applyFontToCMEditor(font.css);
  }
  
  // This function should be called when the editor is initialized
  export function initEditor(editorInstance) {
    editor = editorInstance;
    setFontIfEditorReady(currentFont);
  }
  
  // Function to change font
  function setFont(fontValue) {
    if (!fontValue) return;
    
    const font = fonts.find(f => f.value === fontValue);
    if (!font) return;
    
    // Apply the font immediately (local fonts are pre-loaded)
    applyFontToEditor(font);
  }
  
  function applyFontToEditor(font) {
    // Apply the font to the editor using CSS injection
    applyFontToCMEditor(font.css);
    
    // Update the current font
    currentFont = font.value;
    
    // Save to localStorage
    localStorage.setItem(EDITOR_FONT_KEY, font.value);
    
    // Dispatch a font change event for parent components
    dispatch('fontChange', { font: font.value });
  }
  
  // Function to apply font to CodeMirror editor by injecting CSS
  function applyFontToCMEditor(fontFamily) {
    // Remove existing font style if any
    const existingStyle = document.getElementById('codemirror-font-style');
    if (existingStyle) {
      existingStyle.remove();
    }
    
    // Create new style element
    const style = document.createElement('style');
    style.id = 'codemirror-font-style';
    style.textContent = `
      .CodeMirror {
        font-family: ${fontFamily} !important;
      }
      .CodeMirror pre,
      .CodeMirror-line,
      .CodeMirror-lines,
      .CodeMirror-code,
      .CodeMirror-scroll,
      .CodeMirror-sizer,
      .CodeMirror-gutter,
      .CodeMirror-gutters,
      .CodeMirror-linenumber {
        font-family: ${fontFamily} !important;
      }
    `;
    
    // Append to head
    document.head.appendChild(style);
    
    // Refresh the editor if it exists
    if (editor) {
      setTimeout(() => {
        editor.refresh();
      }, 100);
    }
  }
  
  // Function to load local fonts CSS file
  function loadLocalFontsCSS() {
    // Check if local fonts CSS is already loaded
    const existingLink = document.querySelector('link[href="/fonts/code-fonts.css"]');
    if (existingLink) {
      return;
    }

    console.log('Loading local code fonts CSS');

    // Load the local fonts CSS file
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = '/fonts/code-fonts.css';
    link.onload = () => console.log('Local code fonts loaded successfully');
    link.onerror = () => console.error('Failed to load local code fonts CSS');

    document.head.appendChild(link);
  }
  
  // Handle font dropdown change
  function handleFontChange(event) {
    const selectedFont = event.target.value;
    setFont(selectedFont);
  }
</script>

<div class="flex items-center">
  <span class="text-sm font-medium mr-2">Font:</span>
  <select 
    class="select select-bordered select-sm w-40" 
    bind:value={currentFont}
    on:change={handleFontChange}
  >
    {#each fonts as font}
      <option value={font.value}>{font.name}</option>
    {/each}
  </select>
</div>