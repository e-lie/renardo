<script lang="ts">
  import { useAppStore } from '../../../store/root/Root.store';

  const { editorStore } = useAppStore();
  const { actions, getters } = editorStore;

  function handlePlayAll() {
    const activeBuffer = getters.activeBuffer();
    if (activeBuffer) {
      actions.executeCode(activeBuffer.content);
    }
  }

  function handleStop() {
    actions.executeCode('Clock.clear()');
  }
</script>

<div class="h-full flex items-center justify-between px-4 bg-surface-200 dark:bg-surface-800">
  <div class="flex items-center gap-4">
    <div class="text-lg font-bold text-surface-900 dark:text-surface-50">Renardo ฅ^•ﻌ•^ฅ</div>

    <!-- Play/Stop buttons -->
    <div class="flex items-center gap-2">
      <button
        class="btn btn-sm variant-filled-primary flex items-center gap-1"
        onclick={handlePlayAll}
        title="Execute all code (Shift+Enter)"
      >
        <span>▶</span>
        <span class="text-xs">Play</span>
      </button>
      <button
        class="btn btn-sm variant-filled-error flex items-center gap-1"
        onclick={handleStop}
        title="Stop (Ctrl+.)"
      >
        <span>■</span>
        <span class="text-xs">Stop</span>
      </button>
    </div>

    <!-- Keyboard shortcuts hints -->
    <div
      class="flex items-center gap-3 text-xs text-surface-600 dark:text-surface-400 border-l border-surface-400 dark:border-surface-600 pl-4"
    >
      <div class="flex items-center gap-1">
        <span>Ctrl+Enter</span>
        <span>- Run block |</span>
      </div>
      <div class="flex items-center gap-1">
        <span>Alt+Enter</span>
        <span>- Run line |</span>
      </div>
      <div class="flex items-center gap-1">
        <span>Shift+Enter</span>
        <span>- Run all |</span>
      </div>
      <div class="flex items-center gap-1">
        <span>Ctrl+.</span>
        <span>- Stop</span>
      </div>
    </div>
  </div>
</div>
