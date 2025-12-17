<script lang="ts">
  import type { PaneComponent } from '../../../lib/layout/PaneComponent';

  let {
    paneComponent,
    tabId,
  }: {
    paneComponent: PaneComponent;
    tabId: string;
  } = $props();

  let content = $state('');

  $effect(() => {
    const unsub = paneComponent.subscribe(state => {
      content = state.data.content || '';
    });
    return unsub;
  });

  function handleInput(e: Event) {
    const value = (e.target as HTMLTextAreaElement).value;
    content = value;
    paneComponent.updateData({ content: value });
  }
</script>

<div class="h-full flex flex-col p-2 bg-base-100">
  <textarea
    class="textarea textarea-bordered flex-1 font-mono"
    value={content}
    oninput={handleInput}
    placeholder="Notes..."
  ></textarea>
</div>
