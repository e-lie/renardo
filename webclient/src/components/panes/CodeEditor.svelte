<script>
  import { onMount, onDestroy } from 'svelte';
  import { PaneComponent } from '../../lib/newEditor/PaneComponent';
  import { sendDebugLog } from '../../lib/websocket.js';

  // Props
  export let componentId = null;
  export let title = 'Code Editor';

  // Component instance
  let component = null;
  let unsubscribe = null;

  // Editor elements
  let editorContainer;
  let editor;
  let textarea;

  // Local state synchronized with global state
  let content = '';
  let theme = 'dracula';
  let activeHighlights = new Map();
  let vimModeEnabled = false;
  let showLineNumbers = true;
  let fontSize = 14;
  let tabSize = 4;
  let lineWrapping = true;

  // Theme options
  const themeOptions = [
    { value: 'dracula', label: 'Dracula' },
    { value: 'monokai', label: 'Monokai' },
    { value: 'material', label: 'Material' },
    { value: 'solarized', label: 'Solarized' },
    { value: 'default', label: 'Default' }
  ];

  // Font size options
  const fontSizes = [10, 11, 12, 13, 14, 15, 16, 18, 20, 22, 24];

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
        lineNumbers: showLineNumbers,
        mode: {
          name: 'python',
          version: 3,
          singleLineStringErrors: false
        },
        theme: theme,
        tabSize: tabSize,
        indentWithTabs: false,
        indentUnit: tabSize,
        lineWrapping: lineWrapping,
        viewportMargin: Infinity,
        matchBrackets: true,
        autoCloseBrackets: true,
        styleActiveLine: true,
        smartIndent: true,
        electricChars: true,
        highlightSelectionMatches: true,
        autofocus: false
      };

      if (textarea) {
        editor = window.CodeMirror.fromTextArea(textarea, codeMirrorOptions);

        // Update local content and sync with global state when editor changes
        editor.on('change', (instance) => {
          content = instance.getValue();
          if (component) {
            component.updateData({ content, lastModified: new Date().toISOString() });
          }
        });

        // Handle Vim mode if enabled
        if (vimModeEnabled) {
          loadScript('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.11/keymap/vim.min.js').then(() => {
            if (window.CodeMirror.Vim && editor) {
              window.CodeMirror.Vim.map('jk', '<Esc>', 'insert');
              editor.setOption('keyMap', 'vim');
            }
          }).catch(err => {
            console.error('Failed to load Vim mode:', err);
          });
        }

        // Apply fontSize to CodeMirror
        updateEditorFontSize();

        // Refresh the editor
        setTimeout(() => {
          if (editor) {
            editor.refresh();
          }
        }, 100);

        sendDebugLog('DEBUG', 'CodeEditor: CodeMirror initialized', {
          componentId,
          theme,
          contentLength: content.length
        });
      }
    } catch (error) {
      console.error("Error initializing CodeMirror editor:", error);
    }
  }

  // Update editor font size
  function updateEditorFontSize() {
    if (editor) {
      const wrapper = editor.getWrapperElement();
      if (wrapper) {
        wrapper.style.fontSize = `${fontSize}px`;
        editor.refresh();
      }
    }
  }

  // Update theme
  function updateTheme() {
    if (editor) {
      loadCSS(`/codemirror-themes/${theme}.css`).then(() => {
        editor.setOption('theme', theme);
        if (component) {
          component.setDataProperty('theme', theme);
        }
      });
    }
  }

  // Toggle vim mode
  function toggleVimMode() {
    vimModeEnabled = !vimModeEnabled;
    if (component) {
      component.setDataProperty('vimModeEnabled', vimModeEnabled);
    }

    if (editor) {
      if (vimModeEnabled) {
        loadScript('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.11/keymap/vim.min.js').then(() => {
          if (window.CodeMirror.Vim) {
            window.CodeMirror.Vim.map('jk', '<Esc>', 'insert');
            editor.setOption('keyMap', 'vim');
          }
        }).catch(err => {
          console.error('Failed to load Vim mode:', err);
          vimModeEnabled = false;
          if (component) {
            component.setDataProperty('vimModeEnabled', false);
          }
        });
      } else {
        editor.setOption('keyMap', 'default');
      }
    }
  }

  // Toggle line numbers
  function toggleLineNumbers() {
    showLineNumbers = !showLineNumbers;
    if (editor) {
      editor.setOption('lineNumbers', showLineNumbers);
    }
    if (component) {
      component.setDataProperty('showLineNumbers', showLineNumbers);
    }
  }

  // Toggle line wrapping
  function toggleLineWrapping() {
    lineWrapping = !lineWrapping;
    if (editor) {
      editor.setOption('lineWrapping', lineWrapping);
    }
    if (component) {
      component.setDataProperty('lineWrapping', lineWrapping);
    }
  }

  // Update font size
  function updateFontSize() {
    if (component) {
      component.setDataProperty('fontSize', fontSize);
    }
    updateEditorFontSize();
  }

  // Update tab size
  function updateTabSize() {
    if (editor) {
      editor.setOption('tabSize', tabSize);
      editor.setOption('indentUnit', tabSize);
    }
    if (component) {
      component.setDataProperty('tabSize', tabSize);
    }
  }

  // Execute current selection/paragraph/line
  function executeCode(mode = 'paragraph') {
    if (!editor) return;

    let codeToExecute = '';
    let from, to;

    if (editor.somethingSelected()) {
      codeToExecute = editor.getSelection();
      from = editor.getCursor('from');
      to = editor.getCursor('to');
    } else if (mode === 'line') {
      const cursor = editor.getCursor();
      const line = cursor.line;
      codeToExecute = editor.getLine(line);
      from = { line, ch: 0 };
      to = { line, ch: codeToExecute.length };
    } else {
      // Get paragraph
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

      from = { line: startLine, ch: 0 };
      to = { line: endLine, ch: editor.getLine(endLine).length };
      codeToExecute = editor.getRange(from, to);
    }

    if (codeToExecute.trim()) {
      sendDebugLog('INFO', 'CodeEditor: Code execution requested', {
        mode,
        codeLength: codeToExecute.length,
        from,
        to
      });

      // Here you would integrate with the execution system
      // For now, just highlight the executed code
      highlightExecutedCode(from, to);
    }
  }

  // Highlight executed code
  function highlightExecutedCode(from, to) {
    if (!editor) return;

    const marker = editor.markText(from, to, {
      className: 'executed-code-highlight',
      clearOnEnter: false
    });

    // Remove highlight after animation
    setTimeout(() => {
      marker.clear();
    }, 800);
  }

  onMount(() => {
    sendDebugLog('DEBUG', 'CodeEditor onMount', {
      componentId: componentId,
      title: title
    });

    // Create component instance
    component = new PaneComponent({
      id: componentId,
      type: 'CodeEditor',
      title: title,
      initialData: {
        content,
        theme,
        vimModeEnabled,
        showLineNumbers,
        fontSize,
        tabSize,
        lineWrapping,
        lastModified: new Date().toISOString()
      }
    });

    // Subscribe to global state changes
    unsubscribe = component.getGlobalState().subscribe((data) => {
      if (data.content !== undefined && data.content !== content) {
        content = data.content;
        if (editor && editor.getValue() !== content) {
          editor.setValue(content);
        }
      }
      if (data.theme !== undefined && data.theme !== theme) {
        theme = data.theme;
        updateTheme();
      }
      if (data.vimModeEnabled !== undefined) vimModeEnabled = data.vimModeEnabled;
      if (data.showLineNumbers !== undefined) showLineNumbers = data.showLineNumbers;
      if (data.fontSize !== undefined) {
        fontSize = data.fontSize;
        updateEditorFontSize();
      }
      if (data.tabSize !== undefined) {
        tabSize = data.tabSize;
        updateTabSize();
      }
      if (data.lineWrapping !== undefined) {
        lineWrapping = data.lineWrapping;
        if (editor) {
          editor.setOption('lineWrapping', lineWrapping);
        }
      }
    });

    component.setActive(true);
    
    // Initialize CodeMirror after component is set up
    setTimeout(initEditor, 100);
  });

  onDestroy(() => {
    if (unsubscribe) {
      unsubscribe();
    }
    if (component) {
      component.setActive(false);
    }
    if (editor) {
      editor.toTextArea();
    }
  });
</script>

<div class="code-editor-pane h-full flex flex-col">
  <!-- Header with controls -->
  <div class="flex items-center justify-between p-2 border-b border-base-300 flex-shrink-0 bg-base-200">
    <h3 class="text-sm font-semibold">Code Editor</h3>
    <div class="flex items-center gap-2">
      <!-- Theme Selector -->
      <div class="dropdown dropdown-end">
        <label tabindex="0" class="btn btn-xs btn-ghost">🎨</label>
        <div tabindex="0" class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-48">
          <div class="form-control mb-2">
            <label class="label py-1">
              <span class="label-text text-xs">Theme</span>
            </label>
            <select 
              bind:value={theme}
              on:change={updateTheme}
              class="select select-xs w-full"
            >
              {#each themeOptions as themeOption}
                <option value={themeOption.value}>{themeOption.label}</option>
              {/each}
            </select>
          </div>
        </div>
      </div>
      
      <!-- Settings -->
      <div class="dropdown dropdown-end">
        <label tabindex="0" class="btn btn-xs btn-ghost">⚙️</label>
        <div tabindex="0" class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-64">
          <!-- Font Size -->
          <div class="form-control mb-2">
            <label class="label py-1">
              <span class="label-text text-xs">Font Size: {fontSize}px</span>
            </label>
            <select 
              bind:value={fontSize}
              on:change={updateFontSize}
              class="select select-xs w-full"
            >
              {#each fontSizes as size}
                <option value={size}>{size}px</option>
              {/each}
            </select>
          </div>
          
          <!-- Tab Size -->
          <div class="form-control mb-2">
            <label class="label py-1">
              <span class="label-text text-xs">Tab Size: {tabSize}</span>
            </label>
            <input 
              type="range" 
              min="2" 
              max="8" 
              bind:value={tabSize}
              on:input={updateTabSize}
              class="range range-xs"
            />
          </div>
          
          <!-- Toggles -->
          <div class="form-control">
            <label class="cursor-pointer label py-1">
              <span class="label-text text-xs">Line Numbers</span>
              <input 
                type="checkbox" 
                bind:checked={showLineNumbers}
                on:change={toggleLineNumbers}
                class="toggle toggle-xs"
              />
            </label>
          </div>
          
          <div class="form-control">
            <label class="cursor-pointer label py-1">
              <span class="label-text text-xs">Line Wrapping</span>
              <input 
                type="checkbox" 
                bind:checked={lineWrapping}
                on:change={toggleLineWrapping}
                class="toggle toggle-xs"
              />
            </label>
          </div>
          
          <div class="form-control">
            <label class="cursor-pointer label py-1">
              <span class="label-text text-xs">Vim Mode</span>
              <input 
                type="checkbox" 
                bind:checked={vimModeEnabled}
                on:change={toggleVimMode}
                class="toggle toggle-xs"
              />
            </label>
          </div>
        </div>
      </div>
      
      <!-- Execute buttons -->
      <div class="dropdown dropdown-end">
        <label tabindex="0" class="btn btn-xs btn-primary">▶</label>
        <ul tabindex="0" class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-48">
          <li><button on:click={() => executeCode('paragraph')} class="text-xs">Run Paragraph (Ctrl+Enter)</button></li>
          <li><button on:click={() => executeCode('line')} class="text-xs">Run Line (Alt+Enter)</button></li>
          <li><button on:click={() => executeCode('selection')} class="text-xs">Run Selection</button></li>
        </ul>
      </div>
    </div>
  </div>

  <!-- Editor Container -->
  <div class="flex-1 min-h-0 relative" style="flex: 1; min-height: 0; overflow: hidden;">
    <div class="w-full h-full" bind:this={editorContainer}>
      <textarea bind:this={textarea}>{content}</textarea>
    </div>
  </div>
</div>

<style>
  /* Make CodeMirror look better */
  :global(.CodeMirror) {
    height: 100% !important;
    width: 100%;
    font-family: 'Fira Code', 'Menlo', 'Monaco', 'Courier New', monospace;
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

  /* Executed code highlighting */
  :global(.executed-code-highlight) {
    background-color: rgba(0, 255, 255, 0.3);
    animation: highlight-blink 0.8s ease-in-out;
  }

  @keyframes highlight-blink {
    0% { background-color: rgba(0, 255, 255, 0.6); }
    50% { background-color: rgba(0, 255, 255, 0.2); }
    100% { background-color: transparent; }
  }

  .code-editor-pane {
    min-height: 300px;
  }

  .dropdown:focus-within .dropdown-content {
    display: block;
  }
</style>