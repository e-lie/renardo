<script lang="ts">
  import type { BufferInterface } from '../../models/editor';
  import { ElCodeEditor } from '../primitives';
  import { logger } from '../../services/logger.service';
  import { useEditorStore } from '../../store/editor/Editor.store';

  let {
    buffer,
    onchange,
    onexecute,
    oncreatetab,
  }: {
    buffer: BufferInterface | null;
    onchange?: (content: string) => void;
    onexecute?: (code: string) => void;
    oncreatetab?: (language: 'python' | 'hydra') => void;
  } = $props();

  const { getters } = useEditorStore();
  const { settings } = getters;

  let showLangMenu = $state(false);

  function handleChange(content: string) {
    logger.debug('CodeEditor', 'Content changed', { contentLength: content.length });
    if (buffer) {
      onchange?.(content);
    }
  }

  function handleExecute(code: string) {
    logger.debug('CodeEditor', 'Execute called', { codeLength: code.length });
    onexecute?.(code);
  }

  function handleCreateTab(language: 'python' | 'hydra') {
    showLangMenu = false;
    oncreatetab?.(language);
  }
</script>

<div class="h-full w-full overflow-hidden relative">
  {#if buffer}
    <ElCodeEditor
      content={buffer.content}
      language={buffer.language}
      readonly={false}
      placeholder=""
      theme={$settings.theme}
      showLineNumbers={$settings.showLineNumbers}
      vimMode={$settings.vimMode}
      fontFamily={$settings.fontFamily}
      fontSize={$settings.fontSize}
      lineHeight={$settings.lineHeight}
      testid="code-editor"
      onchange={handleChange}
      onexecute={handleExecute}
    />
    {#if oncreatetab}
      <div class="absolute top-2 right-2 z-10">
        <button
          class="btn btn-sm btn-circle variant-filled-primary shadow-lg"
          onclick={() => (showLangMenu = !showLangMenu)}
          title="Create new tab"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
        </button>
        {#if showLangMenu}
          <div class="absolute right-0 top-full mt-1 card bg-surface-100 dark:bg-surface-800 shadow-lg p-1 min-w-[120px]">
            <button
              class="w-full text-left px-3 py-1.5 text-sm hover:bg-surface-200 dark:hover:bg-surface-700 rounded"
              onclick={() => handleCreateTab('python')}
            >Python</button>
            <button
              class="w-full text-left px-3 py-1.5 text-sm hover:bg-surface-200 dark:hover:bg-surface-700 rounded"
              onclick={() => handleCreateTab('hydra')}
            >Hydra</button>
          </div>
        {/if}
      </div>
    {/if}
  {:else}
    <div class="flex items-center justify-center h-full text-base-content/50">
      <p>No buffer selected</p>
    </div>
  {/if}
</div>
