<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { EditorView, keymap, placeholder as cmPlaceholder, lineNumbers, Decoration, type DecorationSet } from '@codemirror/view';
  import { EditorState, Compartment, StateEffect, StateField, Transaction } from '@codemirror/state';
  import { defaultKeymap, indentWithTab, standardKeymap, insertTab, history } from '@codemirror/commands';
  import { python } from '@codemirror/lang-python';
  import { javascript } from '@codemirror/lang-javascript';
  import { highlightSelectionMatches } from '@codemirror/search';
  import { vim } from '@replit/codemirror-vim';
  import { logger } from '../../../services/logger.service';
  import { getTheme } from '../../../lib/themes/codemirror-themes';

  let {
    content = '',
    language = 'python' as 'python' | 'hydra',
    readonly = false,
    placeholder = 'Enter your code here...',
    theme = 'dracula',
    showLineNumbers = true,
    vimMode = false,
    fontFamily = 'Fira Code',
    fontSize = 14,
    lineHeight = 1.5,
    testid = 'not-set',
    onchange,
    onexecute,
  }: {
    content?: string;
    language?: 'python' | 'hydra';
    readonly?: boolean;
    placeholder?: string;
    theme?: string;
    showLineNumbers?: boolean;
    vimMode?: boolean;
    fontFamily?: string;
    fontSize?: number;
    lineHeight?: number;
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
  const vimCompartment = new Compartment();
  const baseStyleCompartment = new Compartment();
  const historyCompartment = new Compartment();

  // Decoration-based execution highlight (does not touch cursor/selection)
  const addHighlightEffect = StateEffect.define<{ from: number; to: number }>();
  const clearHighlightEffect = StateEffect.define<null>();
  const executionHighlightField = StateField.define<DecorationSet>({
    create: () => Decoration.none,
    update(deco, tr) {
      deco = deco.map(tr.changes);
      for (const e of tr.effects) {
        if (e.is(addHighlightEffect)) {
          deco = deco.update({ add: [Decoration.mark({ class: 'cm-exec-highlight' }).range(e.value.from, e.value.to)] });
        } else if (e.is(clearHighlightEffect)) {
          deco = Decoration.none;
        }
      }
      return deco;
    },
    provide: f => EditorView.decorations.from(f),
  });

  // Execution queue — decouples visual blink from runtime calls
  const executionQueue: string[] = [];
  let queueRunning = false;

  function enqueueExecution(code: string) {
    executionQueue.push(code);
    if (!queueRunning) drainQueue();
  }

  function drainQueue() {
    if (executionQueue.length === 0) {
      queueRunning = false;
      return;
    }
    queueRunning = true;
    const code = executionQueue.shift()!;
    onexecute?.(code);
    setTimeout(drainQueue, 0);
  }

  // Sync local content with prop — reset history so buffer loads don't pollute undo stack
  $effect(() => {
    if (content !== localContent && editorView) {
      const currentDoc = editorView.state.doc.toString();
      if (currentDoc !== content) {
        // 1. Reset history (fresh instance, clears undo stack)
        editorView.dispatch({ effects: historyCompartment.reconfigure(history()) });
        // 2. Load content without recording it in the new history
        editorView.dispatch({
          changes: { from: 0, to: editorView.state.doc.length, insert: content },
          annotations: Transaction.addToHistory.of(false),
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

  // Update vim mode when prop changes
  $effect(() => {
    const currentVimMode = vimMode;

    if (editorView) {
      logger.info('ElCodeMirrorEditor', 'Vim mode prop changed, updating editor', { vimMode: currentVimMode });

      editorView.dispatch({
        effects: vimCompartment.reconfigure(currentVimMode ? vim() : [])
      });
    }
  });

  // Update font family, font size, line height when props change
  $effect(() => {
    const currentFontFamily = fontFamily;
    const currentFontSize = fontSize;
    const currentLineHeight = lineHeight;

    if (editorView) {
      logger.info('ElCodeMirrorEditor', 'Font props changed, updating editor', { fontFamily: currentFontFamily, fontSize: currentFontSize, lineHeight: currentLineHeight });

      const jgsFonts = ['JGS', 'JGS5', 'JGS7', 'JGS9'];
      if (jgsFonts.includes(currentFontFamily)) {
        const fontMap: Record<string, string> = {
          'JGS': `${currentFontSize}px JGS`,
          'JGS5': `${currentFontSize}px JGS5`,
          'JGS7': `${currentFontSize}px JGS7`,
          'JGS9': `${currentFontSize}px JGS9`
        };
        document.fonts.load(fontMap[currentFontFamily]).then(() => {
          applyFontStyle(currentFontFamily, currentFontSize, currentLineHeight);
        }).catch(() => {
          applyFontStyle(currentFontFamily, currentFontSize, currentLineHeight);
        });
      } else {
        applyFontStyle(currentFontFamily, currentFontSize, currentLineHeight);
      }
    }
  });

  function applyFontStyle(currentFontFamily: string, currentFontSize: number, currentLineHeight: number) {
    if (!editorView) return;

    editorView.dispatch({
      effects: baseStyleCompartment.reconfigure(
        EditorView.theme({
          '&': {
            height: '100%',
            fontSize: `${currentFontSize}px`,
            fontFamily: `${currentFontFamily}, "Consolas", monospace`,
            position: 'relative',
          },
          '.cm-scroller': {
            overflow: 'auto',
            fontFamily: `${currentFontFamily}, "Consolas", monospace`,
            position: 'absolute',
            top: '0',
            left: '0',
            right: '0',
            bottom: '0',
          },
          '.cm-content': {
            padding: '16px',
            lineHeight: String(currentLineHeight),
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
        })
      )
    });
  }

  // Language support with enhanced syntax highlighting
  function getLanguageSupport(lang: string) {
    logger.debug('ElCodeMirrorEditor', 'Loading language support', { language: lang });

    switch (lang) {
      case 'python':
        return python();
      case 'hydra':
        return javascript();
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

  // Decoration-based highlight — cursor/selection never touched
  function createExecutionHighlight(view: EditorView, from: number, to: number) {
    view.dispatch({ effects: addHighlightEffect.of({ from, to }) });
    setTimeout(() => {
      if (editorView) editorView.dispatch({ effects: clearHighlightEffect.of(null) });
    }, 200);
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
        enqueueExecution(block.text);
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
        enqueueExecution(lineText);
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
        enqueueExecution(allCode);
      }
      return;
    }

    // Prevent Cmd+Up / Cmd+Down from jumping to start/end of document
    if (event.metaKey && (event.key === 'ArrowUp' || event.key === 'ArrowDown')) {
      event.preventDefault();
      event.stopPropagation();
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
        // Base editor styling (with compartment for dynamic font updates)
        baseStyleCompartment.of(
          EditorView.theme({
            '&': {
              height: '100%',
              fontSize: `${fontSize}px`,
              fontFamily: `${fontFamily}, "Consolas", monospace`,
              position: 'relative',
            },
            '.cm-scroller': {
              overflow: 'auto',
              fontFamily: `${fontFamily}, "Consolas", monospace`,
              position: 'absolute',
              top: '0',
              left: '0',
              right: '0',
              bottom: '0',
            },
            '.cm-content': {
              padding: '16px',
              lineHeight: String(lineHeight),
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
          })
        ),

        // Theme (with compartment for dynamic updates)
        themeCompartment.of(getTheme(theme)),

        // Line numbers (with compartment for dynamic updates)
        lineNumbersCompartment.of(showLineNumbers ? lineNumbers() : []),

        // Vim mode (with compartment for dynamic updates)
        vimCompartment.of(vimMode ? vim() : []),

        // Language support
        getLanguageSupport(language),

        // Enhanced syntax highlighting
        highlightSelectionMatches(),

        // Undo/redo history (in compartment so it can be reset on buffer load)
        historyCompartment.of(history()),

        // Execution highlight decoration field
        executionHighlightField,

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

  :global(.cm-exec-highlight) {
    background-color: rgba(34, 197, 94, 0.2);
    border-radius: 2px;
    animation: execPulse 0.2s ease-out forwards;
  }

  @keyframes execPulse {
    from { background-color: rgba(34, 197, 94, 0.7); }
    to   { background-color: rgba(34, 197, 94, 0.2); }
  }
</style>