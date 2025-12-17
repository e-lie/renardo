<script lang="ts">
  import type { TabInterface } from '../../../models/editor';
  import { ElTab } from '../../primitives';

  let {
    tab,
    onswitch,
    onclose,
  }: {
    tab: TabInterface;
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
  closeable={true}
  testid={`tab-${tab.id}`}
  onclick={handleClick}
  onclose={handleClose}
>
  {tab.title}
</ElTab>
