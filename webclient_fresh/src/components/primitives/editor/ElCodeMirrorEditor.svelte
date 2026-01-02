<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { EditorView, keymap, placeholder as cmPlaceholder, lineNumbers } from '@codemirror/view';
  import { EditorState, Compartment } from '@codemirror/state';
  import { defaultKeymap, indentWithTab, standardKeymap, insertTab } from '@codemirror/commands';
  import { python } from '@codemirror/lang-python';
  import { highlightSelectionMatches } from '@codemirror/search';
  import { logger } from '../../../services/logger.service';
  import { getTheme } from '../../../lib/themes/codemirror-themes';

  let {
    content = '',
    language = 'python',
    readonly = false,
    placeholder = 'Enter your code here...',
    theme = 'dracula',
    showLineNumbers = true,
    testid = 'not-set',
    onchange,
    onexecute,
  }: {
    content?: string;
    language?: 'python';
    readonly?: boolean;
    placeholder?: string;
    theme?: string;
    showLineNumbers?: boolean;
    testid?: string;
    onchange?: (value: string) => void;
    onexecute?: (code: string) => void;
  } = $props();

  let containerElement: HTMLDivElement;
  let editorView: EditorView | null = null;
  let localContent = $state(content);

  // Theme compartment for dynamic reconfiguration
  const themeCompartment = new Compartment();
  const lineNumbersCompartment = new Compartment();

  // Sync local content with prop
  $effect(() => {
    if (content !== localContent && editorView) {
      const currentDoc = editorView.state.doc.toString();
      if (currentDoc !== content) {
        editorView.dispatch({
          changes: {
            from: 0,
            to: currentDoc.length,
            insert: content,
          },
        });
        localContent = content;
      }
    }
  });

  // Update theme when prop changes
  $effect(() => {
    // Access theme to track it
    const currentTheme = theme;

    if (editorView) {
      logger.info('ElCodeMirrorEditor', 'Theme prop changed, updating editor', { theme: currentTheme });

      editorView.dispatch({
        effects: themeCompartment.reconfigure(getTheme(currentTheme))
      });
    }
  });

  // Update line numbers when prop changes
  $effect(() => {
    const currentShowLineNumbers = showLineNumbers;

    if (editorView) {
      logger.info('ElCodeMirrorEditor', 'Line numbers prop changed, updating editor', { showLineNumbers: currentShowLineNumbers });

      editorView.dispatch({
        effects: lineNumbersCompartment.reconfigure(currentShowLineNumbers ? lineNumbers() : [])
      });
    }
  });

  // Language support with enhanced syntax highlighting
  function getLanguageSupport(lang: string) {
    logger.debug('ElCodeMirrorEditor', 'Loading language support', { language: lang });

    switch (lang) {
      case 'python':
        return python();
      default:
        return [];
    }
  }

  // Get current paragraph/block of code
  function getCurrentBlock(view: EditorView): { text: string; from: number; to: number } {
    const doc = view.state.doc;
    const cursor = view.state.selection.main.head;
    const lineInfo = doc.lineAt(cursor);
    
    // Find start of block (go up until empty line or start of document)
    let startLine = lineInfo.number - 1;
    while (startLine > 0) {
      const prevLine = doc.line(startLine);
      if (prevLine.text.trim() === '') {
        break;
      }
      startLine--;
    }
    
    // Find end of block (go down until empty line or end of document)
    let endLine = lineInfo.number;
    while (endLine < doc.lines) {
      const currentLine = doc.line(endLine + 1);
      if (currentLine.text.trim() === '') {
        break;
      }
      endLine++;
    }
    
    const startLineObj = doc.line(Math.max(0, startLine + 1));
    const endLineObj = doc.line(endLine);
    
    return {
      text: doc.sliceString(startLineObj.from, endLineObj.to),
      from: startLineObj.from,
      to: endLineObj.to
    };
  }

  // Simple execution highlight using CSS
  function createExecutionHighlight(view: EditorView, from: number, to: number) {
    // Create temporary selection for highlight
    view.dispatch({
      selection: { anchor: from, head: to }
    });
    
    // Add highlight style
    const highlightStyle = document.createElement('style');
    highlightStyle.id = 'execution-highlight';
    highlightStyle.textContent = `
      .cm-editor .cm-selectionLayer .cm-selectionBackground,
      .cm-editor .cm-selectionBackground {
        background-color: rgba(34, 197, 94, 0.3) !important;
        border-radius: 2px;
        animation: executionPulse 0.8s ease-in-out;
      }
      @keyframes executionPulse {
        0% { background-color: rgba(34, 197, 94, 0.8); }
        50% { background-color: rgba(34, 197, 94, 0.4); }
        100% { background-color: rgba(34, 197, 94, 0.2); }
      }
    `;
    document.head.appendChild(highlightStyle);
    
    // Clear highlight after animation
    setTimeout(() => {
      try {
        const style = document.getElementById('execution-highlight');
        if (style) {
          document.head.removeChild(style);
        }
        // Clear selection to return to normal
        view.dispatch({
          selection: { anchor: from, head: from }
        });
      } catch (e) {
        // Ignore cleanup errors
      }
    }, 800);
  }

  // Custom key handlers for Ctrl+Enter execution and Ctrl+. for stop
  function handleKeyDown(event: KeyboardEvent) {
    // Ctrl+Enter or Cmd+Enter for block execution
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
      event.preventDefault();
      event.stopPropagation();

      if (editorView) {
        // Get current block of code
        const block = getCurrentBlock(editorView);

        // Create execution highlight
        createExecutionHighlight(editorView, block.from, block.to);

        // Execute block
        logger.debug('ElCodeMirrorEditor', 'Executing code block', {
          codeLength: block.text.length,
          from: block.from,
          to: block.to
        });
        onexecute?.(block.text);
      }
      return;
    }

    // Alt+Enter for current line execution
    if (event.altKey && event.key === 'Enter') {
      event.preventDefault();
      event.stopPropagation();

      if (editorView) {
        const state = editorView.state;
        const cursorPos = state.selection.main.head;
        const line = state.doc.lineAt(cursorPos);
        const lineText = line.text;

        // Create execution highlight
        createExecutionHighlight(editorView, line.from, line.to);

        // Execute line
        logger.debug('ElCodeMirrorEditor', 'Executing current line', {
          lineText,
          from: line.from,
          to: line.to
        });
        onexecute?.(lineText);
      }
      return;
    }

    // Shift+Enter for executing all code in editor
    if (event.shiftKey && event.key === 'Enter') {
      event.preventDefault();
      event.stopPropagation();

      if (editorView) {
        const allCode = editorView.state.doc.toString();

        // Create execution highlight for whole document
        createExecutionHighlight(editorView, 0, editorView.state.doc.length);

        // Execute all code
        logger.debug('ElCodeMirrorEditor', 'Executing all code', {
          codeLength: allCode.length
        });
        onexecute?.(allCode);
      }
      return;
    }

    // Ctrl+. or Cmd+. for Clock.clear()
    if ((event.ctrlKey || event.metaKey) && event.key === '.') {
      event.preventDefault();
      event.stopPropagation();
      logger.info('ElCodeMirrorEditor', 'Executing Clock.clear() via Ctrl+.');
      onexecute?.('Clock.clear()');
      return;
    }
  }

  onMount(() => {
    logger.debug('ElCodeMirrorEditor', 'Component mounting...');
    if (!containerElement) {
      logger.error('ElCodeMirrorEditor', 'Container element not found');
      return;
    }

    logger.debug('ElCodeMirrorEditor', 'Creating CodeMirror instance', {
      contentLength: content.length,
      language,
    });

    // Create editor state
    const startState = EditorState.create({
      doc: content,
      extensions: [
        // Base editor styling
        EditorView.theme({
          '&': {
            height: '100%',
            fontSize: '14px',
            fontFamily: 'Fira Code, "JetBrains Mono", "Consolas", monospace',
            position: 'relative',
          },
          '.cm-scroller': {
            overflow: 'auto',
            fontFamily: 'Fira Code, "JetBrains Mono", "Consolas", monospace',
            position: 'absolute',
            top: '0',
            left: '0',
            right: '0',
            bottom: '0',
          },
          '.cm-content': {
            padding: '16px',
            lineHeight: '1.5',
          },
          '.cm-focused': {
            outline: 'none',
          },
          '.cm-editor': {
            height: '100%',
          },
          '.cm-line': {
            padding: '0 0',
          },
        }),

        // Theme (with compartment for dynamic updates)
        themeCompartment.of(getTheme(theme)),

        // Line numbers (with compartment for dynamic updates)
        lineNumbersCompartment.of(showLineNumbers ? lineNumbers() : []),

        // Language support
        getLanguageSupport(language),

        // Enhanced syntax highlighting
        highlightSelectionMatches(),

        // Keymaps (standard keymaps only, custom handled via DOM events)
        keymap.of([...defaultKeymap, ...standardKeymap, indentWithTab, insertTab]),

        // Event handlers
        EditorView.updateListener.of((update) => {
          if (update.docChanged) {
            const newContent = update.state.doc.toString();
            localContent = newContent;
            onchange?.(newContent);
          }
        }),

        // Read-only mode
        EditorState.readOnly.of(readonly),

        // Placeholder
        ...(placeholder ? [cmPlaceholder(placeholder)] : []),
      ],
    });

    // Create editor view
    editorView = new EditorView({
      state: startState,
      parent: containerElement,
    });

    // Add custom keyboard event listener with capture to intercept before CodeMirror
    containerElement.addEventListener('keydown', handleKeyDown, { capture: true });

    logger.info('ElCodeMirrorEditor', 'CodeMirror instance created successfully');
  });

  onDestroy(() => {
    logger.debug('ElCodeMirrorEditor', 'Component destroying...');
    if (editorView) {
      editorView.destroy();
      logger.debug('ElCodeMirrorEditor', 'CodeMirror instance destroyed');
    }
    if (containerElement) {
      containerElement.removeEventListener('keydown', handleKeyDown, { capture: true });
    }
  });

  // Expose focus method
  export function focus() {
    logger.debug('ElCodeMirrorEditor', 'Focus called');
    editorView?.focus();
  }

  // Expose get content method
  export function getContent(): string {
    const content = editorView?.state.doc.toString() || '';
    logger.debug('ElCodeMirrorEditor', 'getContent called', { contentLength: content.length });
    return content;
  }
</script>

<div
  bind:this={containerElement}
  data-testid={testid}
  class="w-full h-full overflow-hidden bg-base-200 text-base-content"
></div>

<style>
  :global(.cm-editor) {
    height: 100%;
    position: relative;
  }

  :global(.cm-scroller) {
    font-family: 'Fira Code', 'JetBrains Mono', 'Consolas', monospace;
    line-height: 1.5;
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
  }

  :global(.cm-content) {
    padding: 16px;
  }

  :global(.cm-focused) {
    outline: none;
  }
</style>