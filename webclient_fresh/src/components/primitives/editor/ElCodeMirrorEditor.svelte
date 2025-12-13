<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { EditorView, keymap, placeholder as cmPlaceholder } from '@codemirror/view';
  import { EditorState } from '@codemirror/state';
  import { defaultKeymap, indentWithTab, standardKeymap, insertTab } from '@codemirror/commands';
  import { python } from '@codemirror/lang-python';
  import { javascript } from '@codemirror/lang-javascript';
  import { oneDark } from '@codemirror/theme-one-dark';
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
    language?: 'python' | 'javascript' | 'text' | 'sclang';
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

  // Language support
  function getLanguageSupport(lang: string) {
    switch (lang) {
      case 'python':
        return python();
      case 'javascript':
        return javascript();
      default:
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
        // Basic setup
        EditorView.theme({
          '&': {
            height: '100%',
            fontSize: '14px',
            fontFamily: 'Fira Code, monospace',
          },
          '.cm-scroller': {
            overflow: 'auto',
            fontFamily: 'Fira Code, monospace',
          },
          '.cm-content': {
            padding: '16px',
            minHeight: '100%',
          },
          '.cm-focused': {
            outline: 'none',
          },
          '.cm-editor': {
            height: '100%',
          },
        }),

        // Language support
        getLanguageSupport(language),

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
