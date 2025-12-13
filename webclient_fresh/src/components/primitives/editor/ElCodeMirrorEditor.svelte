<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { EditorView, keymap, placeholder as cmPlaceholder } from '@codemirror/view';
  import { EditorState } from '@codemirror/state';
  import { defaultKeymap, indentWithTab, standardKeymap, insertTab } from '@codemirror/commands';
  import { python } from '@codemirror/lang-python';
  import { highlightSelectionMatches } from '@codemirror/search';
  import { logger } from '../../../services/logger.service';

  let {
    content = '',
    language = 'python',
    readonly = false,
    placeholder = 'Enter your code here...',
    testid = 'not-set',
    onchange,
    onexecute,
  }: {
    content?: string;
    language?: 'python';
    readonly?: boolean;
    placeholder?: string;
    testid?: string;
    onchange?: (value: string) => void;
    onexecute?: (code: string) => void;
  } = $props();

  let containerElement: HTMLDivElement;
  let editorView: EditorView | null = null;
  let localContent = $state(content);

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

  // Language support with enhanced syntax highlighting
  function getLanguageSupport(lang: string) {
    logger.debug('ElCodeMirrorEditor', 'Loading language support', { language: lang });

    switch (lang) {
      case 'python':
        return python({
          // Python-specific configuration
          indentUnit: 4,
          tabSize: 4,
          languageData: {
            commentTokens: { line: '#' },
            indentOnInput:
              /^\s*(((def|class|if|elif|else|for|while|try|except|finally|with|async)\b.*:|elif\s+.*:|else\s*:|except\s+.*:|finally\s*:|with\s+.*:|async\s+.*:))$/,
          },
        });
      default:
        // Plain text mode
        return [];
    }
  }

  // Custom keymap for Ctrl+Enter execution
  const executeKeymap = keymap.of([
    {
      key: 'Ctrl-Enter',
      mac: 'Cmd-Enter',
      run: (view) => {
        const code = view.state.doc.toString();
        onexecute?.(code);
        return true;
      },
    },
  ]);

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
        // Basic setup with enhanced syntax highlighting
        EditorView.theme({
          '&': {
            height: '100%',
            fontSize: '14px',
            fontFamily: 'Fira Code, "JetBrains Mono", "Consolas", monospace',
          },
          '.cm-scroller': {
            overflow: 'auto',
            fontFamily: 'Fira Code, "JetBrains Mono", "Consolas", monospace',
          },
          '.cm-content': {
            padding: '16px',
            minHeight: '100%',
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
          '.cm-selectionBackground, ::selection': {
            backgroundColor: 'rgba(var(--p), 0.2)',
          },
          '.cm-gutters': {
            backgroundColor: 'transparent',
            border: 'none',
          },
          '.cm-activeLineGutter': {
            backgroundColor: 'transparent',
          },
          '.cm-lineNumbers .cm-gutterElement': {
            color: 'rgba(var(--bc), 0.5)',
            padding: '0 8px 0 16px',
            minWidth: '40px',
            textAlign: 'right',
            fontSize: '12px',
          },
          // Python syntax highlighting
          '.cm-keyword': { color: '#ff79c6', fontWeight: 'bold' },
          '.cm-def': { color: '#8be9fd' },
          '.cm-variable': { color: '#f8f8f2' },
          '.cm-variable-2': { color: '#50fa7b' },
          '.cm-variable-3': { color: '#ffb86c' },
          '.cm-type': { color: '#8be9fd' },
          '.cm-property': { color: '#66d9ef' },
          '.cm-string': { color: '#f1fa8c' },
          '.cm-string-2': { color: '#f1fa8c' },
          '.cm-comment': { color: '#6272a4', fontStyle: 'italic' },
          '.cm-number': { color: '#bd93f9' },
          '.cm-atom': { color: '#bd93f9' },
          '.cm-builtin': { color: '#ff79c6' },
          '.cm-operator': { color: '#ff79c6' },
          '.cm-punctuation': { color: '#f8f8f2' },
          '.cm-bracket': { color: '#f8f8f2' },
          '.cm-tag': { color: '#ff79c6' },
          '.cm-attribute': { color: '#50fa7b' },
          '.cm-hr': { color: '#6272a4' },
          '.cm-link': { color: '#8be9fd', textDecoration: 'underline' },
          '.cm-error': { color: '#ff5555', borderBottom: '1px solid #ff5555' },
          '.cm-positive': { color: '#50fa7b' },
          '.cm-negative': { color: '#ff5555' },
          '.cm-meta': { color: '#f8f8f2' },
          '.cmqualifier': { color: '#50fa7b' },
        }),

        // Language support
        getLanguageSupport(language),

        // Enhanced syntax highlighting
        highlightSelectionMatches(),

        // Keymaps
        keymap.of([...defaultKeymap, ...standardKeymap, indentWithTab, insertTab]),
        executeKeymap,

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
        placeholder ? cmPlaceholder(placeholder) : [],

        // Optional: Dark theme
        // oneDark
      ],
    });

    // Create editor view
    editorView = new EditorView({
      state: startState,
      parent: containerElement,
    });

    logger.info('ElCodeMirrorEditor', 'CodeMirror instance created successfully');
  });

  onDestroy(() => {
    logger.debug('ElCodeMirrorEditor', 'Component destroying...');
    if (editorView) {
      editorView.destroy();
      logger.debug('ElCodeMirrorEditor', 'CodeMirror instance destroyed');
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
  class="w-full h-full bg-base-200 text-base-content"
></div>

<style>
  :global(.cm-editor) {
    height: 100%;
  }

  :global(.cm-scroller) {
    font-family: 'Fira Code', 'JetBrains Mono', 'Consolas', monospace;
    line-height: 1.5;
  }

  :global(.cm-content) {
    padding: 16px;
    min-height: 100%;
  }

  :global(.cm-focused) {
    outline: none;
  }

  :global(.cm-gutter) {
    background-color: transparent;
    border-right: none;
  }

  :global(.cm-lineNumbers .cm-gutterElement) {
    color: rgba(var(--bc), 0.5);
  }

  :global(.cm-activeLineGutter) {
    background-color: transparent;
  }

  :global(.cm-selectionBackground) {
    background-color: rgba(var(--p), 0.2);
  }
</style>
