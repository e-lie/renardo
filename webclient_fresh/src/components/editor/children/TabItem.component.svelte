<script lang="ts">
  import type { TabInterface, BufferInterface } from '../../../models/editor';
  import { ElTab } from '../../primitives';
  import logger from '../../../services/logger.service';

  let {
    tab,
    buffer,
    onswitch,
    onclose,
  }: {
    tab: TabInterface;
    buffer?: BufferInterface;
    onswitch?: (tabId: string) => void;
    onclose?: (tabId: string) => void;
  } = $props();

  function handleClick() {
    onswitch?.(tab.id);
  }

  function handleClose() {
    logger.debug('TabItem', 'handleClose called for tab', { tabId: tab.id });
    onclose?.(tab.id);
    logger.debug('TabItem', 'onclose callback executed');
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
