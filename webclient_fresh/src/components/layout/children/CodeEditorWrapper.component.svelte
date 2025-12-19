<script lang="ts">
  import CodeEditor from '../../editor/CodeEditor.component.svelte'
  import { useEditorStore } from '../../../store/editor'

  let {
    componentId,
    title = 'Code Editor'
  }: {
    componentId: string
    title?: string
  } = $props()

  const { actions, getters } = useEditorStore()
  const { activeBuffer, settings } = getters

  // Create a dedicated buffer for this code editor instance if needed
  // For now, we'll use the active buffer from the editor store
</script>

<div class="h-full">
  <CodeEditor />
</div>
