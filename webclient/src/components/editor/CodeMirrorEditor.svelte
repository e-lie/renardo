<script>
  import { onMount, onDestroy, createEventDispatcher } from 'svelte';
  
  export let content = '';
  export let theme = 'dracula';
  export let activeHighlights = new Map();
  
  const dispatch = createEventDispatcher();
  
  let editorContainer;
  let editor;
  let textarea;
  
  // Function to load a script dynamically
  const loadScript = (src) => {
    return new Promise((resolve, reject) => {
      const existingScript = document.querySelector(`script[src="${src}"]`);
      if (existingScript) {
        resolve();
        return;
      }

      const script = document.createElement('script');
      script.src = src;
      script.onload = () => resolve();
      script.onerror = () => reject(new Error(`Failed to load script: ${src}`));
      document.head.appendChild(script);
    });
  };
  
  // Function to load a CSS file dynamically
  const loadCSS = (href) => {
    return new Promise((resolve, reject) => {
      const existingLink = document.querySelector(`link[href="${href}"]`);
      if (existingLink) {
        resolve();
        return;
      }

      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = href;
      link.onload = () => resolve();
      link.onerror = () => reject(new Error(`Failed to load CSS: ${href}`));
      document.head.appendChild(link);
    });
  };
  
  // Initialize CodeMirror
  async function initEditor() {
    if (typeof window.CodeMirror === 'undefined') {
      setTimeout(initEditor, 100);
      return;
    }
    
    try {
      // Load CodeMirror core CSS
      await loadCSS('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.11/codemirror.min.css');

      // Load theme CSS
      await loadCSS(`/codemirror-themes/${theme}.css`);
      
      // Load CodeMirror addons and modes
      await Promise.all([
        loadScript('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.11/mode/python/python.min.js'),
        loadScript('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.11/addon/edit/matchbrackets.min.js'),
        loadScript('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.11/addon/edit/closebrackets.min.js'),
        loadScript('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.11/addon/selection/active-line.min.js'),
        loadScript('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.11/addon/search/search.min.js'),
        loadScript('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.11/addon/search/searchcursor.min.js'),
        loadScript('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.11/addon/search/match-highlighter.min.js')
      ]).catch(err => {
        console.error("Error loading CodeMirror addons:", err);
      });
      
      // Initialize CodeMirror
      const codeMirrorOptions = {
        value: content,
        lineNumbers: true,
        mode: {
          name: 'python',
          version: 3,
          singleLineStringErrors: false
        },
        theme: theme,
        tabSize: 4,
        indentWithTabs: false,
        indentUnit: 4,
        lineWrapping: true,
        viewportMargin: Infinity,
        matchBrackets: true,
        autoCloseBrackets: true,
        styleActiveLine: true,
        smartIndent: true,
        electricChars: true,
        highlightSelectionMatches: true,
        autofocus: true
      };
    
      if (textarea) {
        editor = window.CodeMirror.fromTextArea(textarea, codeMirrorOptions);

        // Update local content when editor changes
        editor.on('change', (instance) => {
          dispatch('change', { value: instance.getValue() });
        });

        // Add key bindings
        editor.setOption('extraKeys', {
          'Ctrl-Enter': () => dispatch('execute', { mode: 'paragraph' }),
          'Cmd-Enter': () => dispatch('execute', { mode: 'paragraph' }),
          'Alt-Enter': () => dispatch('execute', { mode: 'line' }),
          'Alt-Cmd-Enter': () => dispatch('execute', { mode: 'line' })
        });

        // Apply saved settings
        const showLineNumbers = localStorage.getItem('editor-show-line-numbers') !== 'false';
        const vimModeEnabled = localStorage.getItem('editor-vim-mode') === 'true';

        editor.setOption('lineNumbers', showLineNumbers);

        // Handle Vim mode if enabled
        if (vimModeEnabled) {
          loadScript('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.11/keymap/vim.min.js').then(() => {
            if (window.CodeMirror.Vim) {
              window.CodeMirror.Vim.map('jk', '<Esc>', 'insert');
              editor.setOption('keyMap', 'vim');
            }
          }).catch(err => {
            console.error('Failed to load Vim mode:', err);
            localStorage.setItem('editor-vim-mode', 'false');
          });
        }

        // Refresh the editor
        setTimeout(() => {
          editor.refresh();
        }, 100);
        
        // Dispatch editor ready event
        dispatch('ready', { editor });
      }
    } catch (error) {
      console.error("Error initializing CodeMirror editor:", error);
    }
  }
  
  // Get current paragraph
  export function getCurrentParagraph() {
    if (!editor) return '';
    
    const cursor = editor.getCursor();
    const line = cursor.line;
    
    let startLine = line;
    while (startLine > 0) {
      const prevLine = editor.getLine(startLine - 1);
      if (!prevLine || prevLine.trim() === '') {
        break;
      }
      startLine--;
    }
    
    let endLine = line;
    const totalLines = editor.lineCount();
    while (endLine < totalLines - 1) {
      const nextLine = editor.getLine(endLine + 1);
      if (!nextLine || nextLine.trim() === '') {
        break;
      }
      endLine++;
    }
    
    const from = { line: startLine, ch: 0 };
    const to = { line: endLine, ch: editor.getLine(endLine).length };
    return { text: editor.getRange(from, to), from, to };
  }
  
  // Get current line
  export function getCurrentLine() {
    if (!editor) return '';
    
    const cursor = editor.getCursor();
    const line = cursor.line;
    const text = editor.getLine(line);
    const from = { line, ch: 0 };
    const to = { line, ch: text.length };
    
    return { text, from, to };
  }
  
  // Get selection
  export function getSelection() {
    if (!editor) return null;
    
    if (editor.somethingSelected()) {
      return {
        text: editor.getSelection(),
        from: editor.getCursor('from'),
        to: editor.getCursor('to')
      };
    }
    return null;
  }
  
  // Get all text
  export function getAllText() {
    if (!editor) return '';
    
    const text = editor.getValue();
    const lastLine = editor.lineCount() - 1;
    const from = { line: 0, ch: 0 };
    const to = { line: lastLine, ch: editor.getLine(lastLine).length };
    
    return { text, from, to };
  }
  
  // Highlight executed code
  export function highlightExecutedCode(from, to, requestId) {
    if (!editor) return;
    
    const marker = editor.markText(from, to, {
      className: 'executed-code-highlight',
      clearOnEnter: false
    });
    
    activeHighlights.set(requestId, marker);
    
    // Remove highlight after animation
    setTimeout(() => {
      if (activeHighlights.has(requestId)) {
        marker.clear();
        activeHighlights.delete(requestId);
      }
    }, 300);
  }
  
  // Remove highlight
  export function removeExecutionHighlight(requestId) {
    if (activeHighlights.has(requestId)) {
      const marker = activeHighlights.get(requestId);
      marker.clear();
      activeHighlights.delete(requestId);
    }
  }
  
  // Update content
  export function setValue(value) {
    if (editor && editor.getValue() !== value) {
      editor.setValue(value);
    }
  }
  
  // Get current value
  export function getValue() {
    return editor ? editor.getValue() : '';
  }
  
  // Focus editor
  export function focus() {
    if (editor) {
      editor.focus();
    }
  }
  
  // Check if editor has focus
  export function hasFocus() {
    return editor ? editor.hasFocus() : false;
  }
  
  // Set cursor position
  export function setCursor(pos) {
    if (editor) {
      editor.setCursor(pos);
    }
  }
  
  // Insert text at cursor
  export function insertAtCursor(text) {
    if (editor) {
      const cursor = editor.getCursor();
      editor.replaceRange(text + '\n', cursor);
      editor.setCursor({ line: cursor.line + text.split('\n').length, ch: 0 });
      editor.focus();
    }
  }
  
  // Update theme
  export function setTheme(newTheme) {
    if (editor) {
      loadCSS(`/codemirror-themes/${newTheme}.css`).then(() => {
        editor.setOption('theme', newTheme);
      });
    }
  }
  
  onMount(() => {
    initEditor();
  });
  
  onDestroy(() => {
    if (editor) {
      editor.toTextArea();
    }
  });
</script>

<div class="w-full h-full" bind:this={editorContainer}>
  <textarea id="code-editor" bind:this={textarea}></textarea>
</div>

<style>
  /* Make CodeMirror look better */
  :global(.CodeMirror) {
    height: 100% !important;
    width: 100%;
    font-family: 'Fira Code', 'Menlo', 'Monaco', 'Courier New', monospace;
    font-size: 14px;
    line-height: 1.5;
  }
  
  /* Ensure the editor container has proper height constraints */
  :global(.CodeMirror-scroll) {
    max-height: 100%;
    overflow-y: auto !important;
  }

  /* Let themes handle gutter colors - default theme fallback */
  :global(.CodeMirror-gutters) {
    border-right: 1px solid rgba(0, 0, 0, 0.1);
  }

  :global(.CodeMirror-linenumber) {
    color: inherit;
    opacity: 0.6;
  }

  /* Make sure the textarea is hidden properly */
  #code-editor {
    display: none;
  }
  
  /* Executed code highlighting */
  :global(.executed-code-highlight) {
    background-color: rgba(0, 255, 255, 0.3);
    animation: highlight-blink 0.5s ease-in-out;
  }
  
  @keyframes highlight-blink {
    0% { background-color: rgba(0, 255, 255, 0.6); }
    50% { background-color: rgba(0, 255, 255, 0.2); }
    100% { background-color: transparent; }
  }
</style>