<script>
  import { onMount } from 'svelte';
  import { createEventDispatcher } from 'svelte';
  
  const dispatch = createEventDispatcher();
  
  // Available fonts for code editor
  const fonts = [
    { name: "Fira Code", value: "fira-code", url: "https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;400;500;600;700&display=swap", css: "'Fira Code', 'Courier New', monospace" },
    { name: "Source Code Pro", value: "source-code-pro", url: "https://fonts.googleapis.com/css2?family=Source+Code+Pro:wght@200;300;400;500;600;700;900&display=swap", css: "'Source Code Pro', 'Courier New', monospace" },
    { name: "JetBrains Mono", value: "jetbrains-mono", url: "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@100;200;300;400;500;600;700;800&display=swap", css: "'JetBrains Mono', 'Courier New', monospace" },
    { name: "Cascadia Code", value: "cascadia-code", url: "https://fonts.googleapis.com/css2?family=Cascadia+Code:wght@200;300;400;500;600;700&display=swap", css: "'Cascadia Code', 'Courier New', monospace" },
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
    
    // Load the font if it has a URL
    if (font.url) {
      loadFontCSS(font.url);
    }
    
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
    
    // Load the font CSS if it has a URL
    if (font.url) {
      loadFontCSS(font.url).then(() => {
        applyFontToEditor(font);
      });
    } else {
      applyFontToEditor(font);
    }
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
  
  // Function to load a font's CSS file from Google Fonts
  function loadFontCSS(url) {
    return new Promise((resolve, reject) => {
      // Check if this CSS file is already loaded
      const existingLink = document.querySelector(`link[href="${url}"]`);
      if (existingLink) {
        resolve();
        return;
      }

      console.log(`Loading font CSS from: ${url}`);

      // Load the CSS file
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = url;
      link.onload = () => resolve();
      link.onerror = () => {
        console.error(`Failed to load font CSS: ${url}`);
        reject(new Error(`Failed to load font: ${url}`));
      };

      document.head.appendChild(link);
    });
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