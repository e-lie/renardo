<script lang="ts">
  import type { BufferInterface } from '../../models/editor';
  import { ElCodeEditor } from '../primitives';
  import { logger } from '../../services/logger.service';

  let {
    buffer,
    onchange,
    onexecute,
  }: {
    buffer: BufferInterface | null;
    onchange?: (content: string) => void;
    onexecute?: (code: string) => void;
  } = $props();

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
</script>

<div class="h-full w-full">
  {#if buffer}
    <ElCodeEditor
      content={buffer.content}
      language={buffer.language}
      readonly={false}
      placeholder="Write your Renardo code here... (Ctrl+Enter to execute)"
      testid="code-editor"
      onchange={handleChange}
      onexecute={handleExecute}
    />
  {:else}
    <div class="flex items-center justify-center h-full text-base-content/50">
      <p>No buffer selected</p>
    </div>
  {/if}
</div>
