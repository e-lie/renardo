<script lang="ts">
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

  let textareaElement: HTMLTextAreaElement;
  let localContent = $state(content);

  // Sync local content with prop
  $effect(() => {
    if (content !== localContent) {
      localContent = content;
    }
  });

  function handleInput(e: Event) {
    const target = e.target as HTMLTextAreaElement;
    localContent = target.value;
    onchange?.(localContent);
  }

  function handleKeyDown(e: KeyboardEvent) {
    // Ctrl+Enter or Cmd+Enter to execute
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      onexecute?.(localContent);
    }

    // Tab key inserts spaces
    if (e.key === 'Tab') {
      e.preventDefault();
      const start = textareaElement.selectionStart;
      const end = textareaElement.selectionEnd;
      const spaces = '    '; // 4 spaces

      localContent = localContent.substring(0, start) + spaces + localContent.substring(end);
      onchange?.(localContent);

      // Set cursor position after the inserted spaces
      setTimeout(() => {
        textareaElement.selectionStart = textareaElement.selectionEnd = start + spaces.length;
      }, 0);
    }
  }

  // Expose focus method
  export function focus() {
    textareaElement?.focus();
  }
</script>

<textarea
  bind:this={textareaElement}
  bind:value={localContent}
  {readonly}
  {placeholder}
  data-testid={testid}
  class="w-full h-full p-4 bg-base-200 text-base-content font-mono text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary"
  oninput={handleInput}
  onkeydown={handleKeyDown}
  spellcheck="false"
></textarea>

<style>
  textarea {
    tab-size: 4;
    line-height: 1.5;
  }
</style>
