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
  const { buffers } = getters

  let bufferId = $state<string | null>(null)
  let buffer = $derived($buffers.find(b => b.id === bufferId) || null)

  // Create a dedicated buffer for this code editor instance
  $effect(() => {
    if (!bufferId) {
      const newBufferId = actions.createBuffer({
        name: title || 'Code Editor',
        content: '',
        language: 'python',
      })
      bufferId = newBufferId
      actions.setActiveBuffer(newBufferId)
    }
  })

  function handleChange(value: string) {
    if (bufferId) {
      actions.updateBuffer(bufferId, { content: value })
    }
  }

  function handleExecute(code: string) {
    actions.executeCode(code)
  }
</script>

<div class="h-full">
  {#if buffer}
    <CodeEditor {buffer} onchange={handleChange} onexecute={handleExecute} />
  {:else}
    <div class="h-full flex items-center justify-center text-surface-500">
      <p>Loading editor...</p>
    </div>
  {/if}
</div>
