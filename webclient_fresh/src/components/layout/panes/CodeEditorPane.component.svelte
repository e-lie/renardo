<script lang="ts">
  import CodeEditor from '../../editor/CodeEditor.component.svelte';
  import type { PaneComponent } from '../../../lib/layout/PaneComponent';
  import { useEditorStore } from '../../../store/editor';

  let {
    paneComponent,
    tabId,
  }: {
    paneComponent: PaneComponent;
    tabId: string;
  } = $props();

  const { actions, getters } = useEditorStore();
  const { activeBuffer } = getters;

  function handleChange(content: string) {
    if ($activeBuffer) {
      actions.updateBufferContent($activeBuffer.id, content);
    }
  }

  function handleExecute(code: string) {
    actions.executeCode(code);
  }
</script>

<CodeEditor
  buffer={$activeBuffer}
  onchange={handleChange}
  onexecute={handleExecute}
/>
