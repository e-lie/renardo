<script>
  import { onMount, onDestroy } from 'svelte';
  import { PaneComponent } from '../../lib/newEditor/PaneComponent';
  import { sendDebugLog } from '../../lib/websocket.js';
  import { editorSettings } from '../../stores/editorSettings.js';

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
  let activeHighlights = new Map();
  
  // Editor settings from global store
  let theme = 'dracula';
  let vimModeEnabled = false;
  let showLineNumbers = true;
  let fontSize = 14;
  let fontFamily = 'fira-code';
  let lineHeight = 1.5;
  let tabSize = 4;
  let lineWrapping = true;
  
  // Subscribe to global editor settings
  let settingsUnsubscribe = null;

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

        // Apply font settings to CodeMirror
        updateEditorFont();

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

  // Update editor font settings
  function updateEditorFont() {
    if (editor) {
      const wrapper = editor.getWrapperElement();
      if (wrapper) {
        wrapper.style.fontSize = `${fontSize}px`;
        wrapper.style.fontFamily = getFontFamilyCSS(fontFamily);
        wrapper.style.lineHeight = lineHeight.toString();
        editor.refresh();
      }
    }
  }
  
  // Get CSS font family string from font family value
  function getFontFamilyCSS(fontFamilyValue) {
    const fontMap = {
      'fira-code': "'Fira Code', 'Menlo', 'Monaco', 'Courier New', monospace",
      'source-code-pro': "'Source Code Pro', 'Menlo', 'Monaco', 'Courier New', monospace",
      'jetbrains-mono': "'JetBrains Mono', 'Menlo', 'Monaco', 'Courier New', monospace",
      'jgs': "'JGS', 'Courier New', monospace",
      'jgs5': "'JGS5', 'Courier New', monospace",
      'jgs7': "'JGS7', 'Courier New', monospace",
      'jgs9': "'JGS9', 'Courier New', monospace",
      'monaco': "'Monaco', 'Menlo', 'Courier New', monospace",
      'consolas': "'Consolas', 'Monaco', 'Courier New', monospace",
      'menlo': "'Menlo', 'Monaco', 'Courier New', monospace",
      'sf-mono': "'SF Mono', 'Monaco', 'Courier New', monospace"
    };
    return fontMap[fontFamilyValue] || fontMap['fira-code'];
  }

  // Update theme
  function updateTheme(newTheme) {
    if (editor && newTheme) {
      loadCSS(`/codemirror-themes/${newTheme}.css`).then(() => {
        editor.setOption('theme', newTheme);
        if (component) {
          component.setDataProperty('theme', newTheme);
        }
      });
    }
  }

  // Apply vim mode settings
  function applyVimMode(enabled) {
    if (editor) {
      if (enabled) {
        loadScript('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.11/keymap/vim.min.js').then(() => {
          if (window.CodeMirror.Vim) {
            window.CodeMirror.Vim.map('jk', '<Esc>', 'insert');
            editor.setOption('keyMap', 'vim');
          }
        }).catch(err => {
          console.error('Failed to load Vim mode:', err);
        });
      } else {
        editor.setOption('keyMap', 'default');
      }
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

    // Subscribe to global editor settings
    settingsUnsubscribe = editorSettings.subscribe(settings => {
      const themeChanged = theme !== settings.theme;
      const fontChanged = fontSize !== settings.fontSize || fontFamily !== settings.fontFamily || lineHeight !== settings.lineHeight;
      const tabSizeChanged = tabSize !== settings.tabSize;
      const lineNumbersChanged = showLineNumbers !== settings.showLineNumbers;
      const lineWrappingChanged = lineWrapping !== settings.lineWrapping;
      const vimModeChanged = vimModeEnabled !== settings.vimModeEnabled;
      
      theme = settings.theme;
      fontSize = settings.fontSize;
      fontFamily = settings.fontFamily;
      lineHeight = settings.lineHeight;
      tabSize = settings.tabSize;
      showLineNumbers = settings.showLineNumbers;
      lineWrapping = settings.lineWrapping;
      vimModeEnabled = settings.vimModeEnabled;
      
      // Apply changes to existing editor
      if (editor) {
        if (themeChanged) updateTheme(theme);
        if (fontChanged) updateEditorFont();
        if (tabSizeChanged) {
          editor.setOption('tabSize', tabSize);
          editor.setOption('indentUnit', tabSize);
        }
        if (lineNumbersChanged) editor.setOption('lineNumbers', showLineNumbers);
        if (lineWrappingChanged) editor.setOption('lineWrapping', lineWrapping);
        if (vimModeChanged) applyVimMode(vimModeEnabled);
      }
    });

    // Create component instance
    component = new PaneComponent({
      id: componentId,
      type: 'CodeEditor',
      title: title,
      initialData: {
        content,
        lastModified: new Date().toISOString()
      }
    });

    // Subscribe to component state changes (for content only)
    unsubscribe = component.getGlobalState().subscribe((data) => {
      if (data.content !== undefined && data.content !== content) {
        content = data.content;
        if (editor && editor.getValue() !== content) {
          editor.setValue(content);
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
    if (settingsUnsubscribe) {
      settingsUnsubscribe();
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
  <!-- Editor Container (no header) -->
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