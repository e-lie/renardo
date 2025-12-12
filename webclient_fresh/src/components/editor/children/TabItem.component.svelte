<script lang="ts">
  import type { TabInterface } from '../../../models/editor';
  import { ElTab } from '../../primitives';

  let {
    tab,
    isStartupFile = false,
    onswitch,
    onclose,
  }: {
    tab: TabInterface;
    isStartupFile?: boolean;
    onswitch?: (tabId: string) => void;
    onclose?: (tabId: string) => void;
  } = $props();

  function handleClick() {
    onswitch?.(tab.id);
  }

  function handleClose() {
    onclose?.(tab.id);
  }
</script>

<ElTab
  isActive={tab.isActive}
  isPinned={tab.isPinned}
  {isStartupFile}
  closeable={!isStartupFile}
  testid={`tab-${tab.id}`}
  onclick={handleClick}
  onclose={handleClose}
>
  {tab.title}
</ElTab>
